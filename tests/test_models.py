import pytest
from app.models import Task
from uuid import uuid4


def test_task_creation(db_session):
    """Test creating a Task model"""
    task = Task(
        id=str(uuid4()),
        description="Test task",
        priority="high",
        status="pending",
        result=None
    )
    
    db_session.add(task)
    db_session.commit()
    
    # Verify it was saved
    saved_task = db_session.query(Task).filter(Task.description == "Test task").first()
    assert saved_task is not None
    assert saved_task.description == "Test task"
    assert saved_task.priority == "high"
    assert saved_task.status == "pending"


def test_task_status_update(db_session):
    """Test updating task status"""
    task = Task(
        id=str(uuid4()),
        description="Update test",
        priority="medium",
        status="pending",
        result=None
    )
    
    db_session.add(task)
    db_session.commit()
    
    # Update status
    task.status = "completed"
    task.result = "Weather data: 20°C"
    db_session.commit()
    
    # Verify update
    updated_task = db_session.query(Task).filter(Task.id == task.id).first()
    assert updated_task.status == "completed"
    assert updated_task.result == "Weather data: 20°C"


def test_task_default_values(db_session):
    """Test task default values"""
    task = Task(
        id=str(uuid4()),
        description="Defaults test",
        priority="high"
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    assert task.status == "pending"
    assert task.result is None
