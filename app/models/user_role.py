from sqlalchemy import Column, ForeignKey, DateTime, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID, ForeignKey("roles.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
