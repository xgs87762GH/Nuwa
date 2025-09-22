from src.core.ai import AIManager
from src.core.ai.providers.response import PluginsSelection, ExecutionPlan


class PlanService:
    def __init__(self, prompt_templates, ai_manager: AIManager):
        self.prompt_templates = prompt_templates
        self.ai_manager: AIManager = ai_manager
        self.primary_provider = None
        self.fallback_providers = None
        self.choose_model = None

    async def select_plugins(self, user_input, available_plugins):
        plugins_basic_info = [
            {
                'plugin_name': p['plugin_name'],
                'plugin_id': p['plugin_id'],
                'description': p['description'],
                'tags': p['tags']
            }
            for p in available_plugins
        ]
        prompt = self.prompt_templates.get_plugin_selection_prompt(plugins_basic_info, user_input)
        response = await self.ai_manager.call_with_fallback(
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
            primary_provider=self.primary_provider,
            fallback_providers=self.fallback_providers,
            model=self.choose_model
        )
        if not response or not response.success:
            return []
        data = PluginsSelection.from_content(response.data)
        if data is None:
            return []
        return data.selected_plugins

    async def generate_execution_plan(self, user_input, plugin_functions) -> ExecutionPlan | None:
        prompt = self.prompt_templates.get_function_matching_prompt(plugin_functions, user_input)
        response = await self.ai_manager.call_with_fallback(
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
        )
        if not response or not response.success:
            return None
        execution_plan = ExecutionPlan.from_content(response.data)
        return execution_plan
