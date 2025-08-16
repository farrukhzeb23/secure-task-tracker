from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import User, UserCreate
from app.services.user_service import create_user, get_all_users
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    return get_all_users(db)


@router.post("/", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(user, db)
