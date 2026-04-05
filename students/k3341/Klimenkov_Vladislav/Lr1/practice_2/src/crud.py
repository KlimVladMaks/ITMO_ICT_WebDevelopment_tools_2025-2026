from sqlmodel import Session, select
from typing import List, Optional

from . import models
from . import schemas


# ========== Skills ==========


def get_skills(session: Session) -> List[models.Skill]:
    return session.exec(select(models.Skill)).all()


def get_skill_by_id(session: Session, skill_id: int) -> Optional[models.Skill]:
    return session.get(models.Skill, skill_id)


def get_skill_by_name(session: Session, name: str) -> Optional[models.Skill]:
    return session.exec(select(models.Skill).where(models.Skill.name == name)).first()


def create_skill(session: Session, skill_in: schemas.SkillCreate) -> models.Skill:
    skill = models.Skill(name=skill_in.name)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


def update_skill(
        session: Session, 
        skill: models.Skill, 
        skill_in: schemas.SkillUpdate
) -> models.Skill:
    skill.name = skill_in.name
    skill.updated_at = models.get_utc_now()
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


def delete_skill(session: Session, skill: models.Skill) -> None:
    session.delete(skill)
    session.commit()


# ========== Interests ==========


def get_interests(session: Session) -> List[models.Interest]:
    return session.exec(select(models.Skill)).all()


def get_interest_by_name(session: Session, name: str) -> Optional[models.Interest]:
    return session.exec(select(models.Skill).where(models.Skill.name == name)).first()
