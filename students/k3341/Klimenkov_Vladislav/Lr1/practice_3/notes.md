# Заметки

## Основные команды для работы с проектом

```
# Запуск PostgreSQL
docker-compose up -d

# Запуск FastAPI
uvicorn src.main:app --reload

# Отключение PostgreSQL
docker-compose down
```

## Работа .venv

```
python3 -m venv .venv
source .venv/bin/activate
deactivate
```

## Запуск сервера

```
uvicorn src.main:app --reload
```

## Docs

```
127.0.0.1:8000/docs
```

## Работа с ресурсами

```
pip freeze > requirements.txt
pip install -r requirements.txt
```

## Docker Compose

```
# Список запущенных сервисов
docker-compose ps

# Запуск в фоновом режиме 
docker-compose up -d

# Остановка и удаление контейнеров
docker-compose down

# Остановка контейнера
docker-compose stop

# Запуск остановленного контейнера
docker-compose start

# Остановить и удалить контейнер вместе с данными
docker-compose down -v

# Посмотреть существующие volumes
docker volume ls

# Удалить неиспользуемые тома
docker volume prune

# Удалить все тома
docker volume rm $(docker volume ls -q)
```

## Добавление пользователя в группу `docker`

Данные команды требуются для работы с Docker без `sudo`.

```
sudo usermod -aG docker $USER
newgrp docker
```

## Шпаргалка по Docker и Docker Compose

https://rabrain.ru/special/handbook/docker/remember/

## Доступ к PostgreSQL через веб-интерфейс pgAdmin

Доступ к веб-интерфейсу pgAdmin можно получить по адресу:

http://localhost:8080/

Настройки для подключения к БД:

```
General:
    - Name: project_partner_db  # Но можно дать любое другое
Connection:
    # Важно! Так как они в одной сети Docker, нужно указывать не `localhost`, 
    # а имя сервиса из docker-compose, то есть: `db`
    - Host name/address: db
    - Port: 5432
    - Maintenance database: partners_db
    - Username: user
    - Password: 12345
    - Save password?  # Активировать этот пункт

-> Нажать "Save"
```

## Работа с Alembic

Чтобы сделать миграцию для БД нужно выполнить следующие шаги:

1. Внести требуемые изменения в БД (например, изменить поля или таблицы в `models.py`).

2. Создать миграцию:

```
alembic revision --autogenerate -m "<описание_миграции>"
```

3. В `migrations/versions` появится `.py`-файл с описанием миграции. Его можно проверить на корректность.

4. Примените миграцию:

```
alembic upgrade head
```

5. После этого внесённые изменения должны быть применены к БД.

Дополнительные команды:

```
# Посмотреть текущую версию миграции
alembic current

# Откатиться на одну миграцию назад
alembic downgrade -1

# Откатиться к началу (пустая БД)
alembic downgrade base

# Создать пустую миграцию (ручное редактирование)
alembic revision -m "description"
```
