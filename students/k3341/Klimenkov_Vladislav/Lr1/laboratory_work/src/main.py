from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
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


# ========== Admin ==========


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"])
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


@app.patch("/users/{user_id}/admin", response_model=schemas.UserShortRead, tags=["Admin"])
def change_platform_admin_role(
    user_id: int,
    user_role_in: schemas.ChangePlatformAdminRole,
    current_admin_id: int = Depends(auth.get_current_admin_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    user = crud.change_platform_admin_role(session, user, user_role_in)
    return user


# ========== Users ==========


@app.get("/users/me", response_model=schemas.UserFullRead, tags=["Users"])
def get_current_user(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, current_user_id)
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


@app.get("/users", response_model=List[schemas.UserFullRead], tags=["Users"])
def get_users(
    current_user_id: int = Depends(auth.get_current_user_id),
    session: Session = Depends(get_session)
):
    users = crud.get_users(session)
    return users


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


@app.get("/users/{user_id}/skills/{skill_id}", response_model=schemas.UserSkillRead, tags=["UserSkills"])
def get_user_skill(
    user_id: int,
    skill_id: int,
    session: Session = Depends(get_session)
):
    user_skill = crud.get_user_skill(session, user_id, skill_id)
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык пользователя не найден",
        )
    return user_skill


@app.delete("/users/{user_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["UserSkills"])
def delete_user_skill(
    user_id: int,
    skill_id: int,
    session: Session = Depends(get_session)
):
    user_skill = crud.get_user_skill(session, user_id, skill_id)
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык пользователя не найден",
        )
    crud.delete_user_skill(session, user_skill)
    return None


@app.patch("/users/{user_id}/skills/{skill_id}/level", response_model=schemas.UserSkillRead, tags=["UserSkills"])
def update_user_skill_level(
    user_id: int,
    skill_id: int,
    level_in: schemas.UserSkillUpdateLevel,
    session: Session = Depends(get_session)
):
    user_skill = crud.get_user_skill(session, user_id, skill_id)
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык пользователя не найден",
        )
    user_skill = crud.update_user_skill_level(session, user_skill, level_in)
    return user_skill


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


# ========== UserInterests ==========


@app.get("/users/{user_id}/interests", response_model=List[schemas.UserInterestRead], tags=["UserInterests"])
def get_user_interests(
    user_id: int,
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


@app.post("/users/{user_id}/interests", 
          response_model=schemas.UserInterestRead, 
          status_code=status.HTTP_201_CREATED, 
          tags=["UserInterests"])
def add_user_interest(
    user_id: int,
    interest_in: schemas.UserInterestCreate,
    session: Session = Depends(get_session)
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь не найден"
        )
    interest = crud.get_interest_by_id(session, interest_in.interest_id)
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Интерес не найден"
        )
    existing = crud.get_user_interest(session, user_id, interest_in.interest_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь уже имеет этот интерес"
        )
    user_interest = crud.add_user_interest(session, user_id, interest_in)
    return user_interest


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


@app.delete("/users/{user_id}/interests/{interest_id}", 
            status_code=status.HTTP_204_NO_CONTENT, 
            tags=["UserInterests"])
def delete_user_interest(
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
    crud.delete_user_interest(session, user_interest)
    return None


# ========== Projects ==========


@app.get("/projects", response_model=List[schemas.ProjectFullRead], tags=["Projects"])
def get_projects(session: Session = Depends(get_session)):
    projects = crud.get_projects(session)
    return projects


@app.post("/projects", response_model=schemas.ProjectFullRead, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(
    project_in: schemas.ProjectCreate,
    session: Session = Depends(get_session)
):
    project = crud.create_project(session, project_in)
    return project


@app.get("/projects/{project_id}", response_model=schemas.ProjectFullRead, tags=["Projects"])
def get_project(
    project_id: int,
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
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    project = crud.update_project(session, project, project_in)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def delete_project(
    project_id: int,
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
        )
    crud.delete_project(session, project)
    return None


@app.get("/users/{user_id}/projects", response_model=List[schemas.ProjectShortRead], tags=["Projects"])
def get_user_projects(
    user_id: int,
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
    session: Session = Depends(get_session)
):
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
    session: Session = Depends(get_session)
):
    member = crud.get_project_member(session, project_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Участник проекта не найден"
        )
    crud.delete_project_member(session, member)
    return None


# ========== Tasks ==========


@app.get("/projects/{project_id}/tasks", response_model=List[schemas.TaskRead], tags=["Tasks"])
def get_tasks(
    project_id: int,
    session: Session = Depends(get_session),
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
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
    session: Session = Depends(get_session)
):
    project = crud.get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Проект не найден"
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
    task = crud.create_task(session, project_id, task_in)
    return task


@app.get("/projects/{project_id}/tasks/{task_id}", response_model=schemas.TaskRead, tags=["Tasks"])
def get_task(
    project_id: int,
    task_id: int,
    session: Session = Depends(get_session)
):
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
    session: Session = Depends(get_session)
):
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
    session: Session = Depends(get_session)
):
    task = crud.get_task_by_id(session, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Задача не найдена в этом проекте"
        )
    crud.delete_task(session, task)
    return None
