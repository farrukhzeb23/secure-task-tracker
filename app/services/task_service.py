from typing import Optional, Sequence, Tuple
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(task: TaskCreate, user_id: UUID, db: AsyncSession) -> Task:
    try:
        db_task = Task(title=task.title, description=task.description, user_id=user_id)
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating task: {str(error)}"
        )


async def get_tasks_by_user(
    user_id: UUID, db: AsyncSession, page: int = 1, size: int = 10
) -> Tuple[Sequence[Task], int]:
    # Calculate offset
    offset = (page - 1) * size

    # Get total count
    count_result = await db.execute(
        select(func.count(Task.id)).where(Task.user_id == user_id)
    )
    total_count = count_result.scalar() or 0

    # Get paginated tasks
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    tasks = result.scalars().all()

    return tasks, total_count


async def get_task_by_id(task_id: UUID, user_id: UUID, db: AsyncSession) -> Task | None:
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def update_task(
    task_id: UUID, task_update: TaskUpdate, user_id: UUID, db: AsyncSession
) -> Task | None:
    db_task = await get_task_by_id(task_id, user_id, db)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        await db.commit()
        await db.refresh(db_task)
        return db_task
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating task: {str(error)}"
        )


async def delete_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    db_task = await get_task_by_id(task_id, user_id, db)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        await db.delete(db_task)
        await db.commit()
        return True
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting task: {str(error)}"
        )


async def mark_task_completed(
    task_id: UUID, user_id: UUID, db: AsyncSession
) -> Task | None:
    task_update = TaskUpdate(is_completed=True)
    return await update_task(task_id, task_update, user_id, db)


async def mark_task_incomplete(
    task_id: UUID, user_id: UUID, db: AsyncSession
) -> Task | None:
    task_update = TaskUpdate(is_completed=False)
    return await update_task(task_id, task_update, user_id, db)
