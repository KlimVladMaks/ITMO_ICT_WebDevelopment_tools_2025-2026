from sqlmodel import Session, select
from typing import List, Optional

from . import models
from . import schemas


# ========== Skills ==========


def get_skills(session: Session) -> List[models.Skill]:
    return session.exec(select(models.Skill)).all()


def get_skill_by_name(session: Session, name: str) -> Optional[models.Skill]:
    return session.exec(select(models.Skill).where(models.Skill.name == name)).first()


def create_skill(session: Session, skill_in: schemas.SkillCreate) -> models.Skill:
    skill = models.Skill(name=skill_in.name)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill
