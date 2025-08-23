from datetime import datetime, timedelta, timezone
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.user_service import get_user_by_email
from app.core.security import verify_password, create_access_token, create_refresh_token, hash_refresh_token, verify_refresh_token
from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.token import Token


async def authenticate_user(db: AsyncSession, email: str, password: str):
    users_exists = await get_user_by_email(email, db)

    if not users_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} does not exists"
        )

    if not verify_password(plain_password=password, hashed_password=users_exists.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect password, please try again",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(users_exists.id)})
    refresh_token = create_refresh_token()

    expires_at = datetime.now(timezone.utc) + \
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = RefreshToken(
        user_id=users_exists.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    await db.commit()
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str):
    result = await db.execute(
        select(RefreshToken).join(User).filter(
            RefreshToken.expires_at > datetime.now(timezone.utc)
        )
    )
    db_refresh_token = result.scalars().first()
    if not db_refresh_token or not verify_refresh_token(refresh_token, str(db_refresh_token.token_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_result = await db.execute(select(User).filter(User.id == db_refresh_token.user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    new_access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=new_access_token, refresh_token=refresh_token, token_type="bearer")
