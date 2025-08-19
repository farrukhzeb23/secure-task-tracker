import pytest
import httpx


@pytest.mark.asyncio
async def test_register_user(client: httpx.AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "password": "testing123"
    }

    response = await client.post(url="/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "johndoe"


@pytest.mark.asyncio
async def test_register_user_email_already_exists(client: httpx.AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "password": "testing123"
    }

    # Creating the user first
    await client.post(url="/api/v1/auth/register", json=user_data)

    user_data["username"] = "Sara Williams"

    # Creating the same user again
    response = await client.post(url="/api/v1/auth/register", json=user_data)

    result = response.json()

    assert response.status_code == 400
    assert result["detail"] == "Email already exists choose another email"
