"""
[Tester] Comprehensive test suite for the Todo List API.
Uses pytest + httpx (via TestClient) to test all CRUD endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# ---------------------------------------------------------------------------
# Test database setup – use in-memory SQLite for isolation
# ---------------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """Provide a TestClient instance."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _create_todo(client: TestClient, title: str = "Test Todo", **kwargs) -> dict:
    payload = {"title": title, **kwargs}
    response = client.post("/todos", json=payload)
    assert response.status_code == 201
    return response.json()


# ===========================================================================
# 1. Root / Health-check
# ===========================================================================
class TestRoot:
    def test_root_endpoint(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data


# ===========================================================================
# 2. CREATE – POST /todos
# ===========================================================================
class TestCreateTodo:
    def test_create_todo_minimal(self, client: TestClient):
        """Create a todo with only the required title field."""
        response = client.post("/todos", json={"title": "Buy groceries"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] is None
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_todo_full(self, client: TestClient):
        """Create a todo with all fields populated."""
        payload = {
            "title": "Learn FastAPI",
            "description": "Read the official docs",
            "completed": True,
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Learn FastAPI"
        assert data["description"] == "Read the official docs"
        assert data["completed"] is True

    def test_create_todo_empty_title_rejected(self, client: TestClient):
        """Title must not be empty."""
        response = client.post("/todos", json={"title": ""})
        assert response.status_code == 422

    def test_create_todo_missing_title_rejected(self, client: TestClient):
        """Title is a required field."""
        response = client.post("/todos", json={})
        assert response.status_code == 422

    def test_create_todo_title_too_long(self, client: TestClient):
        """Title must be <= 200 characters."""
        response = client.post("/todos", json={"title": "x" * 201})
        assert response.status_code == 422


# ===========================================================================
# 3. READ – GET /todos & GET /todos/{id}
# ===========================================================================
class TestReadTodos:
    def test_list_todos_empty(self, client: TestClient):
        response = client.get("/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_todos_returns_items(self, client: TestClient):
        _create_todo(client, "Item 1")
        _create_todo(client, "Item 2")
        response = client.get("/todos")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_todos_filter_completed(self, client: TestClient):
        _create_todo(client, "Done task", completed=True)
        _create_todo(client, "Pending task", completed=False)

        completed = client.get("/todos", params={"completed": True}).json()
        assert len(completed) == 1
        assert completed[0]["title"] == "Done task"

        pending = client.get("/todos", params={"completed": False}).json()
        assert len(pending) == 1
        assert pending[0]["title"] == "Pending task"

    def test_list_todos_pagination(self, client: TestClient):
        for i in range(5):
            _create_todo(client, f"Item {i}")
        response = client.get("/todos", params={"skip": 2, "limit": 2})
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_todo_by_id(self, client: TestClient):
        created = _create_todo(client, "Specific Todo")
        response = client.get(f"/todos/{created['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == "Specific Todo"

    def test_get_todo_not_found(self, client: TestClient):
        response = client.get("/todos/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"


# ===========================================================================
# 4. UPDATE – PUT /todos/{id}
# ===========================================================================
class TestUpdateTodo:
    def test_update_title(self, client: TestClient):
        created = _create_todo(client, "Old Title")
        response = client.put(
            f"/todos/{created['id']}", json={"title": "New Title"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "New Title"

    def test_update_completed(self, client: TestClient):
        created = _create_todo(client, "Task")
        response = client.put(
            f"/todos/{created['id']}", json={"completed": True}
        )
        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_update_description(self, client: TestClient):
        created = _create_todo(client, "Task")
        response = client.put(
            f"/todos/{created['id']}", json={"description": "New desc"}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "New desc"

    def test_partial_update_preserves_other_fields(self, client: TestClient):
        created = _create_todo(
            client, "Task", description="Original", completed=False
        )
        response = client.put(
            f"/todos/{created['id']}", json={"completed": True}
        )
        data = response.json()
        assert data["title"] == "Task"
        assert data["description"] == "Original"
        assert data["completed"] is True

    def test_update_not_found(self, client: TestClient):
        response = client.put("/todos/9999", json={"title": "Nope"})
        assert response.status_code == 404


# ===========================================================================
# 5. DELETE – DELETE /todos/{id}
# ===========================================================================
class TestDeleteTodo:
    def test_delete_todo(self, client: TestClient):
        created = _create_todo(client, "To Delete")
        response = client.delete(f"/todos/{created['id']}")
        assert response.status_code == 204

        # Confirm it's gone
        response = client.get(f"/todos/{created['id']}")
        assert response.status_code == 404

    def test_delete_not_found(self, client: TestClient):
        response = client.delete("/todos/9999")
        assert response.status_code == 404
