from fastapi import HTTPException
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import hash_password


async def create_user(user: UserCreate, db: AsyncSession) -> User:

    email_result = await db.execute(select(User).where((User.email == user.email)))

    if email_result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Email already exists choose another email")

    username_result = await db.execute(select(User).where((User.username == user.username)))

    if username_result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Username already exists choose another username")

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
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong when creating the user")


async def get_all_users(db: AsyncSession) -> Sequence[User]:
    result = await db.execute(select(User))
    return result.scalars().all()
