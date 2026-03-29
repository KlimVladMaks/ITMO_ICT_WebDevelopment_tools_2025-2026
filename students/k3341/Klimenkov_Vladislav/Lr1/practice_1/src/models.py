from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class SkillLevel(Enum):
    learning = "learning"
    novice = "novice"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class Skill(BaseModel):
    id: int
    name: str
    level: SkillLevel


class User(BaseModel):
    id: int
    email: str
    full_name: str
    about: str
    skills: Optional[List[Skill]]
