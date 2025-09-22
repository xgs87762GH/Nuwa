import json
from typing import Any, Dict, Optional

from src.core.ai import AIManager
from src.core.ai.providers.response import ExecutionPlan
from src.core.config.logger import get_logger
from src.core.orchestration import PlanService, PluginService
from src.core.orchestration.model import PlanResult, PluginStatusResult

LOGGER = get_logger(__name__)


class IntelligentPluginRouter:
    def __init__(
            self,
            plugin_service: PluginService,
            ai_manager: AIManager,
            plan_service: PlanService,
            model=None
    ):
        self.plugin_service = plugin_service
        self.ai_manager = ai_manager
        self.plan_service = plan_service
        self.model = model

    async def analyze_and_plan(self, user_input: str) -> PlanResult:
        try:
            LOGGER.info(f"🤖 开始分析用户需求: {user_input}")
            if not user_input or not user_input.strip():
                return PlanResult.error_result("用户输入不能为空")
            available_plugins = await self.plugin_service.get_available_plugins()
            if not available_plugins:
                return PlanResult.error_result("没有可用的插件", suggestion="请检查插件是否正确加载和启用")
            selected_plugins = await self.plan_service.select_plugins(user_input, available_plugins)
            if not selected_plugins:
                return PlanResult.error_result(
                    "未找到合适的插件",
                    user_input=user_input,
                    selected_plugins=[],
                    suggestion="请检查插件配置"
                )
            plugin_functions = await self.plugin_service.get_plugin_functions(selected_plugins, available_plugins)
            if not plugin_functions:
                return PlanResult.error_result(
                    "未找到合适的函数",
                    user_input=user_input,
                    selected_plugins=selected_plugins
                )
            execution_plan: ExecutionPlan = await self.plan_service.generate_execution_plan(user_input,
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

    def _parse_ai_response(self, content: str) -> Optional[Dict[str, Any]]:
        try:
            if not content:
                LOGGER.error("AI返回的内容为空")
                return None
            if isinstance(content, str):
                result = json.loads(content)
            elif isinstance(content, dict):
                result = content
            else:
                LOGGER.error(f"不支持的响应类型: {type(content)}")
                return None
            return result
        except json.JSONDecodeError as e:
            LOGGER.error(f"❌ 解析AI返回的JSON失败: {e}")
            return None
        except Exception as e:
            LOGGER.error(f"❌ 解析AI响应失败: {e}")
            return None

    async def get_plugin_status(self) -> PluginStatusResult:
        try:
            available_plugins = await self.plugin_service.get_available_plugins()
            all_plugins = await self.plugin_service.plugin_manager.list_plugins()
            return PluginStatusResult(
                total_plugins=len(all_plugins),
                available_plugins=len(available_plugins),
                plugin_names=[p["plugin_name"] for p in available_plugins]
            )
        except Exception as e:
            LOGGER.error(f"❌ 获取插件状态失败: {e}")
            return PluginStatusResult.error_result(str(e))
