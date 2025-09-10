# API Response Models Module
from typing import Any

from openai import BaseModel


class APIResponse(BaseModel):
    """
    API 响应模型
    """
    success: bool = True
    message: str = ""
    data: dict[str, Any] | None = None

    @staticmethod
    def ok(data: dict[str, Any] | None = None) -> "APIResponse":
        return APIResponse(success=True, message="Success", data=data)

    @staticmethod
    def error(message: str) -> "APIResponse":
        return APIResponse(success=False, message=message)