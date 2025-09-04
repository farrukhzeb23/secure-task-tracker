from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
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


async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.roles))
    )
    return result.scalar_one_or_none()


async def update_user(user_id: UUID, user_update: UserUpdate, db: AsyncSession) -> User:
    existing_user = await get_user_by_id(user_id, db)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if email is being updated and if it conflicts
    if user_update.email and user_update.email != existing_user.email:
        email_user = await get_user_by_email(user_update.email, db)
        if email_user:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Check if username is being updated and if it conflicts
    if user_update.username and user_update.username != existing_user.username:
        username_user = await get_user_by_username(user_update.username, db)
        if username_user:
            raise HTTPException(status_code=400, detail="Username already exists")

    try:
        # Prepare update data
        update_data = {}
        if user_update.email:
            update_data["email"] = user_update.email
        if user_update.username:
            update_data["username"] = user_update.username
        if user_update.full_name:
            update_data["full_name"] = user_update.full_name
        if user_update.is_active is not None:
            update_data["is_active"] = user_update.is_active
        if user_update.password:
            update_data["password"] = hash_password(user_update.password)

        # Update user basic fields first
        if update_data:
            await db.execute(
                update(User).where(User.id == user_id).values(**update_data)
            )

        # Handle role updates - commit basic updates first, then handle roles
        if user_update.role_names is not None:
            await db.commit()  # Commit basic field updates first
            # Get fresh user object for role assignment
            fresh_user = await get_user_by_id(user_id, db)
            await assign_roles_to_user(fresh_user, user_update.role_names, db)
            await db.commit()  # Commit role updates
        else:
            await db.commit()  # Commit basic field updates

        # Return updated user with relationships
        return await get_user_by_id(user_id, db)
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating user: {str(error)}"
        )


async def delete_user(user_id: UUID, db: AsyncSession) -> bool:
    existing_user = await get_user_by_id(user_id, db)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()
        return True
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting user: {str(error)}"
        )
