from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import User
from app.dependencies.auth import get_current_user
from app.services.user_service import get_all_users
from app.core.database import get_db
from app.dependencies.rbac import require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User])
async def get_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin())):
    return await get_all_users(db)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=User)
async def handle_get_current_user(current_user: User = Depends(get_current_user)):
    return current_user
