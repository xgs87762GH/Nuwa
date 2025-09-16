from typing import Dict, List, Any

from fastapi import APIRouter

from src.api.dependencies import PluginManagerDep
from src.api.models import APIResponse
from src.core.config import get_logger

router = APIRouter(prefix="/mcp")

LOGGER = get_logger(__name__)


@router.get("/tools", summary="Get all available tools.", response_model=APIResponse)
async def get_tools(plugin_manager: PluginManagerDep):
    """
    Get all available tools.
    """
    plugins: List[Dict[str, Any]] = await plugin_manager.list_plugins()
    return APIResponse.ok({
        "total": len(plugins) if plugins else 0,
        "tools": plugins
    })


@router.get("/tools/stats", summary="Count all plugins.", response_model=APIResponse)
async def get_tools_statistics(plugin_manager: PluginManagerDep):
    """
    Count all plugins.
    """
    plugins: List[Dict[str, Any]] = await plugin_manager.list_plugins()
    LOGGER.info(f"Total plugins: {len(plugins)}")
    return APIResponse.ok({
        "total": len(plugins) if plugins else 0
    })


@router.get("/tools/{tool_id}", summary="Get tool details.", response_model=APIResponse)
async def get_tool_details(tool_id: str, plugin_manager: PluginManagerDep):
    """
    Get tool details.
    """
    plugin: Dict[str, Any] = await plugin_manager.get_plugin_info(tool_id)
    return APIResponse.ok(plugin)
