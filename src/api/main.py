from contextlib import asynccontextmanager
from fastapi import FastAPI

from .routers import tasks
from src.core.config import get_app_config, get_logger
from src.core.di.bootstrap import ServiceBootstrap

application = get_app_config()
LOGGER = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""

    # ===== 应用启动前：初始化必备组件 =====
    LOGGER.info("App starting: initializing components")

    # 初始化服务容器
    bootstrap = ServiceBootstrap()
    try:
        await bootstrap.register_services()

        # 保存bootstrap实例，用于清理
        app.state.bootstrap = bootstrap
        app.state.app_config = application

        LOGGER.info("All services registered successfully")

        # 交还控制权给 FastAPI
        yield

    finally:
        # ===== 应用关闭时：优雅清理资源 =====
        LOGGER.info("App shutting down: releasing resources")

        try:
            if hasattr(app.state, 'bootstrap'):
                await app.state.bootstrap.cleanup()
        except Exception as e:
            LOGGER.exception("Error while cleaning up services: %s", e)


def init_router() -> FastAPI:
    """初始化FastAPI路由"""

    fastapi = FastAPI(
        title=application.name,
        version=application.version,
        description=application.description,
        lifespan=lifespan
    )

    # 注册路由
    fastapi.include_router(tasks.router, prefix="/v1", tags=["tasks"])

    @fastapi.get("/", tags=["root"])
    async def root():
        return {
            "message": "Welcome to the Nuwa API",
            "version": application.version,
            "documentation": "/docs"
        }

    @fastapi.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "version": application.version}

    return fastapi