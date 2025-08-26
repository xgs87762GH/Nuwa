# Plugin Registry Module

class PluginRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, plugin_name: str, plugin_instance: object):
        if plugin_name in self._registry:
            raise ValueError(f"Plugin {plugin_name} is already registered.")
        self._registry[plugin_name] = plugin_instance

    def unregister(self, plugin_name: str):
        if plugin_name not in self._registry:
            raise KeyError(f"Plugin {plugin_name} is not registered.")
        del self._registry[plugin_name]

    def get_plugin(self, plugin_name: str) -> object:
        return self._registry.get(plugin_name)

    def list_plugins(self) -> list:
        return list(self._registry.keys())

