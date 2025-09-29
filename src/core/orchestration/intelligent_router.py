import json
from typing import Any, Dict, Optional, List

from src.core.ai import AIManager
from src.core.ai.providers.response import ExecutionPlan
from src.core.config.logger import get_logger
from src.core.orchestration import TaskPlanner
from src.core.orchestration.model import PlanResult, PluginStatusResult
from src.core.plugin import PluginManager
from src.core.plugin.model import PluginRegistration

LOGGER = get_logger(__name__)


class IntelligentRouter:
    def __init__(
            self,
            # plugin_service: PluginInfoProvider,
            plugin_manager: PluginManager,
            ai_manager: AIManager,
            TaskPlanner: TaskPlanner,
            model=None
    ):
        # self.plugin_service = plugin_service
        self.ai_manager = ai_manager
        self.plugin_manager = plugin_manager
        self.TaskPlanner = TaskPlanner
        self.model = model

    async def analyze_and_plan(self, user_input: str) -> PlanResult:
        try:
            LOGGER.info(f"🤖 开始分析用户需求: {user_input}")
            if not user_input or not user_input.strip():
                return PlanResult.error_result("用户输入不能为空")
            available_plugins = await self.list_available_plugins()
            if not available_plugins or len(available_plugins) == 0:
                return PlanResult.error_result("没有可用的插件", suggestion="请检查插件是否正确加载和启用")
            selected_plugins = await self.TaskPlanner.select_plugins(user_input, available_plugins)
            if not selected_plugins:
                return PlanResult.error_result(
                    "未找到合适的插件",
                    user_input=user_input,
                    selected_plugins=[],
                    suggestion="请检查插件配置"
                )
            plugin_functions = await self.get_plugin_functions(selected_plugins)
            if not plugin_functions:
                return PlanResult.error_result(
                    "未找到合适的函数",
                    user_input=user_input,
                    selected_plugins=selected_plugins
                )
            execution_plan: ExecutionPlan = await self.TaskPlanner.plan_execution(user_input,
                                                                                  plugin_functions)
            if not execution_plan:
                return PlanResult.error_result(
                    "执行计划生成失败",
                    user_input=user_input
                )
            LOGGER.info("✅ 执行计划生成成功")
            return PlanResult.success_result(
                user_input=user_input,
                selected_plugins=selected_plugins,
                plugin_functions=plugin_functions,
                execution_plan=execution_plan
            )
        except Exception as e:
            LOGGER.exception(f"❌ 分析失败: {e}")
            return PlanResult.error_result(f"{str(e)}")

    async def list_available_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                'plugin_name': p.name,
                'plugin_id': p.id,
                'description': p.description,
                'tags': p.tags
            }
            for p in await self.plugin_manager.list_available_plugins()
        ]

    async def get_plugin_functions(self, selected_plugins):
        plugin_functions = []
        for selected_plugin in selected_plugins:
            plugin_id = selected_plugin.plugin_id
            plugin_obj: PluginRegistration = await self.plugin_manager.get_plugin_by_id(plugin_id)
            functions = await self.extract_plugin_functions(plugin_obj)
            if functions:
                plugin_functions.append({
                    'plugin_name': plugin_obj.name,
                    'plugin_id': plugin_obj.id,
                    'description': plugin_obj.description,
                    'functions': functions,
                    'selection_reason': selected_plugin.reason
                })
        return plugin_functions

    async def extract_plugin_functions(self, plugin_obj: PluginRegistration):
        functions = []
        for service in plugin_obj.plugin_services:
            service_function = service.functions
            functions_list = []
            if service_function and callable(service_function):
                functions_list = service_function()
            elif service_function and isinstance(service_function, list):
                functions_list = service_function
            elif service_function and isinstance(service_function, str):
                functions_list = json.loads(service_function)
            if not functions_list:
                continue
            for func in functions_list:
                if isinstance(func, dict) and func.get("name"):
                    functions.append({
                        "name": func.get("name"),
                        "description": func.get("description", ""),
                        "input_schema": func.get("input_schema", {}),
                        "full_method_name": f"{plugin_obj.name}.{func.get('name')}"
                    })
        return functions
