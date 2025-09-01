from pathlib import Path
from typing import Dict, Any, Optional, Type, TypeVar
import os
from functools import lru_cache

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from src.core.utils.global_tools import project_root

T = TypeVar('T')


class ConfigManager:
    """
    Simplified configuration manager
    Prioritizes pyproject.toml with backward compatibility for YAML
    """

    def __init__(self, project_root_path: Optional[str] = None):
        self.project_root = Path(project_root_path) if project_root_path else Path(project_root())
        self.config_dir = self.project_root / "config"
        self._pyproject_data: Optional[Dict[str, Any]] = None

    def _load_pyproject_toml(self) -> Dict[str, Any]:
        """Load all .toml files from config directory"""
        if self._pyproject_data is not None:
            return self._pyproject_data

        merged_data = {}

        try:
            if not self.config_dir.exists():
                return {}

            # Get all .toml files
            toml_files = list(self.config_dir.glob("*.toml"))

            for toml_file in toml_files:
                with open(toml_file, 'rb') as f:
                    file_data = tomllib.load(f)
                    # Deep merge configuration data
                    self._merge_dict(merged_data, file_data)

            self._pyproject_data = merged_data
            return self._pyproject_data

        except Exception as e:
            print(f"❌ Failed to load configuration files: {e}")
            return {}

    def _merge_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value

    @lru_cache(maxsize=32)
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load specified configuration"""
        pyproject_data = self._load_pyproject_toml()
        if "tool" not in pyproject_data:
            config_data = pyproject_data.get(config_name, {})
        else:
            config_data = pyproject_data.get("tool", {}).get(config_name, {})

        # Apply environment variable overrides
        return self._apply_env_overrides(config_data, config_name)

    def _apply_env_overrides(self, config_data: Dict[str, Any], config_name: str) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        env_prefixes = {
            'app': 'APP_',
            'database': 'DB_',
            'logging': 'LOG_',
        }

        prefix = env_prefixes.get(config_name, f"{config_name.upper()}_")
        result = config_data.copy()

        for key, value in result.items():
            env_key = f"{prefix}{key.upper()}"
            env_value = os.getenv(env_key)

            if env_value is not None:
                if isinstance(value, bool):
                    result[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(value, int):
                    try:
                        result[key] = int(env_value)
                    except ValueError:
                        pass
                else:
                    result[key] = env_value

        return result

    def load_config_model(self, model_class: Type[T], config_name: str) -> T:
        """Load configuration into Pydantic model"""
        config_data = self.load_config(config_name)

        if not config_data:
            return model_class()

        try:
            return model_class(**config_data)
        except Exception as e:
            print(f"❌ Configuration validation failed for {config_name}: {e}")
            return model_class()

    def get_nested_config(self, *keys: str) -> Optional[Any]:
        """Backward compatibility method"""
        if len(keys) == 1:
            return self.load_config(keys[0])

        config_data = self.load_config(keys[0])
        value = config_data

        for key in keys[1:]:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value


if __name__ == '__main__':
    from src.core.config import AppConfig, DatabaseConfig, LoggingConfig, PluginConfig

    config_manager = ConfigManager()
    app_config = config_manager.load_config_model(AppConfig, 'app')
    db_config = config_manager.load_config_model(DatabaseConfig, 'database')
    logging_config = config_manager.load_config_model(LoggingConfig, 'logging')
    plugin_config = config_manager.load_config_model(PluginConfig, 'plugin')

    print("App Config:", app_config)
    print("Database Config:", db_config)
    print("Logging Config:", logging_config)
    print("Plugin Config:", plugin_config)
