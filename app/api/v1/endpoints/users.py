from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import User
from app.services.user_service import get_all_users
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await get_all_users(db)
