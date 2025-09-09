from typing import Optional

from src.core.ai import AIManager
from src.core.config import create_database_manager, DataBaseManager
from src.core.di.container import container
from src.core.orchestration import IntelligentPluginRouter
from src.core.plugin import PluginManager
from src.core.tasks.service import TaskService


class ServiceBootstrap:
    """服务启动器，负责初始化和注册所有服务"""

    def __init__(self):
        self._plugin_manager: Optional[PluginManager] = None
        self._ai_manager: Optional[AIManager] = None
        self._database_manager: Optional[DataBaseManager] = None

    async def register_services(self):
        """注册所有服务到容器"""

        # 1. 注册基础管理器
        await self._register_managers()

        # 2. 注册业务服务
        await self._register_services()

        # 3. 注册其他依赖
        await self._register_dependencies()

    async def _register_managers(self):
        """注册基础管理器"""

        # 数据库管理器
        self._database_manager = create_database_manager()
        await self._database_manager.connect()
        container.register_singleton(DataBaseManager, self._database_manager)


        # 插件管理器
        self._plugin_manager = PluginManager()
        await self._plugin_manager.start()
        container.register_singleton(PluginManager, self._plugin_manager)

        # AI管理器
        self._ai_manager = AIManager()
        container.register_singleton(AIManager, self._ai_manager)

    async def _register_services(self):
        """注册业务服务"""

        # 智能插件路由器
        router = IntelligentPluginRouter(plugin_manager=self._plugin_manager)
        container.register_singleton(IntelligentPluginRouter, router)

        # 任务服务 - 使用工厂注册，支持依赖注入
        container.register_factory(TaskService, lambda: TaskService(
            db=container.get(DataBaseManager),
            router=container.get(IntelligentPluginRouter)
        ))

    async def _register_dependencies(self):
        """注册其他依赖"""
        pass

    async def cleanup(self):
        """清理资源"""
        if self._plugin_manager:
            await self._plugin_manager.stop()

        if self._database_manager:
            await self._database_manager.disconnect()
