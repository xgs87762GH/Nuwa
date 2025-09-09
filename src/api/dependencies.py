from fastapi import Depends
from typing import Annotated

from src.core.di.container import container
from src.core.plugin.manager import PluginManager
from src.core.tasks.service import TaskService
from src.core.config import DataBaseManager
from src.core.ai import AIManager


def get_plugin_manager() -> PluginManager:
    """获取插件管理器"""
    return container.get(PluginManager)


def get_task_service() -> TaskService:
    """获取任务服务"""
    return container.get(TaskService)


def get_database_manager() -> DataBaseManager:
    """获取数据库管理器"""
    return container.get(DataBaseManager)


def get_ai_manager() -> AIManager:
    """获取AI管理器"""
    return container.get(AIManager)


# 类型别名 - 这些是依赖注入的类型标注
PluginManagerDep = Annotated[PluginManager, Depends(get_plugin_manager)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
DataBaseManagerDep = Annotated[DataBaseManager, Depends(get_database_manager)]
AIManagerDep = Annotated[AIManager, Depends(get_ai_manager)]
