from fastapi import HTTPException
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import hash_password


async def create_user(user: UserCreate, db: AsyncSession) -> User:
    try:
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            password=hash_password(user.password)
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Email or Username must be unique")


async def get_all_users(db: AsyncSession) -> Sequence[User]:
    result = await db.execute(select(User))
    return result.scalars().all()
