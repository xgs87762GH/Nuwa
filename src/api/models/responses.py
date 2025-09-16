from typing import Any, Optional, Union, List, Dict
from pydantic import BaseModel


class APIResponse(BaseModel):
    """API 响应模型"""
    success: bool = True
    message: str = ""
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None  # 支持字典、列表或任意类型

    @classmethod
    def ok(cls, data: Any = None, message: str = ""):
        """成功响应"""
        return cls(success=True, data=data, message=message)

    @classmethod
    def error(cls, message: str = "", data: Any = None):
        """错误响应"""
        return cls(success=False, message=message, data=data)