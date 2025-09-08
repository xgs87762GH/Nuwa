from src.core.plugin.model import PluginRegistration
import json

class PluginService:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager

    async def get_available_plugins(self):
        plugins_info = await self.plugin_manager.list_plugins()
        return [
            {
                "plugin_id": p.get("id"),
                "plugin_name": p.get("name", ""),
                "description": p.get("description", ""),
                "tags": p.get("tags", []),
            }
            for p in plugins_info
            if p.get("is_enabled") and p.get("status") == "loaded"
        ]

    async def get_plugin_functions(self, selected_plugins, available_plugins):
        plugin_functions = []
        for selected_plugin in selected_plugins:
            plugin_id = selected_plugin.plugin_id
            full_plugin = next((p for p in available_plugins if p['plugin_id'] == plugin_id), None)
            plugin_obj = await self.plugin_manager.get_register_plugin(plugin_id)
            if not plugin_obj or not full_plugin:
                continue
            functions = await self.extract_plugin_functions(plugin_obj, full_plugin['plugin_name'])
            if functions:
                plugin_functions.append({
                    'plugin_name': full_plugin['plugin_name'],
                    'plugin_id': full_plugin['plugin_id'],
                    'description': full_plugin['description'],
                    'functions': functions,
                    'selection_reason': selected_plugin.reason
                })
        return plugin_functions

    async def extract_plugin_functions(self, plugin_obj: PluginRegistration, plugin_name: str):
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
                        "full_method_name": f"{plugin_name}.{func.get('name')}"
                    })
        return functions