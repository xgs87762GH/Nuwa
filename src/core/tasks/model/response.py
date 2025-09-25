from datetime import datetime
from typing import List, Optional, Any, Dict, Literal

from pydantic import Field, BaseModel

from src.core.tasks.model.models import TaskStatus


class TaskStepResponse(BaseModel):
    step_id: str
    plugin_id: str
    plugin_name: str
    function_name: str
    params: dict
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 0

    class Config:
        orm_mode = True


class StepExecutionResult(BaseModel):
    step_id: Optional[str] = None
    plugin_id: str
    plugin_name: Optional[str] = None
    function_name: str
    params: dict = Field(default_factory=dict)
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    class Config:
        orm_mode = True


class TaskResponse(BaseModel):
    task_id: str
    user_id: str
    description: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    steps: List[TaskStepResponse] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class TaskDetailResponse(TaskResponse):
    scheduled_at: Optional[datetime] = None
    execution_plan: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    priority: int = 0
    timeout: Optional[int] = None


class PaginatedTaskResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[TaskResponse]


class SortField(BaseModel):
    """Single sorting field"""
    field: Literal[
        "created_at", "updated_at", "priority", "task_id", "description"
    ] = Field(..., description="Column name for sorting")
    order: Literal["asc", "desc"] = Field("desc", description="asc or desc")


class TaskQuery(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    task_id: Optional[str] = Field(None, description="Task ID")
    description: Optional[str] = Field(None, description="Task description (fuzzy search)")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    sorts: List[SortField] = Field(
        default_factory=lambda: [
            SortField(field="created_at", order="desc"),
            SortField(field="priority", order="desc"),
        ],
        description="Custom sorting, multi-field supported",
    )
