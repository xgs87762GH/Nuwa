import logging
from typing import Dict, Any

from pydantic import BaseModel, Field
from pydantic import field_validator

from src.core.utils.global_tools import project_root


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(default="structured", description="日志格式: simple, detailed, json, structured")
    file: str = Field(default=f"{project_root()}/logs/app.log", description="日志文件路径")
    console: bool = Field(default=True, description="是否输出到控制台")
    max_file_size: str = Field(default="10MB", description="单个日志文件最大大小")
    backup_count: int = Field(default=5, description="保留的日志文件数量")
    rotation: str = Field(default="time", description="轮转方式: size, time, none")
    rotation_when: str = Field(default="midnight", description="时间轮转时机: midnight, H, M")
    structured_fields: Dict[str, Any] = Field(default_factory=dict, description="结构化日志额外字段")

    @field_validator('level')
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level: {v}. Must be one of {valid_levels}')
        return v.upper()

    @field_validator('format')
    def validate_format(cls, v):
        """验证日志格式"""
        valid_formats = ['simple', 'detailed', 'json', 'structured']
        if v.lower() not in valid_formats:
            raise ValueError(f'Invalid log format: {v}. Must be one of {valid_formats}')
        return v.lower()

    def get_log_level(self) -> int:
        """获取Python日志级别"""
        return getattr(logging, self.level)
