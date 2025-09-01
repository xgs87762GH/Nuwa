# Plugin Registry Module
from src.core.plugin.model.plugins import PluginRegistration


class PluginRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, plugin: PluginRegistration):
        if plugin.path is None:
            raise ValueError("Plugin path cannot be None.")

        # Check if a plugin with the same path already exists.
        exist_plugin = self._get_plugin_by_path(plugin.path)
        if exist_plugin:
            self.unregister(exist_plugin.id)
            plugin.id = exist_plugin.id

        plugin_id = plugin.id
        if plugin_id in self._registry:
            raise ValueError(f"Plugin {plugin_id} is already registered.")
        self._registry[plugin_id] = plugin

    def unregister(self, plugin_id: str):
        if plugin_id not in self._registry:
            raise KeyError(f"Plugin {plugin_id} is not registered.")
        del self._registry[plugin_id]

    def get_plugin(self, plugin_id: str) -> PluginRegistration:
        return self._registry.get(plugin_id)

    async def list_plugins(self) -> list[str]:
        return list(self._registry.keys())

    def _get_plugin_by_path(self, path: str):
        for plugin in self._registry.values():
            if plugin.path == path:
                return plugin
        return None
