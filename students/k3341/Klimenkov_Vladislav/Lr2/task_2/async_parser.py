import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from common import get_language_urls, extract_skill_from_soup, save_skills_bulk, HEADERS
from database import init_db, engine
from sqlmodel import Session, delete
from models import Skill


async def fetch_and_extract(session, url, results):
    """Асинхронно загружает страницу, извлекает данные, добавляет в results."""
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                name, desc = extract_skill_from_soup(soup)
                if name:
                    results.append((name, desc))
                    print(f"Обработан: {name}")
                else:
                    print(f"Не удалось извлечь имя из {url}")
            else:
                print(f"HTTP {resp.status} для {url}")
    except Exception as e:
        print(f"Ошибка при {url}: {e}")


async def run_async(urls, max_concurrent=8):
    start = time.perf_counter()
    results = []
    connector = aiohttp.TCPConnector(limit=max_concurrent)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_and_extract(session, url, results) for url in urls]
        await asyncio.gather(*tasks)
    
    save_skills_bulk(results)
    end = time.perf_counter()
    print(f"Async подход (concurrent={max_concurrent}) занял {end - start:.2f} секунд")
    return end - start


if __name__ == "__main__":
    init_db()

    # Предварительно очищаем БД для честной оценки
    with Session(engine) as session:
        session.exec(delete(Skill))
        session.commit()

    urls = get_language_urls(limit=100)
    print(f"Получено {len(urls)} ссылок")
    asyncio.run(run_async(urls))
