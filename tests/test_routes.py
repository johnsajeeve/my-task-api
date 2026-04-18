import pytest
from app.models import Task

def test_create_task(client):
    response = client.post(
        "/tasks", json={"description":"Get weather for london", "priority": "high"}

    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Get weather for london"
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert "id" in data

def test_get_all_tasks(client):
    client.post("/tasks", json={"description": "Test task","priority": "high"})

    response= client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data)>=1
    assert data[0]["description"] == "Test task"

def test_get_single_task(client):
    create_response = client.post(
        "/tasks", json={"description":"single task", "priority": "medium"}

    )
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["description"] == "single task"

def test_update_task(client):
    create_response = client.post(
        "/tasks", json={"description":"original", "priority": "high"}

    )
    task_id = create_response.json()["id"]

    response= client.put(
         f"/tasks/{task_id}",
        json={"description": "Updated", "priority": "low", "status": "completed"}
 
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated"
    assert data["priority"] == "low"

def test_delete_task(client):
    create_response = client.post(
        "/tasks",
        json={"description": "To delete", "priority": "high"}
    )
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_create_task_missing_description(client):
    response = client.post(
        "/tasks", json={"priority":"high"}

    )
    assert response.status_code == 422

def test_create_task_invalid(client):
    response = client.post(
        "/tasks", json={"description":"Test", "priority":"invalid"}

    )
    assert response.status_code == 422

def test_task_fields(client):
    """Test task response includes all required fields"""
    response = client.post(
        "/tasks",
        json={"description": "Test", "priority": "high"}
    )
    
    data = response.json()
    required_fields = ["id", "description", "priority", "status", "result"]
    
    for field in required_fields:
        assert field in data, f"Missing field: {field}"