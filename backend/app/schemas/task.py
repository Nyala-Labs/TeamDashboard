"""Task Pydantic schemas."""
from datetime import datetime
from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: str = "TODO"
    progress: int = 0
    due_date: datetime | None = None
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    team_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    progress: int | None = None
    due_date: datetime | None = None
    assignee_id: int | None = None


class TaskResponse(TaskBase):
    id: int
    team_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
