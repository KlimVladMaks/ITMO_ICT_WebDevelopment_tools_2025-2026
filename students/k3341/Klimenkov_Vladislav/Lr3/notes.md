# Заметки

## Docker Compose

```
# Список запущенных сервисов
docker compose ps

# Запуск в фоновом режиме 
docker compose up -d

# Запуск с пересборкой образов
docker compose up -d --build

# Остановка и удаление контейнеров
docker compose down

# Остановка контейнера
docker compose stop

# Запуск остановленного контейнера
docker compose start

# Остановить и удалить контейнер вместе с данными
docker compose down -v

# Посмотреть существующие volumes
docker volume ls

# Удалить неиспользуемые тома
docker volume prune

# Удалить все тома
docker volume rm $(docker volume ls -q)

# Посмотреть все логи
docker compose logs

# Посмотреть логи конкретного сервиса
docker compose logs app
docker compose logs parser
```

## Доступ к сервисам

```
# app
http://localhost:8000/docs

# parser
http://localhost:8001/docs
```
