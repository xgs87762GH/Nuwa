from fastapi import APIRouter

from src.api.models import SystemInfoAPIResponse, HealthStatusAPIResponse, SystemInfo, HealthStatus, APIResponse
from src.core.config import get_logger, get_app_config

LOGGER = get_logger(__name__)
application = get_app_config()
router = APIRouter(tags=["System"])


@router.get(
    "/",
    summary="Get system information",
    description="Get basic system information including version and documentation",
    response_model=SystemInfoAPIResponse
)
async def root() -> SystemInfoAPIResponse:
    """Get system information"""
    system_info = SystemInfo(
        message="Welcome to the Nuwa API",
        version=application.version,
        documentation="/docs"
    )

    return APIResponse.ok(data=system_info, message="System information retrieved")


@router.get(
    "/health",
    summary="Check system status",
    description="Perform a basic health check of the system",
    response_model=HealthStatusAPIResponse
)
async def health_check() -> HealthStatusAPIResponse:
    """System health check"""
    health_status = HealthStatus(status="ok")
    return APIResponse.ok(data=health_status, message="System is healthy")
