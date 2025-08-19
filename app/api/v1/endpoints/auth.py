from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, User
from app.core.database import get_db
from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def handle_login():
    pass


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=User)
async def handle_register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(user, db)
