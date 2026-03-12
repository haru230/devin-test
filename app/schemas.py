"""
[Architect + Coder] Pydantic schemas for request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoCreate(BaseModel):
    """Schema for creating a new Todo item."""

    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: str | None = Field(None, description="Optional description")
    completed: bool = Field(False, description="Completion status")


class TodoUpdate(BaseModel):
    """Schema for updating an existing Todo item."""

    title: str | None = Field(None, min_length=1, max_length=200, description="Todo title")
    description: str | None = Field(None, description="Optional description")
    completed: bool | None = Field(None, description="Completion status")


class TodoResponse(BaseModel):
    """Schema for Todo item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
