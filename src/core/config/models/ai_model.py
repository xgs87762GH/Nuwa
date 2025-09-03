import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
from pathlib import Path


class AIProvider(Enum):
    """AI提供者枚举"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

    @classmethod
    def get_by_name(cls, name: str) -> Optional["AIProvider"]:
        """根据名称获取AI提供者枚举"""
        for provider in cls:
            if provider.value == name:
                return provider
        return None


@dataclass
class AIConfig:
    """AI配置数据模型"""
    base_url: str = None
    api_key: str = None
    model: str = None
    user: str = None
    max_tokens: int = 1024
    request_timeout: int = 60

@dataclass
class AIModel:
    provider: Optional[AIProvider] = None
    config: Optional[AIConfig] = None
