# Задача 2. Параллельный парсинг веб-страниц с сохранением в базу данных

## Описание задания

**Задача:** Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов `threading`, `multiprocessing` и `async`. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных.

Подробности задания:

1. Напишите три различных программы на Python, использующие каждый из подходов: `threading`, `multiprocessing` и `async`.
2. Каждая программа должна содержать функцию `parse_and_save(url)`, которая будет загружать HTML-страницу по указанному URL, парсить ее, сохранять заголовок страницы в базу данных и выводить результат на экран.
3. Используйте базу данных из лабораторной работы номер 1 для заполнения ее данными. Если Вы не понимаете, какие таблицы и откуда Вы могли бы заполнить с помощью парсинга, напишите преподавателю в общем чате потока.
4. Для `threading` используйте модуль `threading`, для `multiprocessing` - модуль `multiprocessing`, а для `async` - ключевые слова `async/await` и модуль `aiohttp` для асинхронных запросов.
5. Создайте список нескольких URL-адресов веб-страниц для парсинга и разделите его на равные части для параллельного парсинга.
6. Запустите параллельный парсинг для каждой программы и сохраните данные в базу данных.
7. Замерьте время выполнения каждой программы и сравните результаты.

## Выполнение задания

Для парсинга были взяты 100 страниц Wikipedia про языки программирования, с каждой из которых нужно было извлечь поля `name` и `description` и записать в таблицу `Skill` в БД. Для каждого подхода использовалось разбиение на 8 потоков/процессов/корутин. 

Ниже представлен код реализованных программ:

### 1. `sync_parser.py`

Синхронный однопоточный парсер, который будет выступать в качестве эталонного решения.

```py
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

    urls = get_language_urls(limit=100)
    print(f"Получено {len(urls)} ссылок")
    run_sync(urls)
```

### 2. `threading_parser.py`

Парсер с разбиением на потоки.

```py
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
```

### 3. `multiprocessing_parser.py`

Парсер с разбиением на процессы.

```py
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
```

### 4. `async_parser.py`

Парсер с разбиением на корутины.

```py
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
```

### Полученные результаты

В результате запуска каждой из программ были получены следующие результаты:

```
Массово сохранено 100 языков (из 100 обработанных)
Синхронный подход занял 51.97 секунд

Массово сохранено 100 языков (из 100 обработанных)
Threading подход (workers=8) занял 18.04 секунд

Массово сохранено 100 языков (из 100 обработанных)
Multiprocessing подход (processes=8) занял 6.81 секунд

Массово сохранено 100 языков (из 100 обработанных)
Async подход (concurrent=8) занял 9.17 секунд
```

### Анализ результатов

Полученный результаты оказались не совсем ожидаемыми, так как мною прогнозировалось, что подход `async` должен был показать себя лучше всех, однако, как видим, наилучшее время показал подход `multiprocessing`. Попробуем сделать общие выводы и объяснить полученные результаты:

* Базовый синхронный подход ожидаемо показал наихудшее время, так как выполнял все операции строго последовательно, из-за чего приходилось последовательно ждать выполнение каждого запроса к Wikipedia, что приводило к простою программы на время ожидания каждого ответа.
* Подход `threading` показал себя значительно лучше синхронного подхода, но всё-равно хуже подходов `async` и `multiprocessing`. В рамках `threading` применяется разделение на потоки, благодаря чему, пока один поток ждёт ответ от сервера, другой может отправлять запросы или проводить парсинг. Подобный подход позволил сократить время выполннения с `51.97` секунд до `18.04` секунд. Однако, как было сказано в первом задании, `threading` всё равно работает лишь с одним GIL, а значит не может выполнять несколько парсингов одновременно, так как это CPU-нагрузка. То есть `threading` выигрывает за счёт параллельной обработки I/O-операций, но вот при парсинге полученных HTML-страниц истинной параллельности он не реализует.
* Второе место по скорости выполнения занял подход `async`, который по принципу своей работы во многом похож на `threading` (т.е. также позволяет параллельно работать с I/O-операциями, но при этом также имеет лишь один GIL и при работе с CPU-нагрузкой сталкивается с блокировкой event loop, пока соответствующая операция не будет выполнена), но при этом работает с корутинами, а не с потоками, это позволяет более быстро переключаться между ними, что, как мы можем видеть, позволило сократить время выполнения с `18.04` секунд у `threading` до `9.17` секунд у `async`. Однако так как в рамках задания также требовался парсинг HTML-страниц, т.е. CPU-нагрузка, то `async` показал себя не так хорошо как мог бы, так как вынужден был сталкиваться с блокировкой event loop на время выполнения непосредственного самого парсинга.
* Лучшее время показал подход `multiprocessing`, обогнав в этом отношении даже `async`. Как было сказано в первом задании, `multiprocessing`, в отличие от `threading` и `async`, создаёт отдельные процессы, каждый из которых обладает собственным GIL, что позволяет выполнять параллельно не только I/O, но и CPU-операции (при наличии нескольких процессоров на устройстве), хотя это и требует больше накладных расходов, так как работа с отдельными процессами требует больше времени, чем с потоками и корутинами. Однако, видимо, в рамках данного задания выигрыш от параллельного парсинга (CPU-нагрузка) перевесил дополнительные расходы на работу с отдельными процессами, за счёт чего `multiprocessing` и смог обойти `async`.

## Вывод

По результатам выполнения данной работы можно сделать вывод, что для подобных задач парсинга двумя наиболее оптимальными подходами оказались `async` и `multiprocessing`. `async` лучше подходит, когда "узком горлышком" задачи являются I/O-операции, так как корутины `async` обеспечивают более эффективную работы с ними, чем потоки `threading`. Однако если при парсинге также имеет место быть достаточно большая CPU-нагрузка (например, при обработке полученных HTML-страниц), то `multiprocessing` может показать более высокую эффективность, как мы увидели в примере выше.
