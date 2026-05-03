import time
import multiprocessing
from functools import partial
import requests
from bs4 import BeautifulSoup
from common import get_language_urls, extract_skill_from_soup, save_skills_bulk, HEADERS
from database import init_db, engine
from sqlmodel import Session, delete
from models import Skill


def fetch_and_extract(url, shared_list):
    """Отдельный процесс. Добавляет результат в общий Manager.list."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        name, desc = extract_skill_from_soup(soup)
        if name:
            shared_list.append((name, desc))
            print(f"Процесс обработал: {name}")
        else:
            print(f"Не удалось извлечь имя из {url}")
    except Exception as e:
        print(f"Ошибка в процессе для {url}: {e}")


def run_multiprocessing(urls, processes=8):
    start = time.perf_counter()
    manager = multiprocessing.Manager()
    shared_results = manager.list()

    worker = partial(fetch_and_extract, shared_list=shared_results)
    with multiprocessing.Pool(processes=processes) as pool:
        pool.map(worker, urls)

    results = list(shared_results)
    save_skills_bulk(results)
    end = time.perf_counter()
    print(f"Multiprocessing подход (processes={processes}) занял {end - start:.2f} секунд")
    return end - start


if __name__ == "__main__":
    init_db()

    # Предварительно очищаем БД для честной оценки
    with Session(engine) as session:
        session.exec(delete(Skill))
        session.commit()

    urls = get_language_urls(limit=100)
    print(f"Получено {len(urls)} ссылок")
    run_multiprocessing(urls)
