from fastapi import APIRouter
from app.schemas.user import User, UserCreate
from app.services.user_service import create_user, get_all_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User])
def get_users():
    return get_all_users()


@router.post("/", response_model=User)
def create_new_user(user: UserCreate):
    return create_user(user)
