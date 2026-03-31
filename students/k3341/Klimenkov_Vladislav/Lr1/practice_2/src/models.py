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
    added_at: datetime = Field(default_factory=get_utc_now())


class UserInterest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    interest_id: int = Field(foreign_key="interest.id")
    added_at: datetime = Field(default_factory=get_utc_now())


class ProjectMember(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    project_id: int = Field(foreign_key="project.id")
    role: Optional[str] = Field(default=None)
    joined_at: datetime = Field(default_factory=get_utc_now())


# ===== Основные модели =====


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    full_name: str = Field()
    about: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now())
    updated_at: datetime = Field(default_factory=get_utc_now())

    skills: List["Skill"] = Relationship(
        back_populates="users",
        link_model=UserSkill,
    )
    interests: List["Interest"] = Relationship(
        back_populates="users",
        link_model=UserInterest
    )
    projects: List["Project"] = Relationship(
        back_populates="members",
        link_model=ProjectMember
    )
    tasks: List["Task"] = Relationship(back_populates="assignee")
    user_skills: List[UserSkill] = Relationship(back_populates="user")
    user_interests: List[UserInterest] = Relationship(back_populates="user")
    project_memberships: List[ProjectMember] = Relationship(back_populates="user")


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime = Field(default_factory=get_utc_now())
    updated_at: datetime = Field(default_factory=get_utc_now())

    users: List[User] = Relationship(
        back_populates="skills",
        link_model=UserSkill
    )
    user_skills: List[UserSkill] = Relationship(back_populates="skill")


class Interest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime = Field(default_factory=get_utc_now())
    updated_at: datetime = Field(default_factory=get_utc_now())

    users: List[User] = Relationship(
        back_populates="interests",
        link_model=UserInterest
    )
    user_interests: List[UserInterest] = Relationship(back_populates="interest")


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    description: Optional[str] = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.draft)
    deadline: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now())
    updated_at: datetime = Field(default_factory=get_utc_now())

    members: List[User] = Relationship(
        back_populates="projects",
        link_model=ProjectMember
    )
    tasks: List["Task"] = Relationship(back_populates="project")
    project_members: List[ProjectMember] = Relationship(back_populates="project")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    assignee_id: int = Field(foreign_key="user.id")
    title: str = Field()
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.todo)
    deadline: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now())
    updated_at: datetime = Field(default_factory=get_utc_now())

    project: Optional[Project] = Relationship(back_populates="tasks")
    assignee: Optional[User] = Relationship(back_populates="tasks")
