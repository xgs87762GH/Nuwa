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
    timeout = Column(Integer, nullable=True)  # Timeout in seconds
    extra = Column(JSON, default=dict)  # Changed from Text to JSON

    # Relationship mapping
    steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan")

    def add_step(self, step: "TaskStep") -> None:
        """Add a step to the task"""
        self.steps.append(step)

    def get_step(self, step_id: str) -> Optional["TaskStep"]:
        """Get a specific step by ID"""
        return next((step for step in self.steps if step.step_id == step_id), None)

    def get_steps_by_status(self, status: TaskStatus) -> List["TaskStep"]:
        """Get all steps with a specific status"""
        return [step for step in self.steps if step.status == status]

    def update_status(self) -> None:
        """Update task status based on step statuses"""
        if not self.steps:
            return

        if any(step.status == TaskStatus.FAILED for step in self.steps):
            self.status = TaskStatus.FAILED
        elif all(step.status == TaskStatus.SUCCESS for step in self.steps):
            self.status = TaskStatus.SUCCESS
        elif any(step.status == TaskStatus.RUNNING for step in self.steps):
            self.status = TaskStatus.RUNNING
        elif any(step.status == TaskStatus.CANCELLED for step in self.steps):
            self.status = TaskStatus.CANCELLED
        elif any(step.status == TaskStatus.TIMEOUT for step in self.steps):
            self.status = TaskStatus.TIMEOUT
        else:
            self.status = TaskStatus.SCHEDULED

    def set_started(self) -> None:
        """Mark task as started"""
        self.started_at = datetime.now(timezone.utc)
        self.status = TaskStatus.RUNNING

    def set_finished(self, success: bool, result: Any = None, error: str = None) -> None:
        """Mark task as finished"""
        self.finished_at = datetime.now(timezone.utc)
        self.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
        self.result = result
        self.error = error


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