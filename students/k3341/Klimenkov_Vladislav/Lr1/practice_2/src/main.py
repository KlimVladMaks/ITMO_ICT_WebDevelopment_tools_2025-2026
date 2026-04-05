from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlmodel import Session

from .database import init_db, get_session
from . import schemas
from . import crud


async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


# ========== Skills ==========


@app.get("/skills", response_model=List[schemas.SkillRead])
def get_skills(session: Session = Depends(get_session)):
    skills = crud.get_skills(session)
    return skills


@app.post("/skills", response_model=schemas.SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_in: schemas.SkillCreate,
    session: Session = Depends(get_session)
):
    existing = crud.get_skill_by_name(session, skill_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Навык с этим именем уже существует",
        )
    skill = crud.create_skill(session, skill_in)
    return skill


@app.get("/skills/{skill_id}", response_model=schemas.SkillRead)
def get_skill(
    skill_id: int, 
    session: Session = Depends(get_session),
):
    skill = crud.get_skill_by_id(session, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык не найден",
        )
    return skill


@app.patch("/skills/{skill_id}", response_model=schemas.SkillRead)
def update_skill(
    skill_id: int,
    skill_in: schemas.SkillUpdate,
    session: Session = Depends(get_session),
):
    skill = crud.get_skill_by_id(session, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык не найден",
        )
    if skill_in.name != skill.name:
        existing = crud.get_skill_by_name(session, skill_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Навык с таким именем уже существует",
            )
    skill = crud.update_skill(session, skill, skill_in)
    return skill


@app.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    session: Session = Depends(get_session),
):
    skill = crud.get_skill_by_id(session, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык не найден",
        )
    crud.delete_skill(session, skill)
    return None
