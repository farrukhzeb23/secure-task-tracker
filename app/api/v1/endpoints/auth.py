from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.user import User, UserCreate
from app.services.auth_service import authenticate_user, refresh_access_token
from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def handle_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    return await authenticate_user(db, form_data.username, form_data.password)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=Token)
async def handle_refresh_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    return await refresh_access_token(db, refresh_token=request.refresh_token)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=User)
async def handle_register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(user, db)
