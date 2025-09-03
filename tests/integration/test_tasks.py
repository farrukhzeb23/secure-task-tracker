from uuid import uuid4

import httpx
import pytest

from app.models.task import Task


class TestTasksAPI:

    async def test_create_task(self, client: httpx.AsyncClient, test_access_token):
        headers = {"Authorization": f"Bearer {test_access_token}"}
        task_data = {"title": "Test Task", "description": "This is a test task"}

        response = await client.post("/api/v1/tasks/", json=task_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "This is a test task"
        assert data["is_completed"] is False
        assert "id" in data
        assert "created_at" in data

    async def test_create_task_unauthorized(self, client: httpx.AsyncClient):
        task_data = {"title": "Test Task", "description": "This is a test task"}

        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 401

    async def test_get_user_tasks(self, client: httpx.AsyncClient, test_access_token):
        headers = {"Authorization": f"Bearer {test_access_token}"}

        # First create some tasks
        task1_data = {"title": "Task 1", "description": "First task"}
        task2_data = {"title": "Task 2", "description": "Second task"}

        await client.post("/api/v1/tasks/", json=task1_data, headers=headers)
        await client.post("/api/v1/tasks/", json=task2_data, headers=headers)

        # Get all tasks
        response = await client.get("/api/v1/tasks/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(task["title"] == "Task 1" for task in data)
        assert any(task["title"] == "Task 2" for task in data)

    async def test_get_user_tasks_unauthorized(self, client: httpx.AsyncClient):
        response = await client.get("/api/v1/tasks/")
        assert response.status_code == 401

    async def test_get_specific_task(
        self, client: httpx.AsyncClient, test_access_token
    ):
        headers = {"Authorization": f"Bearer {test_access_token}"}

        # Create a task
        task_data = {"title": "Specific Task", "description": "This is a specific task"}
        create_response = await client.post(
            "/api/v1/tasks/", json=task_data, headers=headers
        )
        created_task = create_response.json()

        # Get the specific task
        response = await client.get(
            f"/api/v1/tasks/{created_task['id']}", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_task["id"]
        assert data["title"] == "Specific Task"

    async def test_get_nonexistent_task_returns_404(
        self, client: httpx.AsyncClient, test_access_token
    ):
        headers = {"Authorization": f"Bearer {test_access_token}"}
        fake_id = str(uuid4())

        response = await client.get(f"/api/v1/tasks/{fake_id}", headers=headers)

        assert response.status_code == 404

    async def test_update_task(self, client: httpx.AsyncClient, test_access_token):
        headers = {"Authorization": f"Bearer {test_access_token}"}

        # Create a task
        task_data = {"title": "Original Title", "description": "Original description"}
        create_response = await client.post(
            "/api/v1/tasks/", json=task_data, headers=headers
        )
        created_task = create_response.json()

        # Update the task
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "is_completed": True,
        }

        response = await client.put(
            f"/api/v1/tasks/{created_task['id']}", json=update_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["is_completed"] is True

    async def test_update_nonexistent_task_returns_404(
        self, client: httpx.AsyncClient, test_access_token
    ):
        headers = {"Authorization": f"Bearer {test_access_token}"}
        fake_id = str(uuid4())
        update_data = {"title": "Updated Title"}

        response = await client.put(
            f"/api/v1/tasks/{fake_id}", json=update_data, headers=headers
        )

        assert response.status_code == 404

    async def test_delete_task(self, client: httpx.AsyncClient, test_access_token):
        headers = {"Authorization": f"Bearer {test_access_token}"}

        # Create a task
        task_data = {"title": "Task to Delete", "description": "This will be deleted"}
        create_response = await client.post(
            "/api/v1/tasks/", json=task_data, headers=headers
        )
        created_task = create_response.json()

        # Delete the task
        response = await client.delete(
            f"/api/v1/tasks/{created_task['id']}", headers=headers
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(
            f"/api/v1/tasks/{created_task['id']}", headers=headers
        )
        assert get_response.status_code == 404

    async def test_delete_nonexistent_task_returns_404(
        self, client: httpx.AsyncClient, test_access_token
    ):
        headers = {"Authorization": f"Bearer {test_access_token}"}
        fake_id = str(uuid4())

        response = await client.delete(f"/api/v1/tasks/{fake_id}", headers=headers)

        assert response.status_code == 404

    async def test_complete_task(self, client: httpx.AsyncClient, test_access_token):
        headers = {"Authorization": f"Bearer {test_access_token}"}

        # Create a task
        task_data = {
            "title": "Task to Complete",
            "description": "This will be completed",
        }
        create_response = await client.post(
            "/api/v1/tasks/", json=task_data, headers=headers
        )
        created_task = create_response.json()

        assert created_task["is_completed"] is False

        # Complete the task
        response = await client.patch(
            f"/api/v1/tasks/{created_task['id']}/complete", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True

    async def test_mark_task_incomplete(
        self, client: httpx.AsyncClient, test_access_token
    ):
        headers = {"Authorization": f"Bearer {test_access_token}"}

        # Create and complete a task
        task_data = {
            "title": "Task to Mark Incomplete",
            "description": "This will be marked incomplete",
        }
        create_response = await client.post(
            "/api/v1/tasks/", json=task_data, headers=headers
        )
        created_task = create_response.json()

        # Complete it first
        await client.patch(
            f"/api/v1/tasks/{created_task['id']}/complete", headers=headers
        )

        # Mark it incomplete
        response = await client.patch(
            f"/api/v1/tasks/{created_task['id']}/incomplete", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is False

    async def test_tasks_are_user_specific(
        self, client: httpx.AsyncClient, test_access_token, test_admin_access_token
    ):
        # Create task with regular user
        user_headers = {"Authorization": f"Bearer {test_access_token}"}
        task_data = {
            "title": "User Task",
            "description": "This belongs to regular user",
        }
        user_response = await client.post(
            "/api/v1/tasks/", json=task_data, headers=user_headers
        )
        user_task = user_response.json()

        # Try to access user's task with admin user
        admin_headers = {"Authorization": f"Bearer {test_admin_access_token}"}
        admin_response = await client.get(
            f"/api/v1/tasks/{user_task['id']}", headers=admin_headers
        )

        # Admin should not be able to access user's task
        assert admin_response.status_code == 404

    async def test_user_can_only_see_their_own_tasks(
        self, client: httpx.AsyncClient, test_access_token, test_admin_access_token
    ):
        # Create task with regular user
        user_headers = {"Authorization": f"Bearer {test_access_token}"}
        await client.post(
            "/api/v1/tasks/", json={"title": "User Task"}, headers=user_headers
        )

        # Create task with admin user
        admin_headers = {"Authorization": f"Bearer {test_admin_access_token}"}
        await client.post(
            "/api/v1/tasks/", json={"title": "Admin Task"}, headers=admin_headers
        )

        # User should only see their own task
        user_tasks_response = await client.get("/api/v1/tasks/", headers=user_headers)
        user_tasks = user_tasks_response.json()
        assert len(user_tasks) == 1
        assert user_tasks[0]["title"] == "User Task"

        # Admin should only see their own task
        admin_tasks_response = await client.get("/api/v1/tasks/", headers=admin_headers)
        admin_tasks = admin_tasks_response.json()
        assert len(admin_tasks) == 1
        assert admin_tasks[0]["title"] == "Admin Task"
