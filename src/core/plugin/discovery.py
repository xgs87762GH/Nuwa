# Plugin Discovery Module
import importlib.util
import os
import sys
import uuid
from pathlib import Path
from typing import List

from model.plugins import PluginDiscoveryResult
from src.core.utils.global_tools import project_root


class PluginDiscovery:

    def __init__(self, plugins_root: str = f"{project_root()}/plugins"):
        self.plugins_root = Path(plugins_root)
        # self.discovered_plugins: Dict[str, PluginDiscoveryResult] = {}
        # self.failed_plugins: Set[str] = set()

        self.plugins: List[PluginDiscoveryResult] = []

    def scan_plugins(self):
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
                    spec = importlib.util.spec_from_file_location(module_name, entry_path,
                                                                  submodule_search_locations=[plugin_path])
                    plugin_module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(plugin_module)
                        sys.modules[module_name] = plugin_module

                        plugin_classes = []
                        for cls_name in getattr(plugin_module, "__all__", []):
                            plugin_class = getattr(plugin_module, cls_name)
                            plugin_classes.append(plugin_class)
                        self.plugins.append(
                            PluginDiscoveryResult(
                                # name=cls_name,
                                path=plugin_path,
                                entry_file=entry_path,
                                plugin_classes=plugin_classes,
                            )
                        )
                    except Exception as e:
                        e.with_traceback()
                        print(f"Failed to load plugin {plugin_dir.name}: {e}")

    # def scan_all_plugins(self) -> Dict[str, PluginDiscoveryResult]:
    #     if not self.plugins_root.exists():
    #         print(f"Plugins directory {self.plugins_root} does not exist.")
    #         return {}
    #
    #     for plugin_dir in self.plugins_root.iterdir():
    #         if plugin_dir.is_dir():
    #             plugin_path = str(plugin_dir.resolve())
    #             if plugin_path not in sys.path:
    #                 sys.path.insert(0, plugin_path)
    #             init_path = plugin_dir / "__init__.py"
    #             main_path = plugin_dir / "main.py"
    #             entry_path = init_path if init_path.exists() else (main_path if main_path.exists() else None)
    #             if entry_path:
    #                 module_name = f"plugin_{plugin_dir.name.replace('-', '_')}_{uuid.uuid4().hex}"
    #                 spec = importlib.util.spec_from_file_location(module_name, entry_path)
    #                 plugin_module = importlib.util.module_from_spec(spec)
    #                 try:
    #                     spec.loader.exec_module(plugin_module)
    #                     sys.modules[module_name] = plugin_module
    #
    #                     for cls_name in getattr(plugin_module, "__all__", []):
    #                         plugin_class = getattr(plugin_module, cls_name)
    #
    #                         metadata = plugin_class.METADATA() if hasattr(plugin_class, "METADATA") else {}
    #                         config = plugin_class.PLUGIN_CONFIG() if hasattr(plugin_class, "PLUGIN_CONFIG") else {}
    #                         tools = plugin_class.FUNCTIONS() if hasattr(plugin_class, "FUNCTIONS") else []
    #                         requirements = metadata.get("requirements", [])
    #                         tags = metadata.get("tags", [])
    #                         category = metadata.get("category", "")
    #                         permissions = metadata.get("permissions", [])
    #
    #                         result = PluginDiscoveryResult(
    #                             name=metadata.get("id", plugin_dir.name),
    #                             path=str(plugin_dir.resolve()),
    #                             entry_file=entry_path.name,
    #                             plugin_class=plugin_class,
    #                             metadata=metadata,
    #                             config=config,
    #                             tools=tools,
    #                             requirements=requirements,
    #                             tags=tags,
    #                             category=category,
    #                             permissions=permissions,
    #                             load_status="loaded"
    #                         )
    #                         self.discovered_plugins[metadata.get("id", result.id)] = result
    #                 except Exception as e:
    #                     self.failed_plugins.add(plugin_dir.name)
    #                     self.discovered_plugins[plugin_dir.name] = PluginDiscoveryResult(
    #                         name=plugin_dir.name,
    #                         path=str(plugin_dir.resolve()),
    #                         entry_file=entry_path.name,
    #                         plugin_class=None,
    #                         load_status="failed",
    #                         error=str(e)
    #                     )
    #     return self.discovered_plugins


if __name__ == '__main__':
    discovery = PluginDiscovery()
    plugins = discovery.scan_plugins()
    for plugin_id, result in plugins.items():
        print(f"Plugin ID: {plugin_id}, Status: {result.name}, Error: {result.error}")
        print(result)
        print(result.tools)
