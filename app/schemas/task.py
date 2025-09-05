from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class Task(TaskBase):
    id: UUID
    is_completed: bool = False
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    pages: int


class PaginatedTaskResponse(BaseModel):
    items: List[Task]
    meta: PaginationMeta
