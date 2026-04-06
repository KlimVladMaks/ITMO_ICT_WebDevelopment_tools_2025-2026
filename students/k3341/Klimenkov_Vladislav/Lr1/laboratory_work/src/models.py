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


class ProjectRole(str, Enum):
    admin = "admin"
    member = "member"


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
    role: ProjectRole = Field(default=ProjectRole.member)
    joined_at: datetime = Field(default_factory=get_utc_now)

    user: "User" = Relationship(back_populates="project_memberships")
    project: "Project" = Relationship(back_populates="project_members")


# ===== Основные модели =====


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    password_hash: str = Field()
    full_name: str = Field()
    about: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    user_skills: List["UserSkill"] = Relationship(back_populates="user")
    user_interests: List["UserInterest"] = Relationship(back_populates="user")
    project_memberships: List["ProjectMember"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="assignee")

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
    assignee_id: int = Field(foreign_key="user.id")
    title: str = Field()
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.todo)
    deadline: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    project: Optional[Project] = Relationship(back_populates="tasks")
    assignee: Optional[User] = Relationship(back_populates="tasks")
