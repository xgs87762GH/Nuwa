import json
from typing import Any, Dict, Optional

from src.core.ai.providers.response import ExecutionPlan
from src.core.config.logger import get_logger
from src.core.orchestration.model import PlanResult, PluginStatusResult, AIStatusResult
from src.core.utils.global_tools import project_root
from src.core.utils.template import EnhancedPromptTemplates
from src.core.orchestration import AIService, PlanService, PluginService
from src.core.ai import AIManager

LOGGER = get_logger(__name__)


class IntelligentPluginRouter:
    def __init__(
            self,
            plugin_manager,
            ai_manager=None,
            template_dir=None,
            user_name="Gordon",
            preferred_provider=None,
            fallback_providers=None,
            model=None
    ):
        self.plugin_service = PluginService(plugin_manager)
        self.ai_service = AIService(ai_manager or AIManager(), preferred_provider, fallback_providers, model)
        self.model = model
        self.prompt_templates = EnhancedPromptTemplates(template_dir or str(project_root() / "templates" / "prompts"),
                                                        user_name)
        self.plan_service = PlanService(self.prompt_templates, self.ai_service)
        self.ai_service.validate_ai_manager(LOGGER)

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
            return PlanResult.error_result(f"分析过程中发生错误: {str(e)}")

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

    def get_ai_status(self) -> AIStatusResult:
        try:
            ai_manager = self.ai_service.ai_manager
            return AIStatusResult(
                available_providers=ai_manager.list_available_providers(),
                provider_types=ai_manager.list_provider_types(),
                health_status=ai_manager.health_check(),
                preferred_provider=self.ai_service.preferred_provider,
                fallback_providers=self.ai_service.fallback_providers
            )
        except Exception as e:
            LOGGER.error(f"❌ 获取AI状态失败: {e}")
            return AIStatusResult.error_result(str(e))


# 测试函数
async def test_simple_case():
    from src.core.plugin import PluginManager

    try:
        # 初始化组件
        plugin_manager = PluginManager()
        await plugin_manager.start()

        ai_manager = AIManager()

        # 创建路由器，可以指定首选AI提供者
        router = IntelligentPluginRouter(
            plugin_manager=plugin_manager,
            ai_manager=ai_manager,
            preferred_provider="anthropic",  # 可以根据你的配置调整
            fallback_providers=["openai", "local"]  # 备选方案
        )
        ai_status = router.get_ai_status()
        plugin_status = await router.get_plugin_status()

        print(f"🤖 AI状态: {ai_status}")
        print(f"📊 插件状态: {plugin_status}")

        result = await router.analyze_and_plan("帮我拍一张照片")

        if not result.success:
            print(f"❌ 简单测试失败: {result.error}")
            if result.suggestion:
                print(f"💡 建议: {result.suggestion}")
            return False

        print("✅ 简单测试通过!")
        print(f"筛选的插件数: {len(result.selected_plugins)}")
        print(f"可用函数数: {len(result.plugin_functions)}")
        return True

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        LOGGER.exception(e)
        return False


def main():
    """主函数"""
    print("🚀 启动智能插件路由器测试程序")
    print(f"当前时间: 2025-09-05 03:46:44 UTC")
    print(f"当前用户: Gordon")
    import asyncio
    asyncio.run(test_simple_case())


if __name__ == "__main__":
    main()
