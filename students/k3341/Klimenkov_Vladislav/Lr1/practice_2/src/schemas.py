from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

from . import models


# ========== Users ==========


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    about: Optional[str] = None


class UserFullRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    about: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_skills: Optional[List["UserSkillRead"]] = None
    user_interests: Optional[List["UserInterestRead"]] = None

    model_config = ConfigDict(from_attributes=True)


class UserShortRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    about: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    about: Optional[str] = None


# ========== Skills ==========


class SkillCreate(BaseModel):
    name: str


class SkillRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillUpdate(BaseModel):
    name: str


# ========== UserSkills ==========


class UserSkillCreate(BaseModel):
    skill_id: int
    level: Optional[models.SkillLevel] = None


class UserSkillRead(BaseModel):
    id: int
    level: Optional[models.SkillLevel] = None
    added_at: datetime
    skill: "SkillRead"

    model_config = ConfigDict(from_attributes=True)


class UserSkillUpdateLevel(BaseModel):
    level: models.SkillLevel


# ========== Interests ==========


class InterestCreate(BaseModel):
    name: str


class InterestRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterestUpdate(BaseModel):
    name: str


# ========== UserInterests ==========


class UserInterestCreate(BaseModel):
    interest_id: int


class UserInterestRead(BaseModel):
    id: int
    added_at: datetime
    interest: "InterestRead"

    model_config = ConfigDict(from_attributes=True)


# ========== Projects ==========


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: models.ProjectStatus = models.ProjectStatus.draft
    deadline: Optional[datetime] = None


class ProjectFullRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: models.ProjectStatus
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    project_members: List["ProjectMemberRead"]

    model_config = ConfigDict(from_attributes=True)


class ProjectShortRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: models.ProjectStatus
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[models.ProjectStatus] = None
    deadline: Optional[datetime] = None


# ========== ProjectMembers ==========


class ProjectMemberCreate(BaseModel):
    user_id: int
    role: models.ProjectRole = models.ProjectRole.member


class ProjectMemberRead(BaseModel):
    id: int
    role: models.ProjectRole
    joined_at: datetime
    user: UserShortRead

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberUpdateRole(BaseModel):
    role: models.ProjectRole


# ========== Tasks ==========


class TaskCreate(BaseModel):
    assignee_id: int
    title: str
    description: Optional[str] = None
    status: models.TaskStatus = models.TaskStatus.todo
    deadline: Optional[datetime] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: models.TaskStatus
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    assignee: UserShortRead
    project: ProjectShortRead

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    assignee_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[models.TaskStatus] = None
    deadline: Optional[datetime] = None
