import pytest
import httpx
# from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user(client: httpx.AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "password": "testing123"
    }

    response = await client.post(url="/api/v1/users/", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "johndoe"


@pytest.mark.asyncio
async def test_create_user_email_already_exists(client: httpx.AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "password": "testing123"
    }

    # Creating the user first
    await client.post(url="/api/v1/users/", json=user_data)

    user_data["username"] = "Sara Williams"

    # Creating the same user again
    response = await client.post(url="/api/v1/users/", json=user_data)

    result = response.json()

    assert response.status_code == 400
    assert result["detail"] == "Email already exists choose another email"


@pytest.mark.asyncio
async def test_get_all_users(client: httpx.AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "password": "testing123"
    }

    # Creating the user first
    await client.post(url="/api/v1/users/", json=user_data)

    response = await client.get(url="/api/v1/users/")
    result = response.json()
    assert response.status_code == 200
    assert len(result) > 0
