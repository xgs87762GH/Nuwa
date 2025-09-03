import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionUserMessageParam
from openai.types.shared_params import ResponseFormatJSONObject

from src.core.plugin import PluginManager
from src.core.plugin.model import PluginRegistration
from src.core.utils.template import EnhancedPromptTemplates

# 配置信息
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_KEY = "sk-xxxxxx"

client = AsyncOpenAI(api_key=OPENAI_KEY)
LOGGER = logging.getLogger(__name__)


class IntelligentPluginRouter:
    """智能插件路由器 - AI理解用户需求并生成执行计划"""

    def __init__(self, plugin_manager: PluginManager, template_dir: str = None, user_name: str = "Gordon"):
        self.plugin_manager = plugin_manager

        # 如果没有提供 template_dir，使用默认路径
        if template_dir is None:
            # 获取项目根目录下的 templates/prompts 目录
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent  # 向上4级到达项目根目录
            template_dir = str(project_root / "templates" / "prompts")

        self.prompt_templates = EnhancedPromptTemplates(template_dir, user_name)

    async def analyze_and_plan(self, user_input: str) -> Dict[str, Any]:
        """
        分析用户输入并生成执行计划

        流程：用户输入 → AI意图分析 → 插件筛选 → 获取函数列表 → 生成执行计划JSONs
        """
        try:
            LOGGER.info(f"🤖 开始分析用户需求: {user_input}")

            # 1. 获取所有可用插件
            available_plugins = await self._get_available_plugins()
            if not available_plugins:
                return {"error": "没有可用的插件"}

            # 2. AI筛选插件
            LOGGER.debug(f"🔍 开始筛选插件====================")
            selected_plugins = await self._select_plugins(user_input, available_plugins)
            if not selected_plugins:
                return {"error": "未找到合适的插件"}

            # 3. 从筛选的插件中获取函数列表
            LOGGER.debug(f"🔍 开始获取插件函数列表====================")
            plugin_functions = await self._get_plugin_functions(selected_plugins, available_plugins)
            if not plugin_functions:
                return {"error": "未找到合适的函数"}

            # 4. 生成执行计划JSON
            LOGGER.debug(f"📝 开始生成执行计划====================")
            execution_plan = await self._generate_execution_plan(user_input, plugin_functions)

            LOGGER.debug(f"📝 执行计划: {execution_plan}", extra=execution_plan)
            return {
                "user_input": user_input,
                "selected_plugins": selected_plugins,
                "plugin_functions": plugin_functions,
                "execution_plan": execution_plan
            }

        except Exception as e:
            LOGGER.exception(e)
            LOGGER.error(f"❌ 分析失败: {e}")
            return {"error": str(e)}

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
            LOGGER.exception(e)
            LOGGER.error(f"❌ 获取插件信息失败: {e}")
            return []

    async def _select_plugins(self, user_input: str, available_plugins: List[Dict]) -> List[Dict]:
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
            system_prompt = self.prompt_templates.get_plugin_selection_prompt(plugins_basic_info)
            user_prompt = f"用户需求: {user_input}\n请分析用户意图，筛选出最适合的插件。"

            completion = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    ChatCompletionSystemMessageParam(role="system", content=system_prompt),
                    ChatCompletionUserMessageParam(role="user", content=user_prompt)
                ],
                response_format=ResponseFormatJSONObject(type="json_object"),
                temperature=0.7,
                max_tokens=1500
            )

            result = json.loads(completion.choices[0].message.content)
            selected_plugins = result.get("selected_plugins", [])

            LOGGER.info(f"🔌 筛选出 {len(selected_plugins)} 个插件")
            return selected_plugins

        except Exception as e:
            LOGGER.error(f"❌ 插件筛选失败: {e}")
            return []

    async def _get_plugin_functions(self, selected_plugins: List[Dict], available_plugins: List[Dict]) -> List[Dict]:
        """从筛选的插件中获取函数列表"""
        plugin_functions = []

        for selected_plugin in selected_plugins:
            plugin_id = selected_plugin.get('plugin_id')

            # 找到完整插件信息
            full_plugin = next((p for p in available_plugins if p['plugin_id'] == plugin_id), None)
            if not full_plugin:
                continue

            plugin_obj: Optional[PluginRegistration] = await self.plugin_manager.get_register_plugin(plugin_id)

            # 提取插件的所有函数
            functions = []
            for service in plugin_obj.plugin_services:
                service_function = service.functions
                try:
                    if service_function and callable(service_function):
                        functions_list: List[Dict[str, Any]] = service_function()
                        if not functions_list:
                            continue

                        if isinstance(functions_list, str):
                            functions_list = json.loads(functions_list)

                        for func in functions_list:
                            functions.append({
                                "name": func.get("name"),
                                "description": func.get("description"),
                                "input_schema": func.get("input_schema", {}),
                                "full_method_name": f"{full_plugin['plugin_name']}.{func.get('name')}"
                            })
                    elif service_function and isinstance(service_function, list):
                        for func in service_function:
                            functions.append({
                                "name": func.get("name"),
                                "description": func.get("description"),
                                "input_schema": func.get("input_schema", {}),
                                "full_method_name": f"{full_plugin['plugin_name']}.{func.get('name')}"
                            })
                except Exception as e:
                    LOGGER.exception(e)
                    LOGGER.warning(f"⚠️ 解析服务函数失败: {e}")

            if functions:
                plugin_functions.append({
                    'plugin_name': full_plugin['plugin_name'],
                    'plugin_id': full_plugin['plugin_id'],
                    'description': full_plugin['description'],
                    'functions': functions,
                    'selection_reason': selected_plugin.get('reason', '')
                })

        LOGGER.info(f"🎯 获取到 {len(plugin_functions)} 个插件的函数列表")
        return plugin_functions

    async def _generate_execution_plan(self, user_input: str, plugin_functions: List[Dict]) -> Dict[str, Any]:
        """生成执行计划JSON"""
        try:
            # 使用function_matching模板生成执行计划
            system_prompt = self.prompt_templates.get_function_matching_prompt(plugin_functions, user_input)
            user_prompt = f"基于用户需求: {user_input}\n请从可用函数中选择合适的函数并生成执行计划JSON。"

            messages: List[ChatCompletionMessageParam] = [
                ChatCompletionSystemMessageParam(role="system", content=system_prompt),
                ChatCompletionUserMessageParam(role="user", content=user_prompt)
            ]
            completion = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                response_format=ResponseFormatJSONObject(type="json_object"),
                temperature=0.5,
                max_tokens=2000
            )

            execution_plan = json.loads(completion.choices[0].message.content)
            LOGGER.info(f"📋 生成执行计划成功")
            return execution_plan

        except Exception as e:
            LOGGER.exception(e)
            LOGGER.error(f"❌ 生成执行计划失败: {e}")
            return {"error": str(e)}


async def test_simple_case():
    """简单测试案例 - 快速验证"""
    print("🧪 运行简单测试案例...")

    mock_plugin_manager = PluginManager()
    await mock_plugin_manager.start()
    router = IntelligentPluginRouter(plugin_manager=mock_plugin_manager)

    # 测试一个简单命令
    result = await router.analyze_and_plan("帮我拍一张照片")

    if "error" in result:
        print(f"❌ 简单测试失败: {result['error']}")
        return False

    print("✅ 简单测试通过!")
    print(f"筛选的插件数: {len(result.get('selected_plugins', []))}")
    print(f"可用函数数: {len(result.get('plugin_functions', []))}")

    return True


def main():
    """主函数"""
    print("🚀 启动智能插件路由器测试程序")
    print(f"当前时间: 2025-09-03 06:58:36 UTC")
    print(f"当前用户: Gordon")
    asyncio.run(test_simple_case())


if __name__ == "__main__":
    main()
