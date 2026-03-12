"""
[Coder] CRUD operations for the Todo application.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


def get_todos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    completed: bool | None = None,
) -> list[Todo]:
    """Retrieve a list of todos with optional filtering."""
    query = db.query(Todo)
    if completed is not None:
        query = query.filter(Todo.completed == completed)
    return query.order_by(Todo.created_at.desc()).offset(skip).limit(limit).all()


def get_todo(db: Session, todo_id: int) -> Todo | None:
    """Retrieve a single todo by ID."""
    return db.query(Todo).filter(Todo.id == todo_id).first()


def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo item."""
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: TodoUpdate) -> Todo | None:
    """Update an existing todo item."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        return None

    update_data = todo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db_todo.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo item. Returns True if deleted, False if not found."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        return False
    db.delete(db_todo)
    db.commit()
    return True
