# Лабораторная работа 3: Упаковка FastAPI приложения в Docker, Работа с источниками данных и Очереди

## Цель

Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой данных и вызывать парсер через API и очередь.

## Выполнение

### Подзадача 1: Упаковка FastAPI приложения, базы данных и парсера данных в Docker

#### 1.1. Реализована возможность вызова парсера по HTTP

Было создано отдельное FastAPI-приложение для парсера.

`parser/main.py`

```py
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
```

#### 1.2. Созданы Dockerfile для FastAPI приложения и приложения парсера

`app/Dockerfile`

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`parser/Dockerfile`

```Dockerfile
FROM python:3.11-slim

WORKDIR /parser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### 1.3. Создан Docker Compose файл для управления оркестром сервисов, включающих FastAPI приложение, базу данных и парсер

`docker-compose.yml`

```yml
services:
  db:
    image: postgres:18.3-alpine
    container_name: project_partner_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: 12345
      POSTGRES_DB: partners_db
      PGDATA: /var/lib/postgresql/data
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d partners_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    build: ./app
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
  
  parser:
    build: ./parser
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8001:8001"

volumes:
  pgdata:
```

### Подзадача 2: Вызов парсера из FastAPI

#### 2.1. В FastAPI-приложение добавлен эндпоинт, который получает запрос от клиента, перенаправляет его парсеру и возвращает клиенту ответ от парсера

`app/src/main.py`

```py
@app.post("/parse-skills", tags=["Parser"])
async def call_parser(limit: int = Query(10, ge=1, le=200, description="Количество языков для парсинга")):
    """
    Вызывает парсер (сервис parser) для извлечения языков программирования из Wikipedia как skills.
    Возвращает результат парсинга клиенту.
    """
    parser_url = "http://parser:8001/parse"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(parser_url, params={"limit": limit})
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Parser service timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

## Вывод

В рамках данной ЛР я упаковал FastAPI-приложение в Docker, интегрировал парсер с базой данных и реализовал вызов парсера через API.
