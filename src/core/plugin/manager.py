# # """
# # 插件管理器
# # 负责插件的整体生命周期管理，包括发现、加载、启动、停止等
# # """
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

#
import structlog

from src.core.config.logger import setup_logging
from src.core.plugin.model import PluginRegistration
from src.core.config import get_plugin_config, PluginConfig
from src.core.plugin import PluginDiscovery, PluginLoader, PluginRegistry


class PluginManager:
    """插件管理器主类"""

    def __init__(self):
        self.logger = structlog.get_logger("plugin_manager")
        self.discovery = PluginDiscovery()
        self.config: PluginConfig = get_plugin_config()

        self.loader = PluginLoader()
        self.registry = PluginRegistry()
        self.discovery = PluginDiscovery()
        self._running = False

    async def start(self):
        """启动插件管理器"""
        self.logger.info("Starting plugin manager")
        self._running = True

        # 启动插件发现
        if self.config.auto_discovery:
            await self.discovery.start()
            for plugin_result in self.discovery.plugins:
                plugin_registration = self.loader.load_plugin(plugin_result)
                self.registry.register(plugin_registration)

        # 启动健康检查
        asyncio.create_task(self._health_check_loop())

    async def stop(self):
        """停止插件管理器"""
        self.logger.info("Stopping plugin manager")
        self._running = False
        # 停止插件发现
        await self.discovery.stop()

    async def install_plugin(self, plugin_path: Path) -> bool:
        """安装/更新 新插件"""
        await self.discovery.start()
        for plugin_result in self.discovery.plugins:
            if plugin_result.path == plugin_path:
                plugin_registration = self.loader.load_plugin(plugin_result)
                self.registry.register(plugin_registration)
                return True
        return False

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        try:
            plugin: PluginRegistration = self.plugins.get(plugin_id)
            if not plugin:
                return False
            # 从注册表移除
            await self.registry.unregister(plugin_id)

            self.logger.info("Plugin uninstalled successfully", plugin_name=plugin.name)
            return True

        except Exception as e:
            self.logger.error("Failed to uninstall plugin", plugin_id=plugin_id, error=str(e))
            return False

    async def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """获取插件信息"""
        plugin = self.plugins.get(plugin_name)
        if plugin:
            return {
                "name": plugin.name,
                "version": plugin.version,
                "status": plugin.status,
                "description": plugin.description,
                "capabilities": plugin.capabilities
            }
        return None

    async def list_plugins(self) -> List[Dict]:
        """列出所有插件"""
        return [await self.get_plugin_info(name) for name in self.plugins.keys()]

    async def _health_check_loop(self):
        """健康检查循环"""
        # while self._running:
        #     try:
        #         for plugin_name, plugin in self.plugins.items():
        #         # health_status = await self.lifecycle.check_health(plugin)
        #         # if not health_status:
        #         #     self.logger.warning("Plugin health check failed", plugin_name=plugin_name)
        #         # 可以在这里实现重启逻辑
        #
        #         await asyncio.sleep(self.config.health_check_interval)
        #     except Exception as e:
        #         self.logger.error("Health check loop error", error=str(e))
        #         await asyncio.sleep(10)


async def main():
    setup_logging()
    manager = PluginManager()
    await manager.start()
    plugin_ids: list[str] = await manager.registry.list_plugins()
    for id in plugin_ids:
        plugin: PluginRegistration = manager.registry.get_plugin(id)
        logging.info(f"Loaded plugin: {plugin.name} at {plugin.path}")


if __name__ == '__main__':
    asyncio.run(main())
