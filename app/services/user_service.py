from typing import Optional, Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.role_service import assign_roles_to_user, get_user_with_roles


async def create_user(user: UserCreate, db: AsyncSession) -> User:

    existing_user = await get_user_by_email(user.email, db)

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Email already exists choose another email"
        )

    existing_user = await get_user_by_username(user.username, db)

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username already exists choose another username"
        )

    try:
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            password=hash_password(user.password),
        )

        # Assign roles to user
        if user.role_names:
            await assign_roles_to_user(db_user, user.role_names, db)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # Load the relationships
        await db.refresh(db_user, ["roles"])

        return db_user
    except Exception as error:
        await db.rollback()  # Rollback on any error
        raise HTTPException(
            status_code=500, detail=f"Error creating user: {str(error)}"
        )


async def get_all_users(db: AsyncSession) -> Sequence[User]:
    result = await db.execute(select(User).options(selectinload(User.roles)))
    return result.scalars().all()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()
