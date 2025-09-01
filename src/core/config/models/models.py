import logging
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field
from pydantic import field_validator

from src.core.utils.global_tools import project_root


class DatabaseConfig(BaseModel):
    driver: str = Field("sqlite+aiosqlite", description="Database driver type")
    url: Optional[str] = Field(None, description="Database connection URL")
    pool_size: int = Field(10, ge=1, le=100, description="Database connection pool size")
    max_overflow: int = Field(20, ge=0, le=200, description="Maximum overflow connections")
    echo: bool = Field(False, description="Enable SQL query logging")
    pool_pre_ping: bool = Field(True, description="连接池预检查")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database URL format"""
        if not v:
            return "sqlite+aiosqlite:///./data/nuwa.db"

        valid_prefixes = [
            'postgresql://', 'postgresql+asyncpg://', 'postgresql+psycopg://',
            'mysql://', 'mysql+aiomysql://', 'mysql+asyncmy://',
            'sqlite:///', 'sqlite+aiosqlite:///',
            'oracle://', 'oracle+cx_oracle_async://',
            'mssql://', 'mssql+aioodbc://'
        ]

        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(f"URL must start with one of: {', '.join(valid_prefixes)}")

        return v

    @field_validator('max_overflow')
    @classmethod
    def validate_max_overflow(cls, v, info):
        if info.data.get('pool_size') and v < info.data['pool_size']:
            raise ValueError('max_overflow must be greater than or equal to pool_size')
        return v


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


class AppConfig(BaseModel):
    name: str = Field(description="Application name")
    version: str = Field("1.0.0", description="Application version")
    description: str = Field(description="Application description")
    debug: bool = Field(description="Enable debug mode")
    host: str = Field("0.0.0.0", description="Server host address")
    port: int = Field(8000, ge=1, le=65535, description="Server port number")
    environment: str = Field(description="Application environment")
    readme: str = Field(description="README file path")
    authors: list[dict] = Field(description="List of authors")
    license: dict = Field(description="License information")
    requires_python: str = Field(description="Required Python version")
    keywords: list[str] = Field(description="Application keywords")

    @field_validator('host')
    @classmethod
    def validate_host(cls, v):
        import re
        # Check if it's a valid IP address pattern or common hostnames
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if v in ['0.0.0.0', 'localhost', '127.0.0.1'] or re.match(ip_pattern, v):
            return v
        raise ValueError('Host must be a valid IP address or hostname')

    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ['development', 'testing', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f'Environment must be one of: {", ".join(valid_envs)}')
        return v.lower()

    @field_validator('requires_python')
    @classmethod
    def validate_python_version(cls, v):
        import re
        pattern = r'^>=\d+\.\d+(\.\d+)?$'
        if not re.match(pattern, v):
            raise ValueError('Python version must be in format ">=X.Y" or ">=X.Y.Z"')
        return v

class PluginConfig(BaseModel):
    auto_discovery: bool = Field(True, description="是否自动发现插件")