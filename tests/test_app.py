import pytest

from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])


def test_index(client):
    """Test that the task tracker page renders successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Test that tasks are returned with a default priority."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


def test_add_task_success(client):
    """Test creating a task without priority defaults to Medium."""
    response = client.post('/api/tasks', json={"title": "Test new task"})
    assert response.status_code == 201
    assert response.get_json()['title'] == "Test new task"
    assert response.get_json()['priority'] == "Medium"

    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 3
    assert data[-1]['priority'] == "Medium"


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_valid_priorities(client, priority):
    """Test creating tasks with each supported priority."""
    response = client.post(
        '/api/tasks',
        json={"title": f"{priority} task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == priority


@pytest.mark.parametrize('priority', ['low', 'Urgent', '', None])
def test_add_task_invalid_priority(client, priority):
    """Test that unsupported priorities are rejected."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid priority task", "priority": priority}
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == (
        "Priority must be Low, Medium, or High"
    )


def test_add_task_missing_title(client):
    """Test that creating a task without a title fails."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()

    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_delete_task(client):
    """Test deleting an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200

    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
