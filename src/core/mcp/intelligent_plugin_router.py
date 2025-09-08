import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from src.core.ai.manager import AIManager
from src.core.ai.providers.response import PluginsSelectionResponse, PluginsSelection, PluginSelectionMata
from src.core.config.logger import get_logger
from src.core.plugin import PluginManager
from src.core.plugin.model import PluginRegistration
from src.core.utils.global_tools import project_root
from src.core.utils.template import EnhancedPromptTemplates, PromptResponse

LOGGER = get_logger(__name__)


class IntelligentPluginRouter:
    """智能插件路由器 - AI理解用户需求并生成执行计划"""

    def __init__(self,
                 plugin_manager: PluginManager,
                 ai_manager: AIManager = None,
                 template_dir: str = None,
                 user_name: str = "Gordon",
                 preferred_provider: str = None,
                 fallback_providers: List[str] = None,
                 model: str = None):
        """
        初始化智能插件路由器

        Args:
            plugin_manager: 插件管理器
            ai_manager: AI管理器，如果为None会自动创建
            template_dir: 模板目录路径
            user_name: 用户名
            preferred_provider: 首选AI提供者
            fallback_providers: 备选AI提供者列表
        """
        self.plugin_manager = plugin_manager
        self.ai_manager = ai_manager or AIManager()
        self.preferred_provider = preferred_provider
        self.fallback_providers = fallback_providers or []

        # 初始化模板引擎
        if template_dir is None:
            template_dir = str(project_root() / "templates" / "prompts")
        self.prompt_templates = EnhancedPromptTemplates(template_dir, user_name)

        # 检查AI管理器状态
        self._validate_ai_manager()
        self.model = model  # 可以指定模型

    def _validate_ai_manager(self):
        """验证AI管理器状态"""
        try:
            available_providers = self.ai_manager.list_available_providers()
            if not available_providers:
                LOGGER.warning("⚠️ 没有可用的AI提供者")
                return

            LOGGER.info(f"🤖 可用AI提供者: {available_providers}")

            # 检查首选提供者是否可用
            if self.preferred_provider and self.preferred_provider not in available_providers:
                LOGGER.warning(f"⚠️ 首选提供者 '{self.preferred_provider}' 不可用，将使用备选方案")

        except Exception as e:
            LOGGER.error(f"❌ AI管理器验证失败: {e}")

    async def analyze_and_plan(self, user_input: str) -> Dict[str, Any]:
        """
        分析用户输入并生成执行计划

        流程：用户输入 → AI意图分析 → 插件筛选 → 获取函数列表 → 生成执行计划JSONs

        Args:
            user_input: 用户输入的需求描述

        Returns:
            包含执行计划的字典，或包含错误信息的字典
        """
        try:
            LOGGER.info(f"🤖 开始分析用户需求: {user_input}")

            # 输入验证
            if not user_input or not user_input.strip():
                return {"error": "用户输入不能为空"}

            # 1. 获取所有可用插件
            available_plugins = await self._get_available_plugins()
            if not available_plugins:
                return {"error": "没有可用的插件", "suggestion": "请检查插件是否正确加载和启用"}

            # 2. AI筛选插件
            LOGGER.debug("🔍 开始筛选插件")
            selected_plugins: List[PluginSelectionMata] = await self._select_plugins(user_input, available_plugins)
            if not selected_plugins:
                return {"error": "未找到合适的插件", "available_plugins": [p["plugin_name"] for p in available_plugins]}

            # 3. 从筛选的插件中获取函数列表
            LOGGER.debug("🔍 开始获取插件函数列表")
            plugin_functions = await self._get_plugin_functions(selected_plugins, available_plugins)
            if not plugin_functions:
                return {"error": "未找到合适的函数", "selected_plugins": selected_plugins}

            # 4. 生成执行计划JSON
            LOGGER.debug("📝 开始生成执行计划")
            execution_plan = await self._generate_execution_plan(user_input, plugin_functions)

            if "error" in execution_plan:
                return execution_plan

            LOGGER.info("✅ 执行计划生成成功")
            return {
                "success": True,
                "user_input": user_input,
                "selected_plugins": selected_plugins,
                "plugin_functions": plugin_functions,
                "execution_plan": execution_plan
            }

        except Exception as e:
            LOGGER.exception(f"❌ 分析失败: {e}")
            return {"error": f"分析过程中发生错误: {str(e)}"}

    async def _call_ai_with_fallback(self, system_prompt: str, user_prompt: str,
                                     model=None) -> PluginsSelectionResponse:
        """
        使用AI管理器调用AI，支持备选方案

        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            **kwargs: 其他参数

        Returns:
            AI响应结果
        """
        try:
            # 如果指定了首选提供者，使用备选机制
            if self.preferred_provider:
                return await self.ai_manager.call_with_fallback(
                    primary_provider=self.preferred_provider,
                    fallback_providers=self.fallback_providers,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=model
                )
            else:
                # 使用最佳可用提供者
                return await self.ai_manager.call_best_available(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=model
                )

        except Exception as e:
            LOGGER.error(f"❌ AI调用失败: {e}")
            raise

    async def _get_available_plugins(self) -> List[Dict[str, Any]]:
        """获取所有可用插件信息"""
        try:
            plugins_info: List[Dict[str, Any]] = await self.plugin_manager.list_plugins()
            available_plugins = []

            for plugin in plugins_info:
                if plugin and plugin.get("is_enabled") and plugin.get("status") == "loaded":
                    available_plugins.append({
                        "plugin_id": plugin.get("id"),
                        "plugin_name": plugin.get("name", ""),
                        "description": plugin.get("description", ""),
                        "tags": plugin.get("tags", []),
                    })

            LOGGER.info(f"📋 发现 {len(available_plugins)} 个可用插件")
            return available_plugins

        except Exception as e:
            LOGGER.exception(f"❌ 获取插件信息失败: {e}")
            return []

    async def _select_plugins(self, user_input: str, available_plugins: List[Dict]) -> List[PluginSelectionMata]:
        """AI筛选插件"""
        try:
            # 构建插件基本信息
            plugins_basic_info = []
            for plugin in available_plugins:
                plugins_basic_info.append({
                    'plugin_name': plugin['plugin_name'],
                    'plugin_id': plugin['plugin_id'],
                    'description': plugin['description'],
                    'tags': plugin['tags']
                })

            # 使用AI筛选插件
            prompt: PromptResponse = self.prompt_templates.get_plugin_selection_prompt(plugins_basic_info, user_input)

            # 通过AI管理器调用AI
            response: PluginsSelectionResponse = await self._call_ai_with_fallback(
                system_prompt=prompt.system_prompt,
                user_prompt=prompt.user_prompt,
                model=self.model
            )

            if not response or not response.success:
                LOGGER.error(f"AI响应失败: {response}")
                return []

            data: PluginsSelection = response.data
            if data is None:
                return []

            selected_plugins: List[PluginSelectionMata] = data.selected_plugins
            LOGGER.info(f"🔌 筛选出 {len(selected_plugins)} 个插件")
            return selected_plugins

        except Exception as e:
            LOGGER.error(f"❌ 插件筛选失败: {e}")
            return []

    async def _generate_execution_plan(self, user_input: str, plugin_functions: List[Dict]) -> Dict[str, Any]:
        """生成执行计划JSON"""
        try:
            # 使用function_matching模板生成执行计划
            prompt: PromptResponse = self.prompt_templates.get_function_matching_prompt(plugin_functions, user_input)

            # 通过AI管理器调用AI
            response = await self._call_ai_with_fallback(
                system_prompt=prompt.system_prompt,
                user_prompt=prompt.user_prompt,
                model=self.model
            )

            if not response or not response.success:
                return {"error": f"AI响应失败: {response}"}

            # 解析AI响应
            execution_plan = self._parse_ai_response(response.data)
            if not execution_plan:
                return {"error": "解析执行计划失败"}

            LOGGER.info("📋 生成执行计划成功")
            return execution_plan

        except Exception as e:
            LOGGER.exception(f"❌ 生成执行计划失败: {e}")
            return {"error": f"生成执行计划时发生错误: {str(e)}"}

    def _parse_ai_response(self, content: str) -> Optional[Dict[str, Any]]:
        """解析AI响应内容"""
        try:
            if not content:
                LOGGER.error("AI返回的内容为空")
                return None

            # 尝试解析JSON
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

    async def _get_plugin_functions(self, selected_plugins: List[PluginSelectionMata], available_plugins: List[Dict]) -> \
    List[Dict]:
        """从筛选的插件中获取函数列表"""
        plugin_functions = []

        for selected_plugin in selected_plugins:
            try:
                plugin_id = selected_plugin.plugin_id
                if not plugin_id:
                    LOGGER.warning(f"插件缺少 plugin_id: {selected_plugin}")
                    continue

                # 找到完整插件信息
                full_plugin = next((p for p in available_plugins if p['plugin_id'] == plugin_id), None)
                if not full_plugin:
                    LOGGER.warning(f"未找到插件: {plugin_id}")
                    continue

                plugin_obj: Optional[PluginRegistration] = await self.plugin_manager.get_register_plugin(plugin_id)
                if not plugin_obj:
                    LOGGER.warning(f"无法获取插件对象: {plugin_id}")
                    continue

                # 提取插件的所有函数
                functions = await self._extract_plugin_functions(plugin_obj, full_plugin['plugin_name'])

                if functions:
                    plugin_functions.append({
                        'plugin_name': full_plugin['plugin_name'],
                        'plugin_id': full_plugin['plugin_id'],
                        'description': full_plugin['description'],
                        'functions': functions,
                        'selection_reason': selected_plugin.reason
                    })

            except Exception as e:
                LOGGER.exception(f"❌ 处理插件 {selected_plugin.get('plugin_id', 'unknown')} 时发生错误: {e}")
                continue

        LOGGER.info(f"🎯 获取到 {len(plugin_functions)} 个插件的函数列表")
        return plugin_functions

    async def _extract_plugin_functions(self, plugin_obj: PluginRegistration, plugin_name: str) -> List[Dict]:
        """提取插件函数信息"""
        functions = []

        for service in plugin_obj.plugin_services:
            service_function = service.functions
            try:
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
                            "full_method_name": f"{plugin_name}.{func.get('name')}"
                        })

            except Exception as e:
                LOGGER.warning(f"⚠️ 解析服务函数失败: {e}")
                continue

        return functions

    async def get_plugin_status(self) -> Dict[str, Any]:
        """获取插件状态摘要"""
        try:
            available_plugins = await self._get_available_plugins()
            all_plugins = await self.plugin_manager.list_plugins()

            return {
                "total_plugins": len(all_plugins),
                "available_plugins": len(available_plugins),
                "plugin_names": [p["plugin_name"] for p in available_plugins]
            }
        except Exception as e:
            LOGGER.error(f"❌ 获取插件状态失败: {e}")
            return {"error": str(e)}

    def get_ai_status(self) -> Dict[str, Any]:
        """获取AI管理器状态"""
        try:
            return {
                "available_providers": self.ai_manager.list_available_providers(),
                "provider_types": self.ai_manager.list_provider_types(),
                "health_status": self.ai_manager.health_check(),
                "preferred_provider": self.preferred_provider,
                "fallback_providers": self.fallback_providers
            }
        except Exception as e:
            LOGGER.error(f"❌ 获取AI状态失败: {e}")
            return {"error": str(e)}


# 测试函数
async def test_simple_case():
    """简单测试案例 - 快速验证"""
    print("🧪 运行简单测试案例...")

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

        # 检查状态
        ai_status = router.get_ai_status()
        plugin_status = await router.get_plugin_status()

        print(f"🤖 AI状态: {ai_status}")
        print(f"📊 插件状态: {plugin_status}")

        # 测试一个简单命令
        result = await router.analyze_and_plan("帮我拍一张照片")

        if "error" in result:
            print(f"❌ 简单测试失败: {result['error']}")
            if "suggestion" in result:
                print(f"💡 建议: {result['suggestion']}")
            return False

        print("✅ 简单测试通过!")
        print(f"筛选的插件数: {len(result.get('selected_plugins', []))}")
        print(f"可用函数数: {len(result.get('plugin_functions', []))}")

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

    asyncio.run(test_simple_case())


if __name__ == "__main__":
    main()
