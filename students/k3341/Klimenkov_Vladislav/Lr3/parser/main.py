from bs4 import BeautifulSoup
import aiohttp
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
import time
from sqlmodel import Session, select, delete

from common import get_language_urls, save_skills_bulk, HEADERS
from models import Skill
from database import init_db, engine


async def fetch_and_extract(session, url, results):
    """Асинхронно загружает страницу, извлекает данные, добавляет в results."""
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                title_tag = soup.find('title')
                if not title_tag:
                    return
                title_text = title_tag.string
                if ' - Wikipedia' in title_text:
                    name = title_text.replace(' - Wikipedia', '').strip()
                else:
                    name = title_text.strip()
                desc_div = soup.find('div', class_='shortdescription')
                description = desc_div.get_text(strip=True) if desc_div else None
                if name:
                    results.append((name, description))
                    print(f"Обработан: {name}")
                else:
                    print(f"Не удалось извлечь имя из {url}")
            else:
                print(f"HTTP {resp.status} для {url}")
    except Exception as e:
        print(f"Ошибка при {url}: {e}")


async def parse_urls(urls, max_concurrent=8):
    """Асинхронно парсит список URL и возвращает список кортежей (name, description)."""
    results = []
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_and_extract(session, url, results) for url in urls]
        await asyncio.gather(*tasks)
    return results


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan для инициализации БД"""
    init_db()
    yield


app = FastAPI(title="Парсер языков программирования", lifespan=lifespan)


@app.post("/parse")
async def parse_languages(limit: int = Query(10, ge=1, le=200, description="Количество языков для парсинга")):
    """
    Запускает парсинг страниц языков программирования.
    :param limit: сколько языков обработать
    :return: статистика выполнения
    """
    start_time = time.perf_counter()

    try:
        urls = get_language_urls(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка url: {e}")
    
    if not urls:
        raise HTTPException(status_code=404, detail="Не найдено ни одной ссылки")
    
    try:
        results = await parse_urls(urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка во время парсинга: {e}")
    
    try:
        save_skills_bulk(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения в БД: {e}")
    
    elapsed = time.perf_counter() - start_time

    return {
        "status": "success",
        "parsed_count": len(results),
        "time_seconds": round(elapsed, 2),
        "limit_requested": limit
    }


@app.get("/skills_count")
async def skills_count():
    """Возвращает количество записей в таблице Skill."""
    with Session(engine) as session:
        count = session.exec(select(Skill)).all()
        return {"count": len(count)}


@app.delete("/skills")
async def clear_skills():
    """
    Полностью удаляет все записи из таблицы Skill.
    """
    with Session(engine) as session:
        statement = delete(Skill)
        result = session.exec(statement)
        session.commit()
        deleted_count = result.rowcount
    return {"status": "success", "deleted_count": deleted_count}
