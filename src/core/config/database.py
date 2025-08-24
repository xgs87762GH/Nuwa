import time
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
import logging

from src.core.config.config import ConfigManager
from src.core.config.models.models import DatabaseConfig
from src.core.utils.global_tools import project_root


class DataBaseManager:
    """Database manager for SQLAlchemy async operations."""

    def __init__(self, db_url: Optional[str] = None):
        self.cfg = ConfigManager()
        self.db: DatabaseConfig = self.cfg.load_config_model(DatabaseConfig, "database")
        self.logger = logging.getLogger(__name__)

        database_url = db_url or self.db.url

        self._prepare_database_url(database_url)

        # Create engine with proper kwargs
        engine_kwargs = self._create_engine_kwargs()
        self.engine: AsyncEngine = create_async_engine(database_url, **engine_kwargs)

        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def _create_engine_kwargs(self) -> Dict[str, Any]:
        """Create engine kwargs based on database type."""
        kwargs = {"echo": self.db.echo}

        if "sqlite" in self.db.url.lower():
            kwargs.update({
                "connect_args": {"check_same_thread": False},
                "pool_pre_ping": True,
            })
        else:
            kwargs.update({
                "pool_pre_ping": self.db.pool_pre_ping,
                "pool_size": self.db.pool_size,
                "max_overflow": self.db.max_overflow,
                "pool_timeout": self.db.pool_timeout,
                "pool_recycle": self.db.pool_recycle
            })
        return kwargs

    async def connect(self) -> bool:
        """Test database connection."""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            self.logger.info("Successfully connected to database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False

    async def disconnect(self) -> None:
        """Close database connection."""
        try:
            await self.engine.dispose()
            self.logger.info("Database connection closed successfully")
        except Exception as e:
            self.logger.error(f"Error while disconnecting from database: {e}")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for database sessions."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Database session error: {e}")
                raise

    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        try:
            start_time = time.time()
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "database_type": self.db.driver
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _prepare_database_url(self, db_url: Optional[str] = None) -> str:
        """Prepare database URL and ensure directory exists for file-based databases."""
        if db_url:
            url = db_url
        else:
            url = self.db.url or "sqlite+aiosqlite:///./data/nuwa.db"
            # Convert sqlite:// to sqlite+aiosqlite:// for async support
            if url.startswith("sqlite:///") and "+aiosqlite" not in url:
                url = url.replace("sqlite:///", "sqlite+aiosqlite:///")

        # Create directory for SQLite file databases (not for memory databases)
        if "sqlite" in url.lower() and "///" in url:
            db_path = url.split("///")[-1]
            if db_path and db_path != ":memory:":
                file_path = Path(f"{project_root()}/{db_path}")
                # Ensure the directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                self.logger.info("Database directory created: %s", file_path.parent)

        return url

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
