import httpx
import pytest


@pytest.mark.asyncio
async def test_register_user(client: httpx.AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "password": "testing123",
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
        "password": "testing123",
    }

    # Creating the user first
    await client.post(url="/api/v1/auth/register", json=user_data)

    user_data["username"] = "Sara Williams"

    # Creating the same user again
    response = await client.post(url="/api/v1/auth/register", json=user_data)

    result = response.json()

    assert response.status_code == 400
    assert result["detail"] == "Email already exists choose another email"


@pytest.mark.asyncio
async def test_login_for_access_token(client: httpx.AsyncClient, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@example.com", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token(client: httpx.AsyncClient, test_refresh_token):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": test_refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: httpx.AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wronguser", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User with email wronguser does not exists"


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: httpx.AsyncClient):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"
