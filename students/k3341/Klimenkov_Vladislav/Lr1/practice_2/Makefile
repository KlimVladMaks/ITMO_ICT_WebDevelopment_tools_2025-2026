.PHONY: up down restart

up:
	@echo "Запускаем PostgreSQL..."
	docker-compose up -d
	@echo "Ждём, когда PostgreSQL будет готова..."
	sleep 3
	@echo "Запускаем FastAPI..."
	. .venv/bin/activate && uvicorn src.main:app --reload
	sleep 1
	@echo "Все процессы запущены!"

down:
	@echo "Остановка FastAPI..."
	-pkill -f "uvicorn src.main:app" 2>/dev/null
	@echo "Остановка PostgreSQL..."
	docker-compose down
	@echo "Все процессы остановлены!"

restart: down up
