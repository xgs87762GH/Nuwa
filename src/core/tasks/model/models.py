from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, String, Integer, DateTime, Enum as SAEnum,
    ForeignKey, Text, JSON
)
from enum import Enum
from datetime import datetime, timezone
from typing import Any, List, Optional

from src.core.config.models import DbBase


class TaskStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    TIMEOUT = "timeout"


class Task(DbBase):
    __tablename__ = "tasks"

    task_id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)  # Changed to NOT NULL
    description = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Use timezone-aware datetime
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING)
    execution_plan = Column(JSON, nullable=True)  # Changed from Text to JSON
    result = Column(JSON, nullable=True)  # Changed from Text to JSON
    error = Column(Text, nullable=True)
    priority = Column(Integer, default=0)
    # timeout = Column(Integer, nullable=True)  # Timeout in seconds
    extra = Column(JSON, default=dict)  # Changed from Text to JSON

    # Relationship mapping
    steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan")


class TaskStep(DbBase):
    __tablename__ = "task_steps"

    step_id = Column(String(64), primary_key=True)
    task_id = Column(String(64), ForeignKey("tasks.task_id"), nullable=False, index=True)
    plugin_id = Column(String(64), nullable=False)
    plugin_name = Column(String(128), nullable=False)
    function_name = Column(String(128), nullable=False)
    params = Column(JSON, default=dict)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=0)

    # Relationship mapping
    task = relationship("Task", back_populates="steps")

    def set_started(self) -> None:
        """Mark step as started"""
        self.started_at = datetime.now(timezone.utc)
        self.status = TaskStatus.RUNNING

    def set_finished(self, success: bool, result: Any = None, error: str = None) -> None:
        """Mark step as finished"""
        self.finished_at = datetime.now(timezone.utc)
        self.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
        self.result = result
        self.error = error