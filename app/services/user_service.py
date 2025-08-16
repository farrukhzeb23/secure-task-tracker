from fastapi import HTTPException
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate
from app.models.user import User


def create_user(user: UserCreate, db: Session) -> User:
    try:
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            password=user.password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as integrity_error:
        raise HTTPException(status_code=400, detail=str(integrity_error))


def get_all_users(db: Session) -> Sequence[User]:
    result = db.execute(select(User)).scalars().all()
    return result
