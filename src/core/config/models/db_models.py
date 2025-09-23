from sqlalchemy.orm import declarative_base

DbBase = declarative_base()
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import field_validator


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
