# MCP Server Module
import asyncio
import logging
# PluginRegistration
from typing import Dict, Any

from src.core.mcp.rpc import MCPRequestSchema, MCPResponseSchema
from src.core.mcp.rpc.response import JSONRPCError
from src.core.plugin import PluginManager

LOGGER = logging.getLogger(__name__)


class MCPServer:
    def __init__(self, plugin_manager: PluginManager) -> None:
        self.plugin_manager = plugin_manager

    async def call(self, req: MCPRequestSchema) -> MCPResponseSchema:
        plugin_id: str = req.method
        params: Dict[str, Any] = req.params or {}
        try:
            result = self.plugin_manager.call(plugin_id, req.method, **params)
            if result:
                return MCPResponseSchema.success(result)
            else:
                return MCPResponseSchema.success(None)
        except Exception as exc:
            # LOGGER.exception("❌ %s.%s call failed: %s", adapter_name, method_name, exc)
            LOGGER.error("❌ %s.%s call failed: %s", plugin_id, req.method, exc)
            LOGGER.exception(exc)
            return MCPResponseSchema.fail(req.id, JSONRPCError.internal_error(str(exc)))

