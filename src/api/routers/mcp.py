from typing import Dict, List, Any

from fastapi import APIRouter

from src.api.dependencies import PluginManagerDep
from src.api.models import APIResponse
from src.core.config import get_logger
from src.core.plugin.model import PluginRegistration

router = APIRouter(prefix="/mcp")

LOGGER = get_logger(__name__)


@router.get("/tools", summary="Get all available tools.", response_model=APIResponse)
async def get_tools(plugin_manager: PluginManagerDep):
    """
    Get all available tools.
    """
    plugins: List[PluginRegistration] = await plugin_manager.list_plugins()
    return APIResponse.ok({
        "total": len(plugins) if plugins else 0,
        "tools": [
            {
                "id": plugin.id,
                "name": plugin.name,
                "version": plugin.version,
                "status": plugin.load_status,
                "description": plugin.description,
                "registered_at": plugin.registered_at,
                "is_enabled": plugin.is_enabled,
                "tags": plugin.tags,
                "metadata": plugin.metadata
            } for plugin in plugins
        ]
    })


@router.get("/tools/stats", summary="Count all plugins.", response_model=APIResponse)
async def get_tools_statistics(plugin_manager: PluginManagerDep):
    """
    Count all plugins.
    """
    plugins: List[PluginRegistration] = await plugin_manager.list_plugins()
    LOGGER.info(f"Total plugins: {len(plugins)}")
    return APIResponse.ok({
        "total": len(plugins) if plugins else 0
    })

@router.get("/tools/{tool_id}", summary="Get tool details.", response_model=APIResponse)
async def get_tool_details(tool_id: str, plugin_manager: PluginManagerDep):
    """
    Get tool details.
    """
    plugin: PluginRegistration = await plugin_manager.get_plugin_info(tool_id)
    if plugin:
        return APIResponse.ok({
            "id": plugin.id,
            "name": plugin.name,
            "version": plugin.version,
            "status": plugin.load_status,
            "description": plugin.description,
            "registered_at": plugin.registered_at,
            "is_enabled": plugin.is_enabled,
            "tags": plugin.tags,
            "metadata": plugin.metadata
        })
    return APIResponse.ok()
