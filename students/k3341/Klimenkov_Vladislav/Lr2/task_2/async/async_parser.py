import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete
from common import get_language_urls, extract_skill_from_soup, HEADERS
from database import engine, init_db
from models import Skill


async def save_skill(session: AsyncSession, name: str, description: str):
    """Асинхронно сохраняет один навык, игнорируя дубликаты."""
    skill = Skill(name=name, description=description)
    session.add(skill)
    try:
        await session.commit()
        print(f"✅ Сохранён: {name}")
    except IntegrityError:
        await session.rollback()
        print(f"⚠️ Уже существует (конфликт): {name}")


async def fetch_and_extract(session: aiohttp.ClientSession, url: str):
    """Загружает страницу, извлекает данные и сразу сохраняет в БД."""
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                name, desc = extract_skill_from_soup(soup)
                if name:
                    async with AsyncSession(engine) as db_session:
                        await save_skill(db_session, name, desc)
                else:
                    print(f"❌ Не удалось извлечь имя из {url}")
            else:
                print(f"❌ HTTP {resp.status} для {url}")
    except Exception as e:
        print(f"❌ Ошибка при {url}: {e}")


async def run_async(urls, max_concurrent=8):
    start = time.perf_counter()
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_and_extract(session, url) for url in urls]
        await asyncio.gather(*tasks)
    end = time.perf_counter()
    print(f"\n⏱ Асинхронный подход (concurrent={max_concurrent}) занял {end - start:.2f} секунд")


async def clear_db():
    """Асинхронная очистка таблицы перед запуском (для честного теста)."""
    async with AsyncSession(engine) as session:
        await session.execute(delete(Skill))
        await session.commit()
        print("🗑 База данных очищена")


async def main():
    await init_db()
    await clear_db()
    urls = get_language_urls(limit=100)
    print(f"🔗 Получено {len(urls)} ссылок")
    await run_async(urls)


if __name__ == "__main__":
    asyncio.run(main())
