# FastAPI Application Module
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers import tasks

# 导入配置模块
from src.core.config import (
    get_app_config
)

application = get_app_config()


def init_router() -> FastAPI:
    fastapi = FastAPI(
        title=application.name,
        version=application.version,
        description=application.description,
    )

    # register routers
    fastapi.include_router(tasks.router, prefix="/v1", tags=["tasks"])

    @fastapi.get("/", tags=["root"])
    async def root():
        return {
            "message": "Welcome to the HomeGuard API",
            "version": application.version,
            "documentation": "/docs"
        }

    @fastapi.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "version": application.version}

    return fastapi
