from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.models import Task
from app.tasks import process_task
from sqlalchemy.orm import Session
import uuid
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Priority enum for validation
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskCreate(BaseModel):
    description: str
    priority: PriorityEnum = "medium"

class TaskUpdate(BaseModel):
    description: str = None
    priority: PriorityEnum = None
    status: str = None
    result: str = None

router = APIRouter()


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            description=task_data.description,
            priority=task_data.priority,
            status="pending",
            result="None"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        process_task.delay(task_id)

        logger.info(f"Task created : {task_id} - {task_data.description[:50]}")

        return task
    except Exception as e:
        db.rollback()
        logger.error(f"failed to create task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to create task"
        )


@router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        logger.warning(f"task not found: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task with id '{task_id}' not found"
        )
    logger.info(f"retrieved task: {task_id}")
    return task


@router.get("/tasks", status_code=status.HTTP_200_OK)
def list_all_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).all()
        logger.info(f"retrieved {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"failed to retieve tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to retrieve tasks"
        )


@router.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def update_task(task_id: str, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        logger.warning(f"task not found for updates: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task with id '{task_id}' not found"
        )
    try:
        # Update fields that are provided
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.priority is not None:
            task.priority = task_update.priority
        if task_update.status is not None:
            task.status = task_update.status
        if task_update.result is not None:
            task.result = task_update.result

        db.commit()
        db.refresh(task)

        logger.info(f"task updated:{task_id}")
        return task
    except Exception as e:
        db.rollback()
        logger.error(f"filed to update task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed tp update task"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        logger.warning(f"task not found for deletion: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task with id '{task_id}' not found"
        )

    try:
        db.delete(task)
        db.commit()
        logger.info(f"task deleted: {task_id}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"failed to delete task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to delete task"
        )