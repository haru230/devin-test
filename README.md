# Todo List Web App

A simple **Todo List REST API** built with **FastAPI** and **SQLite**.

## Architecture

This project was designed using a **3-persona parallel workflow**:

| Persona | Role |
|---------|------|
| **Architect** | Designed project structure, API contracts, and DB schema |
| **Coder** | Implemented all application code (models, CRUD, routes) |
| **Tester** | Wrote comprehensive pytest test suite |

### Project Structure

```
app/
├── __init__.py
├── main.py        # FastAPI entry point, CORS, lifespan
├── database.py    # SQLite + SQLAlchemy engine & session
├── models.py      # SQLAlchemy ORM model (Todo)
├── schemas.py     # Pydantic request/response schemas
└── crud.py        # CRUD helper functions
tests/
├── __init__.py
└── test_todos.py  # Full API test suite
requirements.txt
README.md
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/todos` | List all todos (query: `skip`, `limit`, `completed`) |
| `GET` | `/todos/{id}` | Get a specific todo |
| `POST` | `/todos` | Create a new todo |
| `PUT` | `/todos/{id}` | Update a todo (partial update supported) |
| `DELETE` | `/todos/{id}` | Delete a todo |

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**.  
Interactive docs (Swagger UI) at **http://localhost:8000/docs**.

### 3. Run tests

```bash
pytest tests/ -v
```

## Tech Stack

- **Python 3.12+**
- **FastAPI** – Modern async web framework
- **SQLAlchemy 2.0** – ORM with mapped column syntax
- **SQLite** – Lightweight embedded database
- **Pydantic v2** – Data validation & serialization
- **pytest + httpx** – Testing
