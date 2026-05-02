"""
python3 sync_parser.py
"""

import time
import requests
from sqlmodel import Session, delete
from bs4 import BeautifulSoup
from common import (
    get_language_urls, 
    extract_skill_from_soup, 
    save_skills_bulk, 
    HEADERS
)
from database import init_db, engine
from models import Skill


def parse_all_sync(urls):
    """Последовательно парсит URL, возвращает список (name, description)."""
    results = []
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            name, desc = extract_skill_from_soup(soup)
            if name:
                results.append((name, desc))
                print(f"Обработан: {name}")
            else:
                print(f"Не удалось извлечь имя из {url}")
        except Exception as e:
            print(f"Ошибка при {url}: {e}")
    return results


def run_sync(urls):
    start = time.perf_counter()
    skills_data = parse_all_sync(urls)
    save_skills_bulk(skills_data)
    end = time.perf_counter()
    print(f"Синхронный подход занял {end - start:.2f} секунд")
    return end - start


if __name__ == "__main__":
    init_db()

    # Предварительно очищаем БД для честной оценки
    with Session(engine) as session:
        session.exec(delete(Skill))
        session.commit()

    urls = get_language_urls(limit=10)
    print(f"Получено {len(urls)} ссылок")
    run_sync(urls)
