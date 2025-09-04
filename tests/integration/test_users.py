from uuid import uuid4

import httpx
import pytest


@pytest.mark.asyncio
async def test_get_all_users(client: httpx.AsyncClient, test_admin_access_token):
    response = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {test_admin_access_token}"}
    )
    result = response.json()
    assert response.status_code == 200
    assert len(result) > 0


@pytest.mark.asyncio
async def test_read_users_me(client: httpx.AsyncClient, test_access_token):
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


@pytest.mark.asyncio
async def test_get_user_by_id_as_admin(
    client: httpx.AsyncClient, test_admin_access_token, test_user
):
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["email"] == "testuser@example.com"
    assert result["username"] == "test.user"
    assert result["full_name"] == "test user"


@pytest.mark.asyncio
async def test_get_user_by_id_as_regular_user_forbidden(
    client: httpx.AsyncClient, test_access_token, test_user
):
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    client: httpx.AsyncClient, test_admin_access_token
):
    non_existent_id = uuid4()
    response = await client.get(
        f"/api/v1/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_update_user_as_admin(
    client: httpx.AsyncClient, test_admin_access_token, test_user
):
    update_data = {"full_name": "Updated Test User", "is_active": False}

    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["full_name"] == "Updated Test User"
    assert result["is_active"] == False
    assert result["email"] == "testuser@example.com"  # unchanged


@pytest.mark.asyncio
async def test_update_user_as_regular_user_forbidden(
    client: httpx.AsyncClient, test_access_token, test_user
):
    update_data = {"full_name": "Updated Test User"}

    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_user_not_found(
    client: httpx.AsyncClient, test_admin_access_token
):
    non_existent_id = uuid4()
    update_data = {"full_name": "Updated Name"}

    response = await client.put(
        f"/api/v1/users/{non_existent_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_update_user_email_conflict(
    client: httpx.AsyncClient, test_admin_access_token, test_user, test_admin_user
):
    # Try to update test_user's email to admin's email
    update_data = {"email": "admin@example.com"}

    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.asyncio
async def test_update_user_username_conflict(
    client: httpx.AsyncClient, test_admin_access_token, test_user, test_admin_user
):
    # Try to update test_user's username to admin's username
    update_data = {"username": "admin.user"}

    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_update_user_roles(
    client: httpx.AsyncClient, test_admin_access_token, test_user
):
    # Update user to have admin role
    update_data = {"role_names": ["admin"]}

    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["roles"]) == 1
    assert result["roles"][0]["name"] == "admin"


@pytest.mark.asyncio
async def test_delete_user_as_admin(
    client: httpx.AsyncClient, test_admin_access_token, test_user
):
    response = await client.delete(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 204

    # Verify user is deleted by trying to get it
    get_response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_as_regular_user_forbidden(
    client: httpx.AsyncClient, test_access_token, test_admin_user
):
    response = await client.delete(
        f"/api/v1/users/{test_admin_user.id}",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_not_found(
    client: httpx.AsyncClient, test_admin_access_token
):
    non_existent_id = uuid4()
    response = await client.delete(
        f"/api/v1/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {test_admin_access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_admin_endpoints_require_authentication(
    client: httpx.AsyncClient, test_user
):
    # Test get user by id without auth
    response = await client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 401

    # Test update user without auth
    response = await client.put(
        f"/api/v1/users/{test_user.id}", json={"full_name": "Updated"}
    )
    assert response.status_code == 401

    # Test delete user without auth
    response = await client.delete(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 401
