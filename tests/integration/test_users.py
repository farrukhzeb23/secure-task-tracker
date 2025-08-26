import pytest
import httpx


@pytest.mark.asyncio
async def test_get_all_users(client: httpx.AsyncClient, test_admin_access_token):
    response = await client.get(
        "/api/v1/users/",
        headers={
            "Authorization": f"Bearer {test_admin_access_token}"
        }
    )
    result = response.json()
    assert response.status_code == 200
    assert len(result) > 0


@pytest.mark.asyncio
async def test_read_users_me(client: httpx.AsyncClient, test_access_token):
    response = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {test_access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"
