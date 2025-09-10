# class JSONRPCRequest(BaseModel):
#     jsonrpc: str = "2.0"
#     id: str | int | None = None
#     method: str = "camera.take_photo"
#     params: Dict[str, Any]

from typing import Dict, Any, Union, Optional

from pydantic import BaseModel, Field

from src.core.mcp.rpc import JSONRPCVersion


class McpRequestParams(BaseModel):
    """MCP request parameters containing function name and arguments"""

    fun_name: str = Field(..., description="Plugin ID to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Method arguments")

    class Config:
        schema_extra = {
            "example": {
                "fun_name": "camera_capture",
                "arguments": {
                    "device_id": 0,
                    "format": "jpg"
                }
            }
        }


class MCPRequestSchema(BaseModel):
    """MCP request schema following JSON-RPC 2.0 specification"""

    jsonrpc: JSONRPCVersion = Field(default=JSONRPCVersion.V2_0, description="JSON-RPC version")
    method: str = Field(..., description="Method name to call")
    params: Optional[McpRequestParams] = Field(None, description="Method parameters")
    id: Optional[Union[str, int]] = Field(None, description="Request ID for response correlation")

    class Config:
        schema_extra = {
            "example": {
                "jsonrpc": "2.0",
                "method": "execute_plugin",
                "params": {
                    "fun_name": "camera_capture",
                    "arguments": {
                        "device_id": 0,
                        "format": "jpg"
                    }
                },
                "id": "req_001"
            }
        }
