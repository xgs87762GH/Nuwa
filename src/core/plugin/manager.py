"""
插件管理器
负责插件的整体生命周期管理，包括发现、加载、启动、停止等
"""
from typing import Dict, List, Optional
import asyncio
import structlog
from pathlib import Path

from .loader import PluginLoader
from .registry import PluginRegistry
from .discovery import PluginDiscovery
from .lifecycle import PluginLifecycle
from .validator import PluginValidator
from ...utils.config import get_config


class PluginManager:
    """插件管理器主类"""

    def __init__(self):
        self.logger = structlog.get_logger("plugin_manager")
        self.config = get_config().plugin_registry

        self.loader = PluginLoader()
        self.registry = PluginRegistry()
        self.discovery = PluginDiscovery()
        self.lifecycle = PluginLifecycle()
        self.validator = PluginValidator()

        self.plugins: Dict[str, any] = {}
        self._running = False

    async def start(self):
        """启动插件管理器"""
        self.logger.info("Starting plugin manager")
        self._running = True

        # 启动插件发现
        if self.config.auto_discovery:
            await self.discovery.start()

        # 加载已注册的插件
        await self._load_registered_plugins()

        # 启动健康检查
        asyncio.create_task(self._health_check_loop())

    async def stop(self):
        """停止插件管理器"""
        self.logger.info("Stopping plugin manager")
        self._running = False

        # 停止所有插件
        await self._stop_all_plugins()

        # 停止插件发现
        await self.discovery.stop()

    async def install_plugin(self, plugin_path: Path) -> bool:
        """安装新插件"""
        try:
            # 验证插件
            if not await self.validator.validate_plugin(plugin_path):
                return False

            # 加载插件
            plugin = await self.loader.load_plugin(plugin_path)
            if not plugin:
                return False

            # 注册插件
            await self.registry.register_plugin(plugin)

            # 启动插件
            await self.lifecycle.start_plugin(plugin)

            self.plugins[plugin.name] = plugin
            self.logger.info("Plugin installed successfully", plugin_name=plugin.name)
            return True

        except Exception as e:
            self.logger.error("Failed to install plugin", error=str(e))
            return False

    async def uninstall_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        try:
            plugin = self.plugins.get(plugin_name)
            if not plugin:
                return False

            # 停止插件
            await self.lifecycle.stop_plugin(plugin)

            # 从注册表移除
            await self.registry.unregister_plugin(plugin_name)

            # 从内存移除
            del self.plugins[plugin_name]

            self.logger.info("Plugin uninstalled successfully", plugin_name=plugin_name)
            return True

        except Exception as e:
            self.logger.error("Failed to uninstall plugin", plugin_name=plugin_name, error=str(e))
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

    async def _load_registered_plugins(self):
        """加载已注册的插件"""
        registered_plugins = await self.registry.get_all_plugins()
        for plugin_info in registered_plugins:
            try:
                plugin_path = Path(plugin_info["path"])
                if plugin_path.exists():
                    await self.install_plugin(plugin_path)
            except Exception as e:
                self.logger.error("Failed to load registered plugin",
                                plugin_name=plugin_info.get("name"), error=str(e))

    async def _stop_all_plugins(self):
        """停止所有插件"""
        tasks = []
        for plugin in self.plugins.values():
            tasks.append(self.lifecycle.stop_plugin(plugin))
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _health_check_loop(self):
        """健康检查循环"""
        while self._running:
            try:
                for plugin_name, plugin in self.plugins.items():
                    health_status = await self.lifecycle.check_health(plugin)
                    if not health_status:
                        self.logger.warning("Plugin health check failed", plugin_name=plugin_name)
                        # 可以在这里实现重启逻辑

                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(10)
