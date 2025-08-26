from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
