# Работа .venv

```
python3 -m venv .venv
source .venv/bin/activate
deactivate
```

# Запуск сервера

```
uvicorn src.main:app --reload
```

# Docs

```
127.0.0.1:8000/docs
```

# Работа с ресурсами

```
pip freeze > requirements.txt
pip install -r requirements.txt
```

# Docker Compose

```
# Список запущенных сервисов
docker-compose ps

# Запуск в фоновом режиме 
docker-compose up -d

# Остановка и удаление контейнеров
docker-compose down

# Остановка контейнера
docker compose stop

# Запуск остановленного контейнера
docker compose start
```

# Добавление пользователя в группу `docker`

Данные команды требуются для работы с Docker без `sudo`.

```
sudo usermod -aG docker $USER
newgrp docker
```

# Шпаргалка по Docker и Docker Compose

https://rabrain.ru/special/handbook/docker/remember/
