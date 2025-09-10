# from .request import JSONRPCRequest
# from .response import JSONRPCResponse, JSONRPCError
#
# __all__ = [
#     "JSONRPCRequest",
#     "JSONRPCResponse",
#     "JSONRPCError"
# ]
from enum import Enum

from .request import MCPRequestSchema
from .response import MCPResponseSchema


class JSONRPCVersion(str, Enum):
    """JSON-RPC版本"""
    V2_0 = "2.0"


__all__ = [
    "JSONRPCVersion",
    "MCPRequestSchema",
    "MCPResponseSchema"
]
