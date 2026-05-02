from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


def get_utc_now():
    """Функция для получения текущего времени"""
    return datetime.now(timezone.utc)


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
