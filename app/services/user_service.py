from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models.user import User


def create_user(user: UserCreate):
    pass


def get_all_users(db: Session) -> Sequence[User]:
    result = db.execute(select(User)).scalars().all()
    return result
