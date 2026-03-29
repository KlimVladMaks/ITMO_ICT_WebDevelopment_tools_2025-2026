# Работа .venv

```
python3 -m venv .venv
source .venv/bin/activate
deactivate
```

# Запуск сервера

```
uvicorn main:app --reload
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
