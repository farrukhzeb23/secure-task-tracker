from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_admin
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.schemas.user import User
from app.services.task_service import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks_by_user,
    mark_task_completed,
    mark_task_incomplete,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_user_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_task(task, current_user.id, db)


@router.get("/", response_model=List[Task])
async def get_user_tasks(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await get_tasks_by_user(current_user.id, db)


@router.get("/users/{user_id}", response_model=List[Task])
async def admin_get_user_tasks(
    user_id: UUID,
    _: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    return await get_tasks_by_user(user_id, db)


@router.get("/{task_id}", response_model=Task)
async def get_user_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(task_id, current_user.id, db)
    if not task:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_user_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_task(task_id, task_update, current_user.id, db)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_task(task_id, current_user.id, db)


@router.patch("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await mark_task_completed(task_id, current_user.id, db)


@router.patch("/{task_id}/incomplete", response_model=Task)
async def incomplete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await mark_task_incomplete(task_id, current_user.id, db)
