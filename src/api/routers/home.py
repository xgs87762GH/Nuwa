from fastapi import APIRouter

from src.api.models import APIResponse
from src.core.config import get_logger, get_app_config

LOGGER = get_logger(__name__)
application = get_app_config()
router = APIRouter()


@router.get("/", summary="获取系统信息", response_model=APIResponse)
async def root():
    return APIResponse.ok(data={
        "message": "Welcome to the Nuwa API",
        "version": application.version,
        "documentation": "/docs"
    })


@router.get("/health", summary="检查系统状态", response_model=APIResponse)
async def health_check():
    return APIResponse.ok(data={"status": "ok"})
