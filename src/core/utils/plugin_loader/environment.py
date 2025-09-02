"""
Plugin Environment Management
Handles isolated runtime environments for plugins
"""
import sys
import threading
import uuid
from pathlib import Path

from src.core.config import get_logger

logger = get_logger("plugin_environment")


class PluginEnvironment:
    """Create isolated runtime environment for each plugin"""

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.plugin_name = plugin_dir.name
        self.original_modules = {}
        self.original_path = []
        self.module_prefix = f"plugin_{self.plugin_name.replace('-', '_')}_{uuid.uuid4().hex[:8]}"
        self.lock = threading.Lock()

    def __enter__(self):
        """Enter plugin environment"""
        with self.lock:
            # Save current environment
            self.original_modules = sys.modules.copy()
            self.original_path = sys.path.copy()

            # Set plugin-specific module search path
            plugin_path = str(self.plugin_dir.resolve())

            # Clean up potentially conflicting modules
            self._backup_conflicting_modules()

            # Add plugin directory to the front of search path
            sys.path.insert(0, plugin_path)

            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit plugin environment and restore original state"""
        with self.lock:
            # Restore original modules and paths
            sys.modules.clear()
            sys.modules.update(self.original_modules)
            sys.path.clear()
            sys.path.extend(self.original_path)

    def _backup_conflicting_modules(self):
        """Backup modules that might conflict"""
        # Common module names that are likely to conflict
        potential_conflicts = ['model', 'models', 'services', 'interface', 'utils', 'core', 'config', 'api']

        for module_name in potential_conflicts:
            if module_name in sys.modules:
                # Temporarily remove these modules so plugins can import their own versions
                backup_name = f"_backup_{module_name}_{id(self)}"
                sys.modules[backup_name] = sys.modules[module_name]
                del sys.modules[module_name]
