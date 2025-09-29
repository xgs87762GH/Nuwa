from fastapi import Depends
from typing import Annotated

from src.core.di.container import container
from src.core.orchestration import IntelligentRouter
from src.core.plugin.manager import PluginManager
from src.core.tasks import TaskHandler
from src.core.config import DataBaseManager
from src.core.ai import AIManager


def get_plugin_manager() -> PluginManager:
    """获取插件管理器"""
    return container.get(PluginManager)


def get_task_service() -> TaskHandler:
    """获取任务服务"""
    return container.get(TaskHandler)


def get_database_manager() -> DataBaseManager:
    """获取数据库管理器"""
    return container.get(DataBaseManager)


def get_ai_manager() -> AIManager:
    """获取AI管理器"""
    return container.get(AIManager)


def get_intelligent_plugin_router() -> IntelligentRouter:
    """获取智能插件路由器"""
    return container.get(IntelligentRouter)


# 类型别名 - 这些是依赖注入的类型标注
PluginManagerDep = Annotated[PluginManager, Depends(get_plugin_manager)]
TaskHandlerDep = Annotated[TaskHandler, Depends(get_task_service)]
DataBaseManagerDep = Annotated[DataBaseManager, Depends(get_database_manager)]
AIManagerDep = Annotated[AIManager, Depends(get_ai_manager)]
IntelligentRouterDep = Annotated[IntelligentRouter, Depends(get_intelligent_plugin_router)]
