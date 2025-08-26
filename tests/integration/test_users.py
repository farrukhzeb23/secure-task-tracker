import pytest
import httpx


@pytest.mark.asyncio
async def test_get_all_users(client: httpx.AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "password": "testing123"
    }

    # Creating the user first
    await client.post(url="/api/v1/auth/register", json=user_data)

    response = await client.get(url="/api/v1/users/")
    result = response.json()
    assert response.status_code == 200
    assert len(result) > 0


@pytest.mark.asyncio
async def test_read_users_me(client: httpx.AsyncClient, test_access_token):
    response = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {test_access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"
