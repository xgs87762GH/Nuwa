# Plugin Discovery Module
import importlib.util
import os
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set, Optional, Any, List

from src.core.utils.global_tools import project_root


@dataclass
class PluginDiscoveryResult:
    name: str  # 插件名称
    path: str  # 插件目录绝对路径
    entry_file: str  # 插件主入口文件（如 __init__.py 或 main.py）
    plugin_class: Any  # 插件注册类（如 CameraPlugin）
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 插件唯一标识符（UUID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 插件元信息（如 METADATA）
    config: Dict[str, Any] = field(default_factory=dict)  # 插件配置（如 PLUGIN_CONFIG）
    tools: Optional[str] = None  # 插件工具列表
    requirements: Optional[List[str]] = None  # Python依赖包
    tags: Optional[List[str]] = None  # 插件标签
    category: Optional[str] = None  # 插件分类
    permissions: Optional[List[str]] = None  # 插件权限声明
    load_status: Optional[str] = "pending"  # 加载状态（pending/loaded/failed）
    error: Optional[str] = None  # 加载失败原因
    discovered_at: Optional[str] = None  # 发现时间戳


class PluginDiscovery:

    def __init__(self, plugins_root: str = f"{project_root()}/plugins"):
        self.plugins_root = Path(plugins_root)
        self.discovered_plugins: Dict[str, PluginDiscoveryResult] = {}
        self.failed_plugins: Set[str] = set()

    def scan_all_plugins(self) -> Dict[str, PluginDiscoveryResult]:
        if not self.plugins_root.exists():
            print(f"Plugins directory {self.plugins_root} does not exist.")
            return {}

        for plugin_dir in self.plugins_root.iterdir():
            if plugin_dir.is_dir():
                plugin_path = str(plugin_dir.resolve())
                if plugin_path not in sys.path:
                    sys.path.insert(0, plugin_path)
                init_path = plugin_dir / "__init__.py"
                main_path = plugin_dir / "main.py"
                entry_path = init_path if init_path.exists() else (main_path if main_path.exists() else None)
                if entry_path:
                    module_name = f"plugin_{plugin_dir.name.replace('-', '_')}_{uuid.uuid4().hex}"
                    spec = importlib.util.spec_from_file_location(module_name, entry_path)
                    plugin_module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(plugin_module)
                        sys.modules[module_name] = plugin_module

                        for cls_name in getattr(plugin_module, "__all__", []):
                            plugin_class = getattr(plugin_module, cls_name)

                            metadata = plugin_class.METADATA() if hasattr(plugin_class, "METADATA") else {}
                            config = plugin_class.PLUGIN_CONFIG() if hasattr(plugin_class, "PLUGIN_CONFIG") else {}
                            tools = plugin_class.FUNCTIONS() if hasattr(plugin_class, "FUNCTIONS") else []
                            requirements = metadata.get("requirements", [])
                            tags = metadata.get("tags", [])
                            category = metadata.get("category", "")
                            permissions = metadata.get("permissions", [])

                            result = PluginDiscoveryResult(
                                name=metadata.get("id", plugin_dir.name),
                                path=str(plugin_dir.resolve()),
                                entry_file=entry_path.name,
                                plugin_class=plugin_class,
                                metadata=metadata,
                                config=config,
                                tools=tools,
                                requirements=requirements,
                                tags=tags,
                                category=category,
                                permissions=permissions,
                                load_status="loaded"
                            )
                            self.discovered_plugins[metadata.get("id", result.id)] = result
                    except Exception as e:
                        self.failed_plugins.add(plugin_dir.name)
                        self.discovered_plugins[plugin_dir.name] = PluginDiscoveryResult(
                            name=plugin_dir.name,
                            path=str(plugin_dir.resolve()),
                            entry_file=entry_path.name,
                            plugin_class=None,
                            load_status="failed",
                            error=str(e)
                        )
        return self.discovered_plugins

if __name__ == '__main__':
    discovery = PluginDiscovery()
    plugins = discovery.scan_all_plugins()
    for plugin_id, result in plugins.items():
        print(f"Plugin ID: {plugin_id}, Status: {result.name}, Error: {result.error}")
        print(result)
        print(result.tools)

