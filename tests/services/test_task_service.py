from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.task import TaskCreate, TaskUpdate
from app.services import task_service


async def test_create_task_service_works(db: AsyncSession, test_user):
    new_task = TaskCreate(title="Test Task", description="This is a test task")
    created_task = await task_service.create_task(new_task, test_user.id, db)

    assert created_task.title == "Test Task"
    assert created_task.description == "This is a test task"
    assert created_task.user_id == test_user.id
    assert created_task.is_completed is False


async def test_get_tasks_by_user(db: AsyncSession, test_user):
    # Create multiple tasks
    task1 = TaskCreate(title="Task 1", description="First task")
    task2 = TaskCreate(title="Task 2", description="Second task")

    await task_service.create_task(task1, test_user.id, db)
    await task_service.create_task(task2, test_user.id, db)

    tasks = await task_service.get_tasks_by_user(test_user.id, db)

    assert len(tasks) == 2
    assert any(task.title == "Task 1" for task in tasks)
    assert any(task.title == "Task 2" for task in tasks)


async def test_get_task_by_id(db: AsyncSession, test_user):
    new_task = TaskCreate(title="Test Task", description="Test description")
    created_task = await task_service.create_task(new_task, test_user.id, db)

    retrieved_task = await task_service.get_task_by_id(
        created_task.id, test_user.id, db
    )

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.title == "Test Task"


async def test_get_task_by_id_wrong_user_returns_none(db: AsyncSession, test_user):
    new_task = TaskCreate(title="Test Task", description="Test description")
    created_task = await task_service.create_task(new_task, test_user.id, db)

    wrong_user_id = uuid4()
    retrieved_task = await task_service.get_task_by_id(
        created_task.id, wrong_user_id, db
    )

    assert retrieved_task is None


async def test_update_task(db: AsyncSession, test_user):
    new_task = TaskCreate(title="Original Title", description="Original description")
    created_task = await task_service.create_task(new_task, test_user.id, db)

    task_update = TaskUpdate(
        title="Updated Title", description="Updated description", is_completed=True
    )

    updated_task = await task_service.update_task(
        created_task.id, task_update, test_user.id, db
    )

    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Updated description"
    assert updated_task.is_completed is True


async def test_update_nonexistent_task_raises_404(db: AsyncSession, test_user):
    fake_task_id = uuid4()
    task_update = TaskUpdate(title="Updated Title")

    with pytest.raises(Exception) as exc_info:
        await task_service.update_task(fake_task_id, task_update, test_user.id, db)

    assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


async def test_delete_task(db: AsyncSession, test_user):
    new_task = TaskCreate(title="Task to Delete", description="This will be deleted")
    created_task = await task_service.create_task(new_task, test_user.id, db)

    result = await task_service.delete_task(created_task.id, test_user.id, db)

    assert result is True

    # Verify task is deleted
    retrieved_task = await task_service.get_task_by_id(
        created_task.id, test_user.id, db
    )
    assert retrieved_task is None


async def test_delete_nonexistent_task_raises_404(db: AsyncSession, test_user):
    fake_task_id = uuid4()

    with pytest.raises(Exception) as exc_info:
        await task_service.delete_task(fake_task_id, test_user.id, db)

    assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


async def test_mark_task_completed(db: AsyncSession, test_user):
    new_task = TaskCreate(
        title="Task to Complete", description="This will be completed"
    )
    created_task = await task_service.create_task(new_task, test_user.id, db)

    assert created_task.is_completed is False

    completed_task = await task_service.mark_task_completed(
        created_task.id, test_user.id, db
    )

    assert completed_task.is_completed is True


async def test_mark_task_incomplete(db: AsyncSession, test_user):
    new_task = TaskCreate(
        title="Task to Mark Incomplete", description="This will be marked incomplete"
    )
    created_task = await task_service.create_task(new_task, test_user.id, db)

    # First complete it
    await task_service.mark_task_completed(created_task.id, test_user.id, db)

    # Then mark it incomplete
    incomplete_task = await task_service.mark_task_incomplete(
        created_task.id, test_user.id, db
    )

    assert incomplete_task.is_completed is False
