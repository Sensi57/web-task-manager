from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- Users / Auth ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, examples=["alex"])
    password: str = Field(min_length=6, max_length=72, examples=["secret123"])


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Tasks ----------
class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["Сдать проект по Docker"])
    description: str | None = Field(default=None, examples=["Подготовить Postman и README"])
    done: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
