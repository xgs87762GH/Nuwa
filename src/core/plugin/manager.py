"""
Plugin Manager
Responsible for the overall lifecycle management of plugins, including discovery, loading, starting, stopping, etc.
"""
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import get_plugin_config, PluginConfig, get_logger
from src.core.plugin import PluginDiscovery, PluginLoader, PluginRegistry
from src.core.plugin.model import PluginRegistration

logger = get_logger("PluginManager")


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
        logger.info("Starting plugin manager")
        self._running = True

        # Start plugin discovery
        if self.config.auto_discovery:
            await self.discovery.start()
            for plugin_result in self.discovery.plugins:
                plugin_registration = self.loader.load_plugin(plugin_result)
                self.registry.register(plugin_registration)

        # Start health check
        asyncio.create_task(self._health_check_loop())

    async def stop(self):
        """Stop the plugin manager"""
        logger.info("Stopping plugin manager")
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
            logger.info(f"Plugin {plugin_id} uninstalled successfully")
            return True
        except Exception as e:
            logger.error(f"Error uninstalling plugin {plugin_id}, error: {str(e)}")
            return False

    async def get_plugin_info(self, plugin_id: str) -> Optional[Dict]:
        """Get plugin information"""
        plugin = self.registry.get_plugin(plugin_id)
        if plugin:
            return {
                "id": plugin.id,
                "name": plugin.name,
                "version": plugin.version,
                "status": plugin.load_status,
                "description": plugin.description,
                "registered_at": plugin.registered_at,
                "is_enabled": plugin.is_enabled,
                "tags": plugin.tags
            }
        return None

    async def get_register_plugin(self, plugin_id: str) -> Optional[PluginRegistration]:
        """Get the full plugin registration object"""
        return self.registry.get_plugin(plugin_id)

    async def list_plugins(self) -> List[Dict]:
        """List all registered plugins with their status"""
        keys: List[str] = await self.registry.list_plugins()
        return [await self.get_plugin_info(id) for id in keys]

    async def _health_check_loop(self):
        """Periodic health check for all plugins"""


async def main():
    """Main function for testing plugin manager"""
    manager = PluginManager()
    await manager.start()

    plugins = await manager.list_plugins()
    if plugins:
        for plugin in plugins:
            logger.info(f"Plugin: {plugin}")

if __name__ == '__main__':
    asyncio.run(main())
