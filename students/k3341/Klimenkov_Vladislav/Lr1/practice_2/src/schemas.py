from pydantic import BaseModel, ConfigDict
from typing import Optional

from datetime import datetime


# ========== Skills ==========


class SkillCreate(BaseModel):
    name: str


class SkillRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillUpdate(BaseModel):
    name: str
