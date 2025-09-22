from datetime import datetime

from pydantic import Field, BaseModel
from typing import List, Optional, Any

from src.core.tasks.model.models import TaskStatus


# 用于 API 响应的纯 Pydantic 模型
class TaskStepResponse(BaseModel):
    step_id: str
    plugin_id: str
    plugin_name: str
    function_name: str
    params: dict
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None

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
    steps: List[TaskStepResponse] = []

    class Config:
        orm_mode = True

# 分页响应模型
class PaginatedTaskResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[TaskResponse]

# 查询参数模型
class TaskQuery(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    task_id: Optional[str] = Field(None, description="任务ID")
    description: Optional[str] = Field(None, description="任务描述（模糊查询）")
    status: Optional[TaskStatus] = Field(None, description="任务状态")