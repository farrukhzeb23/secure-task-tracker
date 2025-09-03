from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.role import Role


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str
    role_names: Optional[List[str]] = ["user"]


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    role_names: Optional[List[str]] = None


class User(UserBase):
    id: UUID
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: List[Role] = []

    class Config:
        from_attributes = True
