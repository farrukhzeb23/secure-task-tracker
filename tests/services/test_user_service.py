from sqlalchemy.ext.asyncio import AsyncSession
from app.services import user_service
from app.schemas.user import UserCreate


async def test_create_user_service_works(db: AsyncSession):
    new_user = UserCreate(
        email="johndoe@example.com",
        username="johndoe",
        full_name="John Doe",
        password="testing1234"
    )
    created_user = await user_service.create_user(new_user, db)

    assert created_user.full_name == "John Doe"
