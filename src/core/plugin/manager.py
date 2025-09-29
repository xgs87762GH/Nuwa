"""
Plugin Manager
Responsible for the overall lifecycle management of plugins, including discovery, loading, starting, stopping, etc.
"""
import asyncio
from asyncio import iscoroutinefunction
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import get_plugin_config, PluginConfig, get_logger
from src.core.plugin import PluginDiscovery, PluginLoader, PluginRegistry
from src.core.plugin.model import PluginRegistration, PluginInfoProviderDefinition
from src.core.utils.result import Result

LOGGER = get_logger("PluginManager")


class PluginManager:
    """Main plugin manager class"""

    def __init__(self):
        self.discovery = PluginDiscovery()
        self.config: PluginConfig = get_plugin_config()

        self.loader = PluginLoader()
        self.registry = PluginRegistry()
        self._running = False

    async def start(self):
        """Start the plugin manager"""
        LOGGER.info("Starting plugin manager")
        self._running = True

        # Start plugin discovery
        if self.config.auto_discovery:
            await self.discovery.start()
            for plugin_result in self.discovery.plugins:
                plugin_registration = self.loader.load_plugin(plugin_result)
                self.registry.register(plugin_registration)

        # Start health check
        asyncio.create_task(self._health_check_loop())

    async def reload(self):
        """Reload all plugins"""
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        LOGGER.info("Reloading all plugins")
        await self.registry.clean_all()
        LOGGER.info(f"Plugin manager reloaded: {self.registry.list_plugins()}")
        if self.config.auto_discovery:
            await self.discovery.reload()
            for plugin_result in self.discovery.plugins:
                plugin_registration = self.loader.load_plugin(plugin_result)
                self.registry.register(plugin_registration)

    async def stop(self):
        """Stop the plugin manager"""
        LOGGER.info("Stopping plugin manager")
        self._running = False

        # Stop discovery
        await self.discovery.stop()

    async def install_plugin(self, plugin_path: Path) -> bool:
        """Install/Update a new plugin"""
        await self.discovery.start()
        for plugin_result in self.discovery.plugins:
            if plugin_result.path == plugin_path:
                plugin_registration = self.loader.load_plugin(plugin_result)
                self.registry.register(plugin_registration)
                return True
        return False

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        try:
            # Remove from registry
            await self.registry.unregister(plugin_id)
            LOGGER.info(f"Plugin {plugin_id} uninstalled successfully")
            return True
        except Exception as e:
            LOGGER.error(f"Error uninstalling plugin {plugin_id}, error: {str(e)}")
            return False

    # ===== New: Result-wrapped variants (non-breaking) =====
    async def call(self, plugin: PluginRegistration, method_name: str, **kwargs) -> Result:
        """Call a plugin by id and wrap the outcome into Result. Does not modify original call()."""
        try:
            services: List[PluginInfoProviderDefinition] = plugin.plugin_services
            for service in services:
                functions = service.functions() if callable(service.functions) else service.functions
                for fun in functions:
                    if method_name == (fun.get('name') if isinstance(fun, dict) else getattr(fun, 'name', None)):
                        # Whether await is needed depends on whether the method itself is a coroutine function or not
                        instance = service.instance()
                        if iscoroutinefunction(getattr(instance, method_name)):
                            result = await getattr(instance, method_name)(**kwargs)
                        else:
                            result = getattr(instance, method_name)(**kwargs)
                        return Result.ok(result)

            raise Exception(f"Method '{method_name}' not found in plugin '{plugin.id}'")
        except Exception as e:
            LOGGER.error(f"Error calling plugin {plugin.id} method {method_name}: {str(e)}")
            raise e

    async def get_plugin_info(self, plugin_id: str) -> Optional[PluginRegistration]:
        """Get plugin information"""
        plugin: PluginRegistration = self.registry.get_plugin(plugin_id)
        return plugin

    async def get_plugin_by_id(self, plugin_id: str) -> Optional[PluginRegistration]:
        """根据插件ID获取完整的插件注册对象"""
        return self.registry.get_plugin(plugin_id)

    async def get_plugin_by_name(self, plugin_name: str) -> Optional[PluginRegistration]:
        """根据插件名称获取完整的插件注册对象"""
        return self.registry.get_plugin_by_name(plugin_name)

    async def list_plugins(self) -> List[PluginRegistration]:
        """List all registered plugins with their status"""
        keys: List[str] = await self.registry.list_plugins()
        return [await self.get_plugin_info(id) for id in keys]

    async def list_available_plugins(self) -> List[PluginRegistration]:
        """List all available plugins (enabled and loaded)"""
        all_plugins = await self.list_plugins()
        available_plugins = []
        for plugin in all_plugins:
            if (plugin.load_status == "loaded" and plugin.is_enabled):
                available_plugins.append(plugin)
        return available_plugins

    async def _health_check_loop(self):
        """Periodic health check for all plugins"""
        pass


async def main():
    """Main function for testing plugin manager"""
    manager = PluginManager()
    await manager.start()

    plugins = await manager.list_plugins()
    if plugins:
        for plugin in plugins:
            LOGGER.info(f"Plugin: {plugin}")


if __name__ == '__main__':
    asyncio.run(main())
