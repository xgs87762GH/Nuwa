"""
Nuwa Core Application
主应用入口点，负责初始化和配置整个应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from src.core.config.config import ConfigManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger = structlog.get_logger()
    logger.info("Starting Nuwa application")

    # 初始化各个管理器
    await app.state.plugin_manager.start()
    await app.state.mcp_server.start()
    await app.state.task_scheduler.start()

    yield

    # 关闭时清理
    logger.info("Shutting down Nuwa application")
    await app.state.task_scheduler.stop()
    await app.state.mcp_server.stop()
    await app.state.plugin_manager.stop()


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    config = ConfigManager()
    # setup_logging(config.logging)

    app = FastAPI(
        title=config.app.name,
        version=config.app.version,
        description="MCP插件管理平台",
        lifespan=lifespan,
        debug=config.app.debug
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 初始化核心组件
    # app.state.plugin_manager = PluginManager()
    # app.state.mcp_server = MCPServer()
    # app.state.task_scheduler = TaskScheduler()
    # app.state.ai_manager = AIManager()

    return app
