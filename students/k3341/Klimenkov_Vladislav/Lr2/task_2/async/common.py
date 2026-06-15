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


def get_language_urls(limit=50):
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


def extract_skill_from_soup(soup):
    """
    Принимает BeautifulSoup объект страницы языка.
    Возвращает кортеж (name, description) или (None, None).
    """
    title_tag = soup.find('title')
    if not title_tag:
        return None, None
    title_text = title_tag.string
    if ' - Wikipedia' in title_text:
        name = title_text.replace(' - Wikipedia', '').strip()
    else:
        name = title_text.strip()
    desc_div = soup.find('div', class_='shortdescription')
    description = desc_div.get_text(strip=True) if desc_div else None
    return name, description
