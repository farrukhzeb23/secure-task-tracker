from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service


async def test_create_user_service_works(db: AsyncSession):
    new_user = UserCreate(
        email="johndoe@example.com",
        username="johndoe",
        full_name="John Doe",
        password="testing1234",
    )
    created_user = await user_service.create_user(new_user, db)

    assert created_user.full_name == "John Doe"


async def test_get_user_by_id_success(db: AsyncSession):
    new_user = UserCreate(
        email="testuser@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    created_user = await user_service.create_user(new_user, db)

    found_user = await user_service.get_user_by_id(created_user.id, db)

    assert found_user is not None
    assert found_user.email == "testuser@example.com"
    assert found_user.username == "testuser"
    assert found_user.full_name == "Test User"


async def test_get_user_by_id_not_found(db: AsyncSession):
    non_existent_id = uuid4()

    found_user = await user_service.get_user_by_id(non_existent_id, db)

    assert found_user is None


async def test_update_user_success(db: AsyncSession):
    new_user = UserCreate(
        email="original@example.com",
        username="originaluser",
        full_name="Original Name",
        password="password123",
    )
    created_user = await user_service.create_user(new_user, db)

    update_data = UserUpdate(
        email="updated@example.com", full_name="Updated Name", is_active=False
    )

    updated_user = await user_service.update_user(created_user.id, update_data, db)

    assert updated_user.email == "updated@example.com"
    assert updated_user.full_name == "Updated Name"
    assert updated_user.is_active == False
    assert updated_user.username == "originaluser"  # unchanged


async def test_update_user_not_found(db: AsyncSession):
    non_existent_id = uuid4()
    update_data = UserUpdate(email="test@example.com")

    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(non_existent_id, update_data, db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


async def test_update_user_email_conflict(db: AsyncSession):
    # Create first user
    user1 = UserCreate(
        email="user1@example.com",
        username="user1",
        full_name="User One",
        password="password123",
    )
    created_user1 = await user_service.create_user(user1, db)

    # Create second user
    user2 = UserCreate(
        email="user2@example.com",
        username="user2",
        full_name="User Two",
        password="password123",
    )
    created_user2 = await user_service.create_user(user2, db)

    # Try to update user2's email to user1's email
    update_data = UserUpdate(email="user1@example.com")

    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(created_user2.id, update_data, db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already exists"


async def test_update_user_username_conflict(db: AsyncSession):
    # Create first user
    user1 = UserCreate(
        email="user1@example.com",
        username="user1",
        full_name="User One",
        password="password123",
    )
    created_user1 = await user_service.create_user(user1, db)

    # Create second user
    user2 = UserCreate(
        email="user2@example.com",
        username="user2",
        full_name="User Two",
        password="password123",
    )
    created_user2 = await user_service.create_user(user2, db)

    # Try to update user2's username to user1's username
    update_data = UserUpdate(username="user1")

    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(created_user2.id, update_data, db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Username already exists"


async def test_update_user_with_roles(db: AsyncSession):
    new_user = UserCreate(
        email="roleuser@example.com",
        username="roleuser",
        full_name="Role User",
        password="password123",
        role_names=["user"],
    )
    created_user = await user_service.create_user(new_user, db)

    # Update user to have admin role
    update_data = UserUpdate(role_names=["admin"])

    updated_user = await user_service.update_user(created_user.id, update_data, db)

    assert len(updated_user.roles) == 1
    assert updated_user.roles[0].name == "admin"


async def test_delete_user_success(db: AsyncSession):
    new_user = UserCreate(
        email="deleteuser@example.com",
        username="deleteuser",
        full_name="Delete User",
        password="password123",
    )
    created_user = await user_service.create_user(new_user, db)

    # Delete the user
    result = await user_service.delete_user(created_user.id, db)

    assert result == True

    # Verify user is deleted
    found_user = await user_service.get_user_by_id(created_user.id, db)
    assert found_user is None


async def test_delete_user_not_found(db: AsyncSession):
    non_existent_id = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await user_service.delete_user(non_existent_id, db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
