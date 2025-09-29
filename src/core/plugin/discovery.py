import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import List

from src.core.config import get_logger
from src.core.plugin.model.plugins import PluginDiscoveryResult
from src.core.utils.common_utils import project_root
from src.core.utils.plugin_loader import PluginEnvironment, PluginModuleRewriter

logger = get_logger(__name__)


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

    def install_plugin_dependencies(self, plugin_dir: Path):
        req_file = plugin_dir / "requirements.txt"
        pyproject_file = plugin_dir / "pyproject.toml"
        setup_cfg_file = plugin_dir / "setup.cfg"
        # pip cache purge
        # 检查 setup.cfg 里是否有非法依赖
        if setup_cfg_file.exists():
            with open(setup_cfg_file, "r") as f:
                for i, line in enumerate(f, 1):
                    if ":none:" in line:
                        logger.error(f"Error: Invalid dependency ':none:' found in setup.cfg at line {i}")
                        raise ValueError("Invalid dependency ':none:' found in setup.cfg. Please remove it.")

        try:
            if req_file.exists():
                logger.info(f"Installing requirements.txt for {plugin_dir.name}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(req_file)])
            elif pyproject_file.exists():
                logger.info(f"Installing pyproject.toml for {plugin_dir.name}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", str(plugin_dir)])
        except subprocess.CalledProcessError as e:
            logger.error(f"Dependency installation failed for {plugin_dir.name}: {e}")
            # raise

    def _load_plugin_with_isolation(self, plugin_dir: Path):
        """Load plugin in an isolated environment"""
        plugin_name = plugin_dir.name
        logger.info(f"Starting to load plugin: {plugin_name}")

        # Check for __init__.py
        init_path = self._load_plugin_initializer(plugin_dir)
        if not init_path.exists():
            # logger_handler.debug(f"Skipping plugin {plugin_name}: no __init__.py file")
            logger.warning(f"❌ Skipping plugin {plugin_name}: missing __init__.py or main.py file")
            return

        # Install dependencies
        self.install_plugin_dependencies(plugin_dir=plugin_dir)

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

    async def reload(self):
        """Reload all plugins"""
        import warnings
        warnings.warn("PluginDiscovery.reload expired there are compatibility issues", DeprecationWarning)
        self.plugins = []
        await self.start()

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
