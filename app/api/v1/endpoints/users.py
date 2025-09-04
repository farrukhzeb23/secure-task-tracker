from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_admin
from app.schemas.user import User, UserUpdate
from app.services.user_service import (
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User])
async def get_users(
    db: AsyncSession = Depends(get_db), _: User = Depends(require_admin())
):
    return await get_all_users(db)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=User)
async def handle_get_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user_by_id_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin()),
):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
async def update_user_endpoint(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin()),
):
    return await update_user(user_id, user_update, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin()),
):
    await delete_user(user_id, db)
