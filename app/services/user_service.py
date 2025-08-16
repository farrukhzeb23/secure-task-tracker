from fastapi import HTTPException
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate
from app.models.user import User


async def create_user(user: UserCreate, db: AsyncSession) -> User:
    try:
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            password=user.password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as integrity_error:
        raise HTTPException(status_code=400, detail=str(integrity_error))


async def get_all_users(db: AsyncSession) -> Sequence[User]:
    result = await db.execute(select(User))
    return result.scalars().all()
