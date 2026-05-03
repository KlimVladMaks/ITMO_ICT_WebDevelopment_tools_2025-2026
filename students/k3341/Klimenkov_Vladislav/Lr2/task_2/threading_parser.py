import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, delete
from common import get_language_urls, extract_skill_from_soup, save_skills_bulk, HEADERS
from database import init_db, engine
from models import Skill


def fetch_and_extract(url, results_list, lock):
    """Отдельная задача для потока: загружает страницу, извлекает данные, добавляет в общий список."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        name, desc = extract_skill_from_soup(soup)
        if name:
            with lock:
                results_list.append((name, desc))
            print(f"Поток обработал: {name}")
        else:
            print(f"Не удалось извлечь имя из {url}")
    except Exception as e:
        print(f"Ошибка в потоке для {url}: {e}")


def run_threading(urls, max_workers=8):
    start = time.perf_counter()
    results = []
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_and_extract, url, results, lock) for url in urls]
        for future in as_completed(futures):
            future.result()
        
        save_skills_bulk(results)
        end = time.perf_counter()
        print(f"Threading подход (workers={max_workers}) занял {end - start:.2f} секунд")
        return end - start


if __name__ == "__main__":
    init_db()

    # Предварительно очищаем БД для честной оценки
    with Session(engine) as session:
        session.exec(delete(Skill))
        session.commit()

    urls = get_language_urls(limit=100)
    print(f"Получено {len(urls)} ссылок")
    run_threading(urls)
