from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.api.dependencies import TaskServiceDep
from src.core.config import AppConfig
from src.core.config.logger import get_logger

router = APIRouter(prefix="/tasks", tags=["Tasks"])

LOGGER = get_logger(__name__)


class CreateTaskRequest(BaseModel):
    user_input: str


@router.post("/", summary="创建任务", response_model=None)
async def create_task_api(request: CreateTaskRequest, req: Request, task_service: TaskServiceDep):
    """
    创建任务：根据用户输入调用 IntelligentPluginRouter，生成任务并保存
    """
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"获取APP配置信息：{app_config.name}")
    result = await task_service.create_task_from_input(request.user_input)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "任务创建失败"))
    return result


if __name__ == '__main__':

    import requests
    import json

    url = "http://localhost:8000/v1/tasks/"
    data = {"user_input": "take a photo"}

    try:
        response = requests.post(url, json=data, proxies={"http": None, "https": None})
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")
