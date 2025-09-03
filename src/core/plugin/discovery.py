# # Plugin Discovery Module
# import importlib.util
# import os
# import sys
# import uuid
# from pathlib import Path
# from typing import List
#
# from model.plugins import PluginDiscoveryResult
# from src.core.utils.global_tools import project_root
#
#
# class PluginDiscovery:
#
#     def __init__(self, plugins_root: str = f"{project_root()}/plugins"):
#         self.plugins_root = Path(plugins_root)
#         # self.discovered_plugins: Dict[str, PluginDiscoveryResult] = {}
#         # self.failed_plugins: Set[str] = set()
#
#         self.plugins: List[PluginDiscoveryResult] = []
#
#     def scan_plugins(self):
#         if not self.plugins_root.exists():
#             print(f"Plugins directory {self.plugins_root} does not exist.")
#             return {}
#
#         for plugin_dir in self.plugins_root.iterdir():
#             if plugin_dir.is_dir():
#                 plugin_path = str(plugin_dir.resolve())
#                 if plugin_path not in sys.path:
#                     sys.path.insert(0, plugin_path)
#                 init_path = plugin_dir / "__init__.py"
#                 main_path = plugin_dir / "main.py"
#                 entry_path = init_path if init_path.exists() else (main_path if main_path.exists() else None)
#
#                 if entry_path:
#                     module_name = f"plugin_{plugin_dir.name.replace('-', '_')}_{uuid.uuid4().hex}"
#                     spec = importlib.util.spec_from_file_location(module_name, entry_path,
#                                                                   submodule_search_locations=[plugin_path])
#                     plugin_module = importlib.util.module_from_spec(spec)
#                     try:
#                         spec.loader.exec_module(plugin_module)
#                         sys.modules[module_name] = plugin_module
#
#                         plugin_classes = []
#                         for cls_name in getattr(plugin_module, "__all__", []):
#                             plugin_class = getattr(plugin_module, cls_name)
#                             plugin_classes.append(plugin_class)
#                         self.plugins.append(
#                             PluginDiscoveryResult(
#                                 # name=cls_name,
#                                 path=plugin_path,
#                                 entry_file=entry_path,
#                                 plugin_classes=plugin_classes,
#                             )
#                         )
#                     except Exception as e:
#                         e.with_traceback()
#                         print(f"Failed to load plugin {plugin_dir.name}: {e}")
#
#     # def scan_all_plugins(self) -> Dict[str, PluginDiscoveryResult]:
#     #     if not self.plugins_root.exists():
#     #         print(f"Plugins directory {self.plugins_root} does not exist.")
#     #         return {}
#     #
#     #     for plugin_dir in self.plugins_root.iterdir():
#     #         if plugin_dir.is_dir():
#     #             plugin_path = str(plugin_dir.resolve())
#     #             if plugin_path not in sys.path:
#     #                 sys.path.insert(0, plugin_path)
#     #             init_path = plugin_dir / "__init__.py"
#     #             main_path = plugin_dir / "main.py"
#     #             entry_path = init_path if init_path.exists() else (main_path if main_path.exists() else None)
#     #             if entry_path:
#     #                 module_name = f"plugin_{plugin_dir.name.replace('-', '_')}_{uuid.uuid4().hex}"
#     #                 spec = importlib.util.spec_from_file_location(module_name, entry_path)
#     #                 plugin_module = importlib.util.module_from_spec(spec)
#     #                 try:
#     #                     spec.loader.exec_module(plugin_module)
#     #                     sys.modules[module_name] = plugin_module
#     #
#     #                     for cls_name in getattr(plugin_module, "__all__", []):
#     #                         plugin_class = getattr(plugin_module, cls_name)
#     #
#     #                         metadata = plugin_class.METADATA() if hasattr(plugin_class, "METADATA") else {}
#     #                         config = plugin_class.PLUGIN_CONFIG() if hasattr(plugin_class, "PLUGIN_CONFIG") else {}
#     #                         tools = plugin_class.FUNCTIONS() if hasattr(plugin_class, "FUNCTIONS") else []
#     #                         requirements = metadata.get("requirements", [])
#     #                         tags = metadata.get("tags", [])
#     #                         category = metadata.get("category", "")
#     #                         permissions = metadata.get("permissions", [])
#     #
#     #                         result = PluginDiscoveryResult(
#     #                             name=metadata.get("id", plugin_dir.name),
#     #                             path=str(plugin_dir.resolve()),
#     #                             entry_file=entry_path.name,
#     #                             plugin_class=plugin_class,
#     #                             metadata=metadata,
#     #                             config=config,
#     #                             tools=tools,
#     #                             requirements=requirements,
#     #                             tags=tags,
#     #                             category=category,
#     #                             permissions=permissions,
#     #                             load_status="loaded"
#     #                         )
#     #                         self.discovered_plugins[metadata.get("id", result.id)] = result
#     #                 except Exception as e:
#     #                     self.failed_plugins.add(plugin_dir.name)
#     #                     self.discovered_plugins[plugin_dir.name] = PluginDiscoveryResult(
#     #                         name=plugin_dir.name,
#     #                         path=str(plugin_dir.resolve()),
#     #                         entry_file=entry_path.name,
#     #                         plugin_class=None,
#     #                         load_status="failed",
#     #                         error=str(e)
#     #                     )
#     #     return self.discovered_plugins
#
#
# if __name__ == '__main__':
#     discovery = PluginDiscovery()
#     plugins = discovery.scan_plugins()
#     for plugin_id, result in plugins.items():
#         print(f"Plugin ID: {plugin_id}, Status: {result.name}, Error: {result.error}")
#         print(result)
#         print(result.tools)


import importlib.util
import os
import sys
from pathlib import Path
from typing import List

from src.core.plugin.model.plugins import PluginDiscoveryResult
from src.core.config import get_logger
from src.core.utils.global_tools import project_root
from src.core.utils.plugin_loader import PluginEnvironment, PluginModuleRewriter

logger = get_logger("PluginDiscovery")

class PluginDiscovery:
    """Improved plugin discovery system with fully isolated plugin environments"""

    def __init__(self, plugins_root: str = f"{project_root()}/plugins"):
        self.plugins_root = Path(plugins_root)
        self.plugins: List[PluginDiscoveryResult] = []
        self.stopped = False

    async def stop(self):
        self.stopped = True

    async def start(self):
        if not self.plugins_root.exists():
            logger.warning(f"Plugin directory {self.plugins_root} does not exist")
            return

        if not self.stopped:
            self.stopped = False

        for plugin_dir in self.plugins_root.iterdir():
            if plugin_dir.is_dir() and not self.stopped:
                self._load_plugin_with_isolation(plugin_dir)

    def _load_plugin_initializer(self, plugin_dir: Path):
        init_path = plugin_dir / "__init__.py"
        main_path = plugin_dir / "main.py"
        entry_path = init_path if init_path.exists() else (main_path if main_path.exists() else None)
        return entry_path

    def _load_plugin_with_isolation(self, plugin_dir: Path):
        """Load plugin in an isolated environment"""
        plugin_name = plugin_dir.name
        logger.info(f"Starting to load plugin: {plugin_name}")

        # Check for __init__.py
        init_path = self._load_plugin_initializer(plugin_dir)
        if not init_path.exists():
            # logger.debug(f"Skipping plugin {plugin_name}: no __init__.py file")
            logger.warning(f"❌ Skipping plugin {plugin_name}: missing __init__.py or main.py file")
            return

        # Create plugin environment
        with PluginEnvironment(plugin_dir) as env:
            try:
                # Preload all plugin modules into a separate namespace
                self._preload_plugin_modules(plugin_dir, env.module_prefix)

                # Load main module
                module_name = f"{env.module_prefix}_main"
                spec = importlib.util.spec_from_file_location(module_name, init_path)
                plugin_module = importlib.util.module_from_spec(spec)

                # Execute main module
                spec.loader.exec_module(plugin_module)
                sys.modules[module_name] = plugin_module

                # Get plugin classes
                plugin_classes = []
                if hasattr(plugin_module, "__all__"):
                    for cls_name in plugin_module.__all__:
                        if hasattr(plugin_module, cls_name):
                            plugin_class = getattr(plugin_module, cls_name)
                            logger.debug(f"   Loading plugin class: {cls_name}")
                            plugin_classes.append(plugin_class)

                self.plugins.append(
                    PluginDiscoveryResult(
                        path=str(plugin_dir.resolve()),
                        entry_file=init_path,
                        plugin_classes=plugin_classes,
                    )
                )
                logger.info(f"✅ Successfully loaded plugin: {plugin_name}")

            except Exception as e:
                logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
                import traceback
                logger.error(traceback.format_exc())

    def _preload_plugin_modules(self, plugin_dir: Path, module_prefix: str):
        """Preload all plugin modules into a separate namespace"""
        rewriter = PluginModuleRewriter(plugin_dir, module_prefix)

        # Scan all Python files
        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                if file.endswith('.py') and (file != '__init__.py' or file != 'main.py'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(plugin_dir)

                    # Build module name
                    module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
                    module_name = f"{module_prefix}.{'.'.join(module_parts)}"

                    try:
                        # Load module using rewriter
                        module = rewriter.rewrite_imports_and_load(file_path, module_name)
                        sys.modules[module_name] = module
                    except Exception as e:
                        logger.warning(f"Preloading module {module_name} failed: {e}")

                # Handle package __init__.py
                elif file == '__init__.py' or file == 'main.py':
                    dir_path = Path(root)
                    if dir_path != plugin_dir:  # Skip root __init__.py
                        rel_path = dir_path.relative_to(plugin_dir)
                        module_name = f"{module_prefix}.{'.'.join(rel_path.parts)}"

                        try:
                            module = rewriter.rewrite_imports_and_load(
                                dir_path / file, module_name
                            )
                            sys.modules[module_name] = module
                        except Exception as e:
                            logger.warning(f"Preloading package {module_name} failed: {e}")


def safe_call_method(instance, method_name, *args, **kwargs):
    """Safely call instance method"""
    if not hasattr(instance, method_name):
        return {'success': False, 'error': f'Method {method_name} not found'}

    try:
        method = getattr(instance, method_name)
        if not callable(method):
            return {'success': False, 'error': f'{method_name} is not callable'}

        result = method(*args, **kwargs)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e), 'exception_type': type(e).__name__}
