import httpx
import pytest


@pytest.mark.asyncio
async def test_admin_access(client: httpx.AsyncClient, test_admin_access_token):

    response = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {test_admin_access_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_forbidden_access(client: httpx.AsyncClient, test_access_token):
    response = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code == 403
