from fastapi import FastAPI, HTTPException, status
from typing import List

from .temp_db import temp_db
from .models import User


app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
def get_api_status() -> dict:
    return {"status": "ok"}


@app.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
def get_user_list() -> List[User]:
    return temp_db


@app.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def get_user(user_id: int) -> User:
    for user in temp_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def post_user(user: User) -> User:
    temp_db.append(user)
    return user


@app.put("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def put_user(user_id: int, updated_user: User) -> User:
    for i, user in enumerate(temp_db):
        if user.id == user_id:
            temp_db[i] = updated_user
            return updated_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    for i, user in enumerate(temp_db):
        if user.id == user_id:
            temp_db.pop(i)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
