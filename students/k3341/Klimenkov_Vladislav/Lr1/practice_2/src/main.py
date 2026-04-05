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


@app.get("/skills", response_model=List[schemas.SkillRead], tags=["Skills"])
def get_skills(session: Session = Depends(get_session)):
    skills = crud.get_skills(session)
    return skills


@app.post("/skills", response_model=schemas.SkillRead, status_code=status.HTTP_201_CREATED, tags=["Skills"])
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


@app.get("/skills/{skill_id}", response_model=schemas.SkillRead, tags=["Skills"])
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


@app.patch("/skills/{skill_id}", response_model=schemas.SkillRead, tags=["Skills"])
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


@app.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Skills"])
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


# ========== Interests ==========


@app.get("/interests", response_model=List[schemas.InterestRead], tags=["Interests"])
def get_interests(session: Session = Depends(get_session)):
    interests = crud.get_interests(session)
    return interests


@app.post("/interests", response_model=schemas.InterestRead, status_code=status.HTTP_201_CREATED, tags=["Interests"])
def create_interest(
    interest_in: schemas.InterestCreate,
    session: Session = Depends(get_session)
):
    existing = crud.get_interest_by_name(session, interest_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Интерес с таким именем уже существует",
        )
    interest = crud.create_interest(session, interest_in)
    return interest


@app.get("/interests/{interest_id}", response_model=schemas.InterestRead, tags=["Interests"])
def get_interest(
    interest_id: int, 
    session: Session = Depends(get_session),
):
    interest = crud.get_interest_by_id(session, interest_id)
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Интерес не найден",
        )
    return interest


@app.patch("/interests/{interest_id}", response_model=schemas.InterestRead, tags=["Interests"])
def update_interest(
    interest_id: int,
    interest_in: schemas.InterestUpdate,
    session: Session = Depends(get_session),
):
    interest = crud.get_interest_by_id(session, interest_id)
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Интерес не найден",
        )
    if interest_in.name != interest.name:
        existing = crud.get_interest_by_name(session, interest_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Интерес с таким именем уже существует",
            )
    interest = crud.update_interest(session, interest, interest_in)
    return interest


@app.delete("/interests/{interest_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Interests"])
def delete_interest(
    interest_id: int,
    session: Session = Depends(get_session),
):
    interest = crud.get_interest_by_id(session, interest_id)
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык не найден",
        )
    crud.delete_interest(session, interest)
    return None
