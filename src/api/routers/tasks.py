from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.api.dependencies import TaskServiceDep
from src.api.models import APIResponse
from src.core.config import AppConfig
from src.core.config.logger import get_logger

router = APIRouter(prefix="/tasks", tags=["Tasks"])

LOGGER = get_logger(__name__)


class CreateTaskRequest(BaseModel):
    user_input: str


@router.post("/", summary="创建任务", response_model=APIResponse)
async def create_task_api(request: CreateTaskRequest, req: Request, task_service: TaskServiceDep):
    """
    创建任务：根据用户输入调用 IntelligentPluginRouter，生成任务并保存
    """
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"获取APP配置信息：{app_config.name}")
    result = await task_service.create_task_from_input(request.user_input)
    return APIResponse.ok(result)
