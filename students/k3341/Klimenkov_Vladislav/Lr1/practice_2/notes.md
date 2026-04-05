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

## Работа с Makefile

```
make up
make down
make restart
```
