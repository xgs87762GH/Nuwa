from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any

from src.core.ai.providers.response import PluginsSelection


class ErrorCode(Enum):
    """错误代码"""
    INVALID_JSON = "INVALID_JSON"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_TYPE = "INVALID_TYPE"
    AI_ERROR = "AI_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"


@dataclass
class SelectionResponse:
    """响应基类"""
    success: bool
    timestamp: str = ""
    error_code: str = ""
    error_message: str = ""
    details: Optional[str] = None
    data: Optional[Any] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def success_response(cls, data: Any) -> "SelectionResponse":
        """成功响应"""
        return cls(success=True, data=data)

    @classmethod
    def error_response(cls, error_code: str, error_message: str,
                       details: Optional[str] = None) -> "SelectionResponse":
        """错误响应"""
        return cls(success=False, error_code=error_code, error_message=error_message, details=details)
