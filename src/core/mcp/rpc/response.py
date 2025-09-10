from typing import Dict, Any, Union, Optional

from pydantic import BaseModel
from pydantic import Field

from src.core.mcp.rpc import JSONRPCVersion


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Any = None

    @staticmethod
    def parse_error(msg: str = "Parse error") -> "JSONRPCError":
        return JSONRPCError(code=-32700, message=msg)

    @staticmethod
    def invalid_request(msg: str = "Invalid Request") -> "JSONRPCError":
        return JSONRPCError(code=-32600, message=msg)

    @staticmethod
    def method_not_found(msg: str = "Method not found") -> "JSONRPCError":
        return JSONRPCError(code=-32601, message=msg)

    @staticmethod
    def invalid_params(msg: str = "Invalid params") -> "JSONRPCError":
        return JSONRPCError(code=-32602, message=msg)

    @staticmethod
    def internal_error(msg: str = "Internal error") -> "JSONRPCError":
        return JSONRPCError(code=-32603, message=msg)

    @staticmethod
    def custom(code: int, msg: str, data: Any = None) -> "JSONRPCError":
        return JSONRPCError(code=code, message=msg, data=data)

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


#
# class JSONRPCResponse(BaseModel):
#     jsonrpc: str = "2.0"
#     id: str | int | None
#     result: Any = None
#     error: JSONRPCError | None = None

class MCPResponseSchema(BaseModel):
    """MCP 响应 Schema"""
    jsonrpc: JSONRPCVersion = JSONRPCVersion.V2_0
    result: Optional[Any] = Field(None, description="方法执行结果")
    error: Optional[Dict[str, Any]] = Field(None, description="错误信息")
    id: Optional[Union[str, int]] = Field(None, description="对应请求的ID")

    @staticmethod
    def success(result: Any, rid: Optional[Union[str, int]] = None) -> "MCPResponseSchema":
        """成功响应"""
        return MCPResponseSchema(result=result, id=rid)

    @staticmethod
    def fail(request_id: Union[str, int], error: JSONRPCError):
        return MCPResponseSchema(error=error.to_dict(), id=request_id)
