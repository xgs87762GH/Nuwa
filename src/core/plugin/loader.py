"""
插件加载器
负责动态加载和实例化插件模块
"""
import importlib.util
import sys
from pathlib import Path
from typing import Optional, Any
import structlog
import json

from .validator import PluginValidator


class PluginLoader:
    """插件加载器类"""

    def __init__(self):
        self.logger = structlog.get_logger("plugin_loader")
        self.validator = PluginValidator()

    async def load_plugin(self, plugin_path: Path) -> Optional[Any]:
        """加载插件

        Args:
            plugin_path: 插件目录路径

        Returns:
            加载的插件实例，失败返回None
        """
        try:
            # 验证插件结构
            if not await self._validate_plugin_structure(plugin_path):
                return None

            # 读取插件清单
            manifest = await self._load_manifest(plugin_path)
            if not manifest:
                return None

            # 加载插件模块
            plugin_module = await self._load_plugin_module(plugin_path, manifest)
            if not plugin_module:
                return None

            # 创建插件实例
            plugin_instance = await self._create_plugin_instance(plugin_module, manifest)

            self.logger.info("Plugin loaded successfully",
                           plugin_name=manifest.get("name"),
                           plugin_version=manifest.get("version"))

            return plugin_instance

        except Exception as e:
            self.logger.error("Failed to load plugin",
                            plugin_path=str(plugin_path),
                            error=str(e))
            return None

    async def _validate_plugin_structure(self, plugin_path: Path) -> bool:
        """验证插件目录结构"""
        required_files = ["manifest.json", "main.py"]

        for file_name in required_files:
            file_path = plugin_path / file_name
            if not file_path.exists():
                self.logger.error("Missing required file",
                                file_path=str(file_path))
                return False

        return True

    async def _load_manifest(self, plugin_path: Path) -> Optional[dict]:
        """加载插件清单文件"""
        try:
            manifest_path = plugin_path / "manifest.json"
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            # 验证清单格式
            if await self.validator.validate_manifest(manifest):
                return manifest
            else:
                self.logger.error("Invalid manifest format",
                                plugin_path=str(plugin_path))
                return None

        except Exception as e:
            self.logger.error("Failed to load manifest",
                            plugin_path=str(plugin_path),
                            error=str(e))
            return None

    async def _load_plugin_module(self, plugin_path: Path, manifest: dict) -> Optional[Any]:
        """加载插件Python模块"""
        try:
            entry_point = manifest.get("entry_point", "main.py")
            module_path = plugin_path / entry_point

            if not module_path.exists():
                self.logger.error("Entry point not found",
                                entry_point=entry_point,
                                plugin_path=str(plugin_path))
                return None

            # 动态导入模块
            spec = importlib.util.spec_from_file_location(
                f"plugin_{manifest['name']}",
                module_path
            )

            if spec is None or spec.loader is None:
                self.logger.error("Failed to create module spec",
                                module_path=str(module_path))
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            return module

        except Exception as e:
            self.logger.error("Failed to load plugin module",
                            plugin_path=str(plugin_path),
                            error=str(e))
            return None

    async def _create_plugin_instance(self, module: Any, manifest: dict) -> Optional[Any]:
        """创建插件实例"""
        try:
            # 查找插件主类
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class is None:
                self.logger.error("Plugin class not found in module")
                return None

            # 创建插件实例
            plugin_instance = plugin_class(manifest)

            # 设置插件属性
            plugin_instance.name = manifest["name"]
            plugin_instance.version = manifest["version"]
            plugin_instance.description = manifest["description"]
            plugin_instance.capabilities = manifest.get("capabilities", [])
            plugin_instance.status = "loaded"

            return plugin_instance

        except Exception as e:
            self.logger.error("Failed to create plugin instance",
                            plugin_name=manifest.get("name"),
                            error=str(e))
            return None

    async def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件模块"""
        try:
            module_name = f"plugin_{plugin_name}"
            if module_name in sys.modules:
                del sys.modules[module_name]
                self.logger.info("Plugin module unloaded", plugin_name=plugin_name)
                return True
            return False

        except Exception as e:
            self.logger.error("Failed to unload plugin module",
                            plugin_name=plugin_name,
                            error=str(e))
            return False
