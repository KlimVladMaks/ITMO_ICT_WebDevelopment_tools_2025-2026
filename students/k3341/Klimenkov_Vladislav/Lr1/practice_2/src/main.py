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
def get_skills(*, session: Session = Depends(get_session)):
    skills = crud.get_skills(session)
    return skills


@app.post("/skills", response_model=schemas.SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(
    *, 
    session: Session = Depends(get_session), 
    skill_in: schemas.SkillCreate
):
    existing = crud.get_skill_by_name(session, skill_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Навык с этим именем уже существует",
        )
    skill = crud.create_skill(session, skill_in)
    return skill
