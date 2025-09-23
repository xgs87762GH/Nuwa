from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.api.dependencies import TaskServiceDep, IntelligentPluginRouterDep
from src.api.models import TaskCreateAPIResponse, TaskResult, APIResponse
from src.core.config import AppConfig
from src.core.config.logger import get_logger
from src.core.tasks.model.models import TaskStatus
from src.core.tasks.model.response import TaskQuery, PaginatedTaskResponse, TaskDetailResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])
LOGGER = get_logger(__name__)


class CreateTaskRequest(BaseModel):
    """Create task request model"""
    user_input: str


@router.post(
    "/",
    summary="Create task",
    description="Create a task based on user input using IntelligentPluginRouter",
    response_model=TaskCreateAPIResponse
)
async def create_task_api(
        request: CreateTaskRequest,
        req: Request,
        task_service: TaskServiceDep,
        intelligent_plugin_router: IntelligentPluginRouterDep
) -> TaskCreateAPIResponse:
    """Create task based on user input"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting app configuration: {app_config.name}")

    result = await task_service.create_task_from_input(
        user_input=request.user_input,
        router=intelligent_plugin_router
    )

    if result.get("success") is False:
        return APIResponse.error(
            message=result.get("error", "Failed to create task")
        )

    # Convert result to structured format
    task_result = TaskResult(
        task_id=result.get("task_id", ""),
        status=result.get("status", "created"),
        created_at=result.get("created_at", ""),
        user_input=request.user_input,
        processed_by=result.get("processed_by", "unknown")
    )

    return APIResponse.ok(data=task_result)


from fastapi import Query


@router.get('', response_model=APIResponse[PaginatedTaskResponse])
async def list(
        req: Request, task_service: TaskServiceDep,
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, le=100, description="每页数量"),
        task_id: Optional[str] = Query(None, description="任务ID"),
        description: Optional[str] = Query(None, description="任务描述"),
        status: Optional[TaskStatus] = Query(None, description="任务状态")
) -> APIResponse[PaginatedTaskResponse]:
    """List tasks with optional filters"""
    query = TaskQuery(
        page=page,
        size=size,
        task_id=task_id,
        description=description,
        status=status
    )
    tasks = await task_service.query_tasks(query)
    return APIResponse.ok(data=tasks)


@router.get('/{task_id}', response_model=APIResponse[TaskDetailResponse])
async def detail(task_id: str, task_service: TaskServiceDep) -> APIResponse[TaskDetailResponse]:
    """Get detailed information of a single task, including steps and plan/result fields."""
    detail = await task_service.get_task_detail(task_id)
    if detail is None:
        return APIResponse.error(message="Task not found")
    return APIResponse.ok(data=detail)


@router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(task_id: str, task_service: TaskServiceDep) -> APIResponse[None]:
    """Delete a task"""
    await task_service.del_task(task_id)
    return APIResponse.ok()
