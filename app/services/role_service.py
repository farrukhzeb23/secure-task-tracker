import uuid
from typing import List, Optional, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole


async def get_role_by_name(name: str, db: AsyncSession) -> Optional[Role]:
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def get_roles_by_names(names: List[str], db: AsyncSession) -> Sequence[Role]:
    result = await db.execute(select(Role).where(Role.name.in_(names)))
    return result.scalars().all()


async def assign_roles_to_user(db_user: User, role_names: List[str], db: AsyncSession):
    try:
        # Clear existing roles using the relationship
        db_user.roles.clear()

        # Get roles by names
        roles = await get_roles_by_names(role_names, db)

        # Assign new roles
        for role in roles:
            db_user.roles.append(role)

    except ValueError as e:
        raise ValueError(f"Invalid user_id format: {e}")
    except Exception as e:
        raise Exception(f"Error assigning roles: {e}")


async def get_user_with_roles(user_id: str, db: AsyncSession) -> Optional[User]:
    """Get user with their roles."""
    try:
        user_uuid = uuid.UUID(user_id)
        result = await db.execute(
            select(User).options(selectinload(User.roles)).where(User.id == user_uuid)
        )
        return result.scalar_one_or_none()
    except ValueError as e:
        raise ValueError(f"Invalid user_id format: {e}")
    except Exception as e:
        raise Exception(f"Error getting user with roles: {e}")
