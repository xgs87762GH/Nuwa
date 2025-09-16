from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class AIProviderEnum(Enum):
    """AI提供者枚举"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

    @classmethod
    def get_by_name(cls, name: str) -> Optional["AIProviderEnum"]:
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
    models: List[str] = None
    default_model: str = None
    user: str = None
    max_tokens: int = 1024
    request_timeout: int = 60
    anthropic_version: str = None

    @classmethod
    def from_dict(cls, data: dict) -> "AIConfig":
        """Create AIConfig from dictionary, ignoring unknown fields"""
        # Map field names
        field_mapping = {
            'anthropic-version': 'anthropic_version'
        }

        # Convert field names
        processed_data = {}
        for key, value in data.items():
            mapped_key = field_mapping.get(key, key)
            processed_data[mapped_key] = value

        # Filter only known fields
        known_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in processed_data.items() if k in known_fields}

        return cls(**filtered_data)


@dataclass
class AIModel:
    provider: Optional[AIProviderEnum] = None
    config: Optional[AIConfig] = None
