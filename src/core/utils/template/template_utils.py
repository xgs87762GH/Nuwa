"""
模板变量处理工具类 - 只负责变量替换，不涉及文件读取和业务逻辑
"""

from string import Template
from typing import Dict, Any
from datetime import datetime, timezone
from .template_manager import TemplateManager


class TemplateVariableProcessor:
    """模板变量处理器 - 只负责变量替换"""

    def __init__(self, user_name: str = "Gordon"):
        self.user_name = user_name

    def get_global_variables(self) -> Dict[str, Any]:
        """
        获取全局模板变量
        """
        now_utc = datetime.now(timezone.utc)
        return {
            'current_date_time': now_utc.strftime("%Y-%m-%d %H:%M:%S"),
            'current_date_time_utc': "2025-09-03 06:00:59",  # 使用提供的时间
            'current_user_login': self.user_name,
            'current_year': now_utc.year,
            'current_date': now_utc.strftime("%Y-%m-%d"),
            'current_time': now_utc.strftime("%H:%M:%S"),
            'timezone': 'UTC'
        }

    def render_string_template(self, template_content: str, variables: Dict[str, Any] = None) -> str:
        """
        渲染字符串模板
        """
        template = Template(template_content)
        all_variables = self.get_global_variables()
        if variables:
            all_variables.update(variables)
        try:
            return template.safe_substitute(all_variables)
        except Exception:
            return template_content


class EnhancedPromptTemplates:
    """
    业务模板渲染器：通过 TemplateManager 读取模板文件，通过 TemplateVariableProcessor 替换变量
    """
    def __init__(self, template_dir: str, user_name: str = "Gordon"):
        self.template_manager = TemplateManager(template_dir)
        self.variable_processor = TemplateVariableProcessor(user_name)

    def render_prompt(self, template_name: str, variables: dict = None) -> str:
        template_content = self.template_manager.load_template(template_name)
        if not template_content:
            return ""
        return self.variable_processor.render_string_template(template_content, variables)

    def get_plugin_selection_prompt(self, plugins_basic_info: list) -> str:
        return self.render_prompt("plugin_selection", {"plugins_description": plugins_basic_info})

    def get_function_matching_prompt(self, plugin_functions: list, user_input: str) -> str:
        return self.render_prompt("function_matching", {
            "plugins_with_functions": plugin_functions,
            "user_input": user_input
        })
