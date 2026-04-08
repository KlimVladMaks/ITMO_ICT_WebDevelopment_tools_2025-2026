# Лабораторная работа 1. Реализация серверного приложения FastAPI

## Цели

Научится реализовывать полноценное серверное приложение с помощью фреймворка FastAPI с применением дополнительных средств и библиотек.

## Выбранная тема

**Разработка платформы для поиска людей в команду.**

Задача - создать веб-платформу, которая поможет людям находить партнеров для совместной работы над проектами. Платформа должна предоставлять возможность пользователям создавать профили, описывать свои навыки, опыт и интересы, а также искать других участников и команды для участия в проектах.

- **Создание профилей:** Возможность пользователям создавать профили, указывать информацию о себе, своих навыках, опыте работы и предпочтениях по проектам.

- **Поиск и фильтрация профилей:** Реализация функционала поиска пользователей и команд на основе заданных критериев, таких как навыки, опыт, интересы и т.д.

- **Создание и просмотр проектов:** Возможность пользователям создавать проекты и описывать их цели, требования и ожидаемые результаты. Возможность просмотра доступных проектов и их участников.

- **Управление командами и проектами:** Возможность участникам создавать команды для совместной работы над проектами и управления участниками. Функционал для управления проектами, включая установку сроков, назначение задач, отслеживание прогресса и т.д.

## Выполнение ЛР

### Практика 1

[https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/practice_1](https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/practice_1)

### Практика 2

[https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/practice_2](https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/practice_2)

### Практика 3

[https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/practice_3](https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/practice_3)

### Лабораторная работы

[https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/laboratory_work](https://github.com/KlimVladMaks/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Klimenkov_Vladislav/Lr1/laboratory_work)

#### Все реализованные эндпоинты:

`src/main.py`

```py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlmodel import Session

from .database import init_db, get_session
from . import schemas
from . import crud
from . import auth


async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


# ========== Auth ==========


@app.post("/auth/register", 
         response_model=schemas.UserFullRead, 
         status_code=status.HTTP_201_CREATED, 
         tags=["Auth"])
def register(
    user_in: schemas.UserCreate,
    session: Session = Depends(get_session)
):
    if crud.get_user_by_username(session, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Этот username уже занят"
        )
    user = crud.create_user(session, user_in)
    return user


@app.post("/auth/login", response_model=schemas.LoginResponse, tags=["Auth"])
def login(
    login_in: schemas.LoginRequest,
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_username(session, login_in.username)
    if (user is None) or (not auth.verify_password(login_in.password, user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверное имя пользователя или пароль"
        )
    access_token = auth.encode_user_id(user.id)
    return schemas.LoginResponse(
        user=user,
        access_token=access_token
    )


# ========== Users ==========


@app.get("/users", response_model=List[schemas.UserFullRead], tags=["Users"])
def get_users(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session),
    skill_ids: Optional[List[int]] = Query(None),
    interest_ids: Optional[List[int]] = Query(None)
):
    users = crud.get_users(
        session=session,
        skill_ids=skill_ids,
        interest_ids=interest_ids
    )
    return users


@app.get("/users/me", response_model=schemas.UserFullRead, tags=["Users"])
def get_current_user(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь не найден"
        )
    return user


@app.patch("/users/me", response_model=schemas.UserFullRead, tags=["Users"])
def update_current_user(
    user_in: schemas.UserUpdate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session),
):
    user = crud.get_user_by_id(session, current_user_id)
    user = crud.update_user(session, user, user_in)
    return user


@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_current_user(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session),
):
    user = crud.get_user_by_id(session, current_user_id)
    crud.delete_user(session, user)
    return None


@app.patch("/users/me/password", status_code=status.HTTP_200_OK, tags=["Users"])
def update_current_user_password(
    password_in: schemas.UserPasswordUpdate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session),
):
    user = crud.get_user_by_id(session, current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь не найден"
        )
    if not auth.verify_password(password_in.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверный старый пароль"
        )
    crud.update_user_password(session, user, password_in.new_password)
    return None


@app.get("/users/{user_id}", response_model=schemas.UserFullRead, tags=["Users"])
def get_user(
    user_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь не найден"
        )
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(
    user_id: int,
    current_admin_id: int = Depends(auth.get_current_admin_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь не найден"
        )
    crud.delete_user(session, user)
    return None


@app.patch("/users/{user_id}/admin", response_model=schemas.UserShortRead, tags=["Users"])
def change_platform_admin_role(
    user_id: int,
    user_role_in: schemas.ChangePlatformAdminRole,
    current_admin_id: int = Depends(auth.get_current_admin_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    user = crud.change_platform_admin_role(session, user, user_role_in)
    return user


# ========== Skills ==========


@app.get("/skills", response_model=List[schemas.SkillRead], tags=["Skills"])
def get_skills(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    skills = crud.get_skills(session)
    return skills


@app.post("/skills", response_model=schemas.SkillRead, status_code=status.HTTP_201_CREATED, tags=["Skills"])
def create_skill(
    skill_in: schemas.SkillCreate,
    current_admin_id: int = Depends(auth.get_current_admin_id),
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
    current_user_id: int = Depends(auth.get_current_user_id),
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
    current_admin_id: int = Depends(auth.get_current_admin_id),
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
    current_admin_id: int = Depends(auth.get_current_admin_id),
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


# ========== UserSkills ==========


@app.get("/users/me/skills", response_model=List[schemas.UserSkillRead], tags=["UserSkills"])
def get_current_user_skills(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    skills = crud.get_user_skills(session, current_user_id)
    return skills


@app.post("/users/me/skills", 
          response_model=schemas.UserSkillRead, 
          status_code=status.HTTP_201_CREATED, 
          tags=["UserSkills"])
def add_user_skill(
    skill_in: schemas.UserSkillCreate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    skill = crud.get_skill_by_id(session, skill_in.skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык не найден",
        )
    existing = crud.get_user_skill(session, current_user_id, skill_in.skill_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь уже имеет этот навык"
        )
    user_skill = crud.add_user_skill(session, current_user_id, skill_in)
    return user_skill


@app.delete("/users/me/skills/{skill_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["UserSkills"])
def delete_current_user_skill(
    skill_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user_skill = crud.get_user_skill(session, current_user_id, skill_id)
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык пользователя не найден",
        )
    crud.delete_user_skill(session, user_skill)
    return None


@app.patch("/users/me/skills/{skill_id}/level", response_model=schemas.UserSkillRead, tags=["UserSkills"])
def update_user_skill_level(
    skill_id: int,
    level_in: schemas.UserSkillUpdateLevel,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user_skill = crud.get_user_skill(session, current_user_id, skill_id)
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык пользователя не найден",
        )
    user_skill = crud.update_user_skill_level(session, user_skill, level_in)
    return user_skill


@app.get("/users/{user_id}/skills", response_model=List[schemas.UserSkillRead], tags=["UserSkills"])
def get_user_skills(
    user_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    skills = crud.get_user_skills(session, user_id)
    return skills


@app.get("/users/{user_id}/skills/{skill_id}", response_model=schemas.UserSkillRead, tags=["UserSkills"])
def get_user_skill(
    user_id: int,
    skill_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user_skill = crud.get_user_skill(session, user_id, skill_id)
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык пользователя не найден",
        )
    return user_skill


# ========== Interests ==========


@app.get("/interests", response_model=List[schemas.InterestRead], tags=["Interests"])
def get_interests(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    interests = crud.get_interests(session)
    return interests


@app.post("/interests", response_model=schemas.InterestRead, status_code=status.HTTP_201_CREATED, tags=["Interests"])
def create_interest(
    interest_in: schemas.InterestCreate,
    current_admin_id: int = Depends(auth.get_current_admin_id),
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
    current_user_id: int = Depends(auth.get_current_user_id),
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
    current_admin_id: int = Depends(auth.get_current_admin_id),
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
    current_admin_id: int = Depends(auth.get_current_admin_id),
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


# ========== UserInterests ==========


@app.get("/users/me/interests", response_model=List[schemas.UserInterestRead], tags=["UserInterests"])
def get_current_user_interests(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    interests = crud.get_user_interests(session, current_user_id)
    return interests


@app.post("/users/me/interests", response_model=schemas.UserInterestRead, tags=["UserInterests"])
def add_current_user_interest(
    interest_in: schemas.UserInterestCreate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    interest = crud.get_interest_by_id(session, interest_in.interest_id)
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Интерес не найден"
        )
    user_interest = crud.add_user_interest(session, current_user_id, interest_in)
    return user_interest


@app.delete("/users/me/interests/{interest_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["UserInterests"])
def delete_current_user_interest(
    interest_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user_interest = crud.get_user_interest(session, current_user_id, interest_id)
    if not user_interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Интерес пользователя не найден"
        )
    crud.delete_user_interest(session, user_interest)
    return None


@app.get("/users/{user_id}/interests", response_model=List[schemas.UserInterestRead], tags=["UserInterests"])
def get_user_interests(
    user_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь не найден"
        )
    interests = crud.get_user_interests(session, user_id)
    return interests


@app.get("/users/{user_id}/interests/{interest_id}", 
         response_model=schemas.UserInterestRead, 
         tags=["UserInterests"])
def get_user_interest(
    user_id: int,
    interest_id: int,
    session: Session = Depends(get_session)
):
    user_interest = crud.get_user_interest(session, user_id, interest_id)
    if not user_interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Интерес пользователя не найден"
        )
    return user_interest


# ========== Projects ==========


@app.get("/projects", response_model=List[schemas.ProjectFullRead], tags=["Projects"])
def get_projects(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    projects = crud.get_projects(session)
    return projects


@app.post("/projects", response_model=schemas.ProjectFullRead, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(
    project_in: schemas.ProjectCreate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project = crud.create_project(session, project_in, current_user_id)
    return project


@app.get("/projects/{project_id}", response_model=schemas.ProjectFullRead, tags=["Projects"])
def get_project(
    project_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    return project


@app.patch("/projects/{project_id}", response_model=schemas.ProjectFullRead, tags=["Projects"])
def update_project(
    project_id: int,
    project_in: schemas.ProjectUpdate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if (project_member is None) or (not project_member.is_project_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Изменять проект могут только админы проекта"
        )
    project = crud.update_project(session, project, project_in)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def delete_project(
    project_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if (project_member is None) or (not project_member.is_project_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Удалить проект могут только админы проекта"
        )
    crud.delete_project(session, project)
    return None


@app.get("/users/{user_id}/projects", response_model=List[schemas.ProjectShortRead], tags=["Projects"])
def get_user_projects(
    user_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    projects = crud.get_user_projects(session, user_id)
    return projects


# ========== ProjectMembers ==========


@app.get("/projects/{project_id}/members", 
         response_model=List[schemas.ProjectMemberRead], 
         tags=["ProjectMembers"])
def get_project_members(
    project_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    members = crud.get_project_members(session, project_id)
    return members


@app.post("/projects/{project_id}/members", 
          response_model=schemas.ProjectMemberRead, 
          status_code=status.HTTP_201_CREATED, 
          tags=["ProjectMembers"])
def add_project_member(
    project_id: int,
    member_in: schemas.ProjectMemberCreate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if (project_member is None) or (not project_member.is_project_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Добавлять новых участников могут только админы проекта"
        )
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    user = crud.get_user_by_id(session, member_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь не найден"
        )
    existing = crud.get_project_member(session, project_id, member_in.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь уже является участником данного проекта"
        )
    member = crud.add_project_member(session, project_id, member_in)
    return member


@app.get("/projects/{project_id}/members/{user_id}", 
         response_model=schemas.ProjectMemberRead, 
         tags=["ProjectMembers"])
def get_project_member(
    project_id: int,
    user_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    member = crud.get_project_member(session, project_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Участник проекта не найден"
        )
    return member


@app.delete("/projects/{project_id}/members/{user_id}", 
            status_code=status.HTTP_204_NO_CONTENT, 
            tags=["ProjectMembers"])
def delete_project_member(
    project_id: int,
    user_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if (project_member is None) or (not project_member.is_project_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Удалять участников могут только админы проекта"
        )
    member = crud.get_project_member(session, project_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Участник проекта не найден"
        )
    crud.delete_project_member(session, member)
    return None


@app.patch("/projects/{project_id}/members/{user_id}/admin",
            response_model=schemas.ProjectMemberRead,
            tags=["ProjectMembers"])
def update_project_member_role(
    project_id: int,
    user_id: int,
    role_in: schemas.ProjectMemberRoleUpdate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if (project_member is None) or (not project_member.is_project_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Изменять роли участников могут только админы проекта"
        )
    member = crud.get_project_member(session, project_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Участник проекта не найден"
        )
    member = crud.update_project_member_role(session, member, role_in)
    return member


# ========== Tasks ==========


@app.get("/projects/{project_id}/tasks", response_model=List[schemas.TaskRead], tags=["Tasks"])
def get_tasks(
    project_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session),
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Смотреть задачи могут только участники проекта"
        )
    tasks = crud.get_tasks_by_project(session, project_id)
    return tasks


@app.post("/projects/{project_id}/tasks", 
          response_model=schemas.TaskRead, 
          status_code=status.HTTP_201_CREATED, 
          tags=["Tasks"])
def create_task(
    project_id: int,
    task_in: schemas.TaskCreate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Создавать задачи могут только участники проекта"
        )
    assignee = crud.get_user_by_id(session, task_in.assignee_id)
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Получатель задачи не найден"
        )
    member = crud.get_project_member(session, project_id, task_in.assignee_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Получатель задачи не является участником проекта"
        )
    task = crud.create_task(session, project_id, current_user_id, task_in)
    return task


@app.get("/projects/{project_id}/tasks/{task_id}", response_model=schemas.TaskRead, tags=["Tasks"])
def get_task(
    project_id: int,
    task_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Смотреть задачи могут только участники проекта"
        )
    task = crud.get_task_by_id(session, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Задача не найдена в этом проекте"
        )
    return task


@app.patch("/projects/{project_id}/tasks/{task_id}", response_model=schemas.TaskRead, tags=["Tasks"])
def update_task(
    project_id: int,
    task_id: int,
    task_in: schemas.TaskUpdate,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Изменять задачи могут только участники проекта"
        )
    task = crud.get_task_by_id(session, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Задача не найдена в этом проекте"
        )
    if task_in.assignee_id is not None:
        assignee = crud.get_user_by_id(session, task_in.assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Новый получатель задачи не найден"
            )
        member = crud.get_project_member(session, project_id, task_in.assignee_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Новый получатель задачи не является участником проекта"
            )
    task = crud.update_task(session, task, task_in)
    return task


@app.delete("/projects/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(
    project_id: int,
    task_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    project_member = crud.get_project_member(session, project_id, current_user_id)
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Удалять задачи могут только участники проекта"
        )
    task = crud.get_task_by_id(session, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Задача не найдена в этом проекте"
        )
    crud.delete_task(session, task)
    return None
```

#### Модели:

`src/models.py`

```py
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone


def get_utc_now():
    """Функция для получения текущего времени"""
    return datetime.now(timezone.utc)


# ===== Перечисления =====


class SkillLevel(str, Enum):
    learning = "learning"
    novice = "novice"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class ProjectStatus(str, Enum):
    draft = "draft"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


# ===== Ассоциативные модели (таблицы связи many-to-many) =====


class UserSkill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    skill_id: int = Field(foreign_key="skill.id")
    level: Optional[SkillLevel] = Field(default=None)
    added_at: datetime = Field(default_factory=get_utc_now)

    user: "User" = Relationship(back_populates="user_skills")
    skill: "Skill" = Relationship(back_populates="user_skills")


class UserInterest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    interest_id: int = Field(foreign_key="interest.id")
    added_at: datetime = Field(default_factory=get_utc_now)

    user: "User" = Relationship(back_populates="user_interests")
    interest: "Interest" = Relationship(back_populates="user_interests")


class ProjectMember(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    project_id: int = Field(foreign_key="project.id")
    is_project_admin: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=get_utc_now)

    user: "User" = Relationship(back_populates="project_memberships")
    project: "Project" = Relationship(back_populates="project_members")


# ===== Основные модели =====


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str = Field()
    full_name: str = Field()
    about: Optional[str] = Field(default=None)
    is_platform_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    user_skills: List["UserSkill"] = Relationship(back_populates="user")
    user_interests: List["UserInterest"] = Relationship(back_populates="user")
    project_memberships: List["ProjectMember"] = Relationship(back_populates="user")
    assigned_tasks: List["Task"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "[Task.assignee_id]"}
    )
    created_tasks: List["Task"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Task.creator_id]"}
    )

    @property
    def skills(self) -> List["Skill"]:
        return [us.skill for us in self.user_skills]
    
    @property
    def interests(self) -> List["Interest"]:
        return [ui.interest for ui in self.user_interests]
    
    @property
    def projects(self) -> List["Project"]:
        return [pm.project for pm in self.project_memberships]


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    user_skills: List["UserSkill"] = Relationship(back_populates="skill")

    @property
    def users(self) -> List["User"]:
        return [us.user for us in self.user_skills]


class Interest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    user_interests: List["UserInterest"] = Relationship(back_populates="interest")
    
    @property
    def users(self) -> List["User"]:
        return [ui.user for ui in self.user_interests]


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field()
    description: Optional[str] = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.draft)
    deadline: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    project_members: List["ProjectMember"] = Relationship(back_populates="project")
    tasks: List["Task"] = Relationship(back_populates="project")

    @property
    def members(self) -> List["User"]:
        return [pm.user for pm in self.project_members]


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    creator_id: Optional[int] = Field(foreign_key="user.id", default=None)
    assignee_id: Optional[int] = Field(foreign_key="user.id", default=None)
    title: str = Field()
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.todo)
    deadline: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    project: Optional[Project] = Relationship(back_populates="tasks")
    assignee: Optional[User] = Relationship(
        back_populates="assigned_tasks",
        sa_relationship_kwargs={"foreign_keys": "[Task.assignee_id]"}
    )
    creator: Optional[User] = Relationship(
        back_populates="created_tasks",
        sa_relationship_kwargs={"foreign_keys": "[Task.creator_id]"}
    )
```

#### Соединение с БД:

`src/database.py`

```py
from sqlmodel import SQLModel, Session, create_engine


db_url = 'postgresql://user:12345@localhost:5432/partners_db'
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```
