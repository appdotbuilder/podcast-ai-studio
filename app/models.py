from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    """A task in the to-do list with title and completion status."""

    __tablename__ = "tasks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(SQLModel, table=False):
    """Schema for creating a new task."""

    title: str = Field(max_length=200, min_length=1)


class TaskUpdate(SQLModel, table=False):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(default=None, max_length=200, min_length=1)
    completed: Optional[bool] = Field(default=None)
