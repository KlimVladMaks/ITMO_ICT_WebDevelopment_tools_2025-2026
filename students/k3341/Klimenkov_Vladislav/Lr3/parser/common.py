import requests
from bs4 import BeautifulSoup
from sqlmodel import Session

from database import engine
from models import Skill


BASE_URL = "https://en.wikipedia.org"
LIST_URL = "https://en.wikipedia.org/wiki/List_of_programming_languages"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def get_language_urls(limit=10):
    """Парсит страницу со списком языков и возвращает список полных URL (не более limit)."""
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for div in soup.find_all('div', class_='div-col'):
        for a in div.find_all('a', href=True):
            href = a['href']
            if href.startswith('/wiki/') and ':' not in href and '#' not in href:
                full_url = BASE_URL + href
                if full_url not in links:
                    links.append(full_url)
                if len(links) >= limit:
                    return links
    return links


def save_skills_bulk(skills_data):
    """
    Принимает список кортежей (name, description) и массово сохраняет новые навыки в БД.
    Игнорирует существующие записи с таким же name.
    """
    if not skills_data:
        return
    with Session(engine) as session:
        existing_names = {name for name, in session.query(Skill.name).all()}
        new_skills = []
        for name, desc in skills_data:
            if name and name not in existing_names:
                new_skills.append(Skill(name=name, description=desc))
        if new_skills:
            session.add_all(new_skills)
            session.commit()
            print(f"Массово сохранено {len(new_skills)} языков (из {len(skills_data)} обработанных)")
        else:
            print("Нет новых языков для сохранения")
