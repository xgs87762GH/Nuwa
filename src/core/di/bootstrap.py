from typing import Optional

from src.core.ai import AIManager
from src.core.config import create_database_manager, DataBaseManager
from src.core.di.container import container
from src.core.orchestration import IntelligentPluginRouter, PluginService, Planner
from src.core.plugin import PluginManager
from src.core.scheduler import SchedulerRegister
from src.core.tasks.service import TaskService
from src.core.utils.global_tools import project_root
from src.core.utils.template import EnhancedPromptTemplates


class ServiceBootstrap:
    """服务启动器，负责初始化和注册所有服务"""

    def __init__(self):
        self._plugin_manager: Optional[PluginManager] = None
        self._ai_manager: Optional[AIManager] = None
        self._database_manager: Optional[DataBaseManager] = None
        self.scheduler_register: Optional[SchedulerRegister] = None

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
        # 创建并注册 PluginService 单例
        plugin_service = PluginService(self._plugin_manager)
        container.register_singleton(PluginService, plugin_service)

        # 计划生成服务 - 使用已注册的 AIService 单例
        self.prompt_templates = EnhancedPromptTemplates(str(project_root() / "templates" / "prompts"))

        # 智能插件路由器 - 使用已注册的服务单例
        router = IntelligentPluginRouter(
            plugin_service=plugin_service,
            ai_manager=self._ai_manager,
            planner=Planner(ai_manager=self._ai_manager, prompt_templates=self.prompt_templates)
        )
        container.register_singleton(IntelligentPluginRouter, router)

        # 任务服务 - 使用工厂注册，支持依赖注入
        container.register_factory(TaskService, lambda: TaskService(
            db=container.get(DataBaseManager)
        ))

        self.scheduler_register = SchedulerRegister()
        await self.scheduler_register.start()
        container.register_singleton(SchedulerRegister, self.scheduler_register)

    async def _register_dependencies(self):
        """注册其他依赖"""
        pass

    async def cleanup(self):
        """清理资源"""
        if self._plugin_manager:
            await self._plugin_manager.stop()
        if self._database_manager:
            await self._database_manager.disconnect()
        if self.scheduler_register:
            await self.scheduler_register.stop()
