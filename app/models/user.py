from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
