from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from . import models
from . import schemas


# ========== Users ==========


def get_users(session: Session) -> List[models.User]:
    return session.exec(select(models.User)).all()


def get_user_by_id(session: Session, user_id: int) -> Optional[models.User]:
    return session.get(models.User, user_id)


def get_user_by_username(session: Session, username: str) -> Optional[models.User]:
    return session.exec(select(models.User).where(models.User.username == username)).first()


def get_user_by_email(session: Session, email: str) -> Optional[models.User]:
    return session.exec(select(models.User).where(models.User.email == email)).first()


def create_user(session: Session, user_in: schemas.UserCreate) -> models.User:
    user = models.User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        about=user_in.about
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user: models.User, user_in: schemas.UserUpdate) -> models.User:
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    user.updated_at = models.get_utc_now()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user: models.User) -> None:
    session.delete(user)
    session.commit()


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


# ========== User Skills ==========


def get_user_skills(session: Session, user_id: int) -> List[models.UserSkill]:
    return session.exec(
        select(models.UserSkill).where(models.UserSkill.user_id == user_id)
    ).all()


def get_user_skill(session: Session, user_id: int, skill_id: int) -> Optional[models.UserSkill]:
    return session.exec(
        select(models.UserSkill).where(
            models.UserSkill.user_id == user_id,
            models.UserSkill.skill_id == skill_id
        )
    ).first()


def add_user_skill(
    session: Session, 
    user_id: int, 
    skill_in: schemas.UserSkillCreate
) -> models.UserSkill:
    user_skill = models.UserSkill(
        user_id=user_id,
        skill_id=skill_in.skill_id,
        level=skill_in.level
    )
    session.add(user_skill)
    session.commit()
    session.refresh(user_skill)
    return user_skill


def update_user_skill_level(
    session: Session, 
    user_skill: models.UserSkill, 
    level_in: schemas.UserSkillUpdateLevel
) -> models.UserSkill:
    user_skill.level = level_in.level
    session.add(user_skill)
    session.commit()
    session.refresh(user_skill)
    return user_skill


def delete_user_skill(session: Session, user_skill: models.UserSkill) -> None:
    session.delete(user_skill)
    session.commit()


# ========== Interests ==========


def get_interests(session: Session) -> List[models.Interest]:
    return session.exec(select(models.Interest)).all()


def get_interest_by_id(session: Session, interest_id: int) -> Optional[models.Interest]:
    return session.get(models.Interest, interest_id)


def get_interest_by_name(session: Session, name: str) -> Optional[models.Interest]:
    return session.exec(select(models.Interest).where(models.Interest.name == name)).first()


def create_interest(session: Session, interest_in: schemas.InterestCreate) -> models.Interest:
    interest = models.Interest(name=interest_in.name)
    session.add(interest)
    session.commit()
    session.refresh(interest)
    return interest


def update_interest(
        session: Session, 
        interest: models.Interest, 
        interest_in: schemas.InterestUpdate
) -> models.Interest:
    interest.name = interest_in.name
    interest.updated_at = models.get_utc_now()
    session.add(interest)
    session.commit()
    session.refresh(interest)
    return interest


def delete_interest(session: Session, interest: models.Interest) -> None:
    session.delete(interest)
    session.commit()


# ========== UserInterests ==========

def get_user_interests(session: Session, user_id: int) -> List[models.UserInterest]:
    return session.exec(
        select(models.UserInterest).where(models.UserInterest.user_id == user_id)
    ).all()


def get_user_interest(session: Session, user_id: int, interest_id: int) -> Optional[models.UserInterest]:
    return session.exec(
        select(models.UserInterest).where(
            models.UserInterest.user_id == user_id,
            models.UserInterest.interest_id == interest_id
        )
    ).first()


def add_user_interest(
    session: Session, 
    user_id: int, 
    interest_in: schemas.UserInterestCreate
) -> models.UserInterest:
    user_interest = models.UserInterest(
        user_id=user_id,
        interest_id=interest_in.interest_id
    )
    session.add(user_interest)
    session.commit()
    session.refresh(user_interest)
    return user_interest


def delete_user_interest(session: Session, user_interest: models.UserInterest) -> None:
    session.delete(user_interest)
    session.commit()


# ========== Projects ==========


def get_projects(session: Session) -> List[models.Project]:
    return session.exec(select(models.Project)).all()


def get_project_by_id(session: Session, project_id: int) -> Optional[models.Project]:
    return session.get(models.Project, project_id)


def create_project(session: Session, project_in: schemas.ProjectCreate,) -> models.Project:
    project = models.Project(
        title=project_in.title,
        description=project_in.description,
        status=project_in.status,
        deadline=project_in.deadline
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def update_project(
    session: Session, 
    project: models.Project, 
    project_in: schemas.ProjectUpdate
) -> models.Project:
    for field, value in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    project.updated_at = models.get_utc_now()
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, project: models.Project) -> None:
    session.delete(project)
    session.commit()


def get_user_projects(session: Session, user_id: int) -> Optional[List[models.Project]]:
    user = get_user_by_id(session, user_id)
    if not user:
        return
    return user.projects


# ========== ProjectMembers ==========


def get_project_members(session: Session, project_id: int) -> List[models.ProjectMember]:
    return session.exec(
        select(models.ProjectMember).where(models.ProjectMember.project_id == project_id)
    ).all()


def get_project_member(session: Session, project_id: int, user_id: int) -> Optional[models.ProjectMember]:
    return session.exec(
        select(models.ProjectMember).where(
            models.ProjectMember.project_id == project_id,
            models.ProjectMember.user_id == user_id
        )
    ).first()


def add_project_member(
    session: Session, 
    project_id: int, 
    member_in: schemas.ProjectMemberCreate
) -> models.ProjectMember:
    member = models.ProjectMember(
        user_id=member_in.user_id,
        project_id=project_id,
        role=member_in.role
    )
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def update_project_member(
    session: Session, 
    member: models.ProjectMember, 
    role_in: schemas.ProjectMemberUpdateRole
) -> models.ProjectMember:
    member.role = role_in.role
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def delete_project_member(session: Session, member: models.ProjectMember) -> None:
    session.delete(member)
    session.commit()


# ========== Tasks ==========


def get_tasks_by_project(session: Session, project_id: int) -> List[models.Task]:
    return session.exec(
        select(models.Task)
        .where(models.Task.project_id == project_id)
    ).all()


def get_task_by_id(session: Session, task_id: int) -> Optional[models.Task]:
    return session.get(models.Task, task_id)


def create_task(
    session: Session, 
    project_id: int, 
    task_in: schemas.TaskCreate
) -> models.Task:
    task = models.Task(
        project_id=project_id,
        assignee_id=task_in.assignee_id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        deadline=task_in.deadline
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task(
    session: Session, 
    task: models.Task, 
    task_in: schemas.TaskUpdate
) -> models.Task:
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    task.updated_at = models.get_utc_now()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task: models.Task) -> None:
    session.delete(task)
    session.commit()
