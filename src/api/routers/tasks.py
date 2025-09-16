from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.api.dependencies import TaskServiceDep
from src.api.models import TaskCreateAPIResponse, TaskResult, APIResponse
from src.core.config import AppConfig
from src.core.config.logger import get_logger

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
        task_service: TaskServiceDep
) -> TaskCreateAPIResponse:
    """Create task based on user input"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting app configuration: {app_config.name}")

    result = await task_service.create_task_from_input(request.user_input)

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
