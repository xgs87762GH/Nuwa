from src.core.config.models.ai_model import AIModel, AIProviderEnum, AIConfig
from src.core.config.models.db_models import DbBase, DatabaseConfig
from src.core.config.models.logger_models import LoggingConfig
from src.core.config.models.app_models import AppConfig
from pydantic import BaseModel, Field


class PluginConfig(BaseModel):
    auto_discovery: bool = Field(True, description="是否自动发现插件")


__all__ = [
    "AIModel",
    "AIProviderEnum",
    "AIConfig",

    # db
    "DbBase",
    "DatabaseConfig",

    # logger
    "LoggingConfig",

    # app
    "AppConfig",

    # plugin
    "PluginConfig"
]
