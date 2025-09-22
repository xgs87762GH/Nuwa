from typing import List

from fastapi import APIRouter

from src.api.dependencies import AIManagerDep, IntelligentPluginRouterDep
from src.api.models import AIServerListResponse, AIProvidersResponse, APIResponse
from src.api.models.responses import AIProviderInfo
from src.core.config import get_logger

router = APIRouter(prefix="/ai", tags=["AI Management"])
LOGGER = get_logger(__name__)


@router.get(
    "/services",
    summary="Get all AI servers",
    description="Retrieve status information for all configured AI providers",
    response_model=AIServerListResponse
)
async def get_all_ai_server(ai_manager: AIManagerDep) -> AIServerListResponse:
    """Get all AI servers status"""
    provider_status_list = ai_manager.get_provider_status()

    providers = [
        AIProviderInfo(
            type=data.get("type", "unknown"),
            default_model=data.get("default_model", "unknown"),
            models=data.get("models", []),
            base_url=data.get("base_url", "default"),
            status=data.get("status", "inactive"),
            initialized_at=data.get("initialized_at", "")
        )
        for data in provider_status_list
    ]

    response_data = AIProvidersResponse(providers=providers, total=len(providers))
    LOGGER.info(f"Available AI providers: {len(providers)}")

    return APIResponse.ok(data=response_data)


@router.post("/set_default/{provider_type}", summary="Set default AI provider", response_model=APIResponse)
async def set_default_ai_provider(provider_type: str,
                                  intelligent_plugin_router: IntelligentPluginRouterDep) -> APIResponse:
    """
    Set the default AI provider by type.
    """
    intelligent_plugin_router.set_preferred_provider(provider_type)
    LOGGER.info(f"Set default AI provider to {provider_type}")
    LOGGER.info(f"preferred providers: {intelligent_plugin_router.ai_service.preferred_provider}")
    return APIResponse.ok(message="Default AI provider set successfully")


@router.get("/provider/current", summary="Get current AI provider", response_model=APIResponse)
async def get_current_ai_provider(ai_manager_dep: AIManagerDep) -> APIResponse:
    """Get current AI provider"""
    return APIResponse.ok(data=ai_manager_dep.primary_provider)


@router.get("/provider/models/{provider_type}", summary="Get models for AI provider", response_model=APIResponse)
async def get_models_for_provider(provider_type: str, ai_manager_dep: AIManagerDep) -> APIResponse:
    """
    Get models for a specific AI provider.
    """
    models: List[str] = ai_manager_dep.get_models_by_provider(provider_type)
    return APIResponse.ok(data=models)
