"""
Plugin Loader
Responsible for dynamically loading and instantiating plugin modules
"""
import datetime
import logging
import tomllib
from pathlib import Path
from typing import Optional, Any, Dict, List

from pydantic import BaseModel, Field, field_validator

from model.plugins import PluginDiscoveryResult, PluginRegistration, PluginServiceDefinition
from src.core.config.logger import setup_logging
from validator import PluginValidator

# Configure logger
logger = logging.getLogger(__name__)


class PluginLoadConfig(BaseModel):
    """Configuration for plugin loading operations"""
    max_retry_attempts: int = Field(default=3, ge=1, description="Maximum retry attempts for plugin loading")
    timeout_seconds: int = Field(default=30, ge=1, description="Timeout for plugin loading operations")
    validate_dependencies: bool = Field(default=True, description="Whether to validate plugin dependencies")

    @field_validator('max_retry_attempts')
    @classmethod
    def validate_retry_attempts(cls, v):
        if v <= 0:
            raise ValueError('max_retry_attempts must be greater than 0')
        return v


class PluginLoader:

    def __init__(self, config: Optional[PluginLoadConfig] = None):
        self.config = config or PluginLoadConfig()
        self.validator = PluginValidator()

    def load_plugin(self, plugin: PluginDiscoveryResult = None) -> Optional[PluginRegistration]:
        logger.info(f"Loading plugin from path: {plugin.path}")
        plugin_info = self._load_plugin(plugin)
        if not plugin_info:
            logger.error(f"Failed to load plugin at path: {plugin.path}")
            return None
        logger.info(f"Plugin '{plugin_info.name}' loaded successfully")
        return plugin_info

    def _load_plugin(self, plugin: Any) -> PluginRegistration | None:
        try:
            self.metadata_extractor = ProjectMetadataReader(plugin.path)
            path = plugin.path
            entry_file: Path = plugin.entry_file
            metadata: Dict[str, Any] = self.metadata_extractor.metadata

            # Extract project information
            name = metadata.get("project", {}).get("name")
            tags = metadata.get("project", {}).get("keywords", [])

            # Load dependencies
            dependencies = self._load_dependencies(plugin.path, metadata)

            services: List[PluginServiceDefinition] = []
            for service_class in plugin.plugin_classes:
                config: Dict[str, Any] = self._load_config(service_class)
                functions = self._load_functinos(service_class)
                instance = self._load_instance(service_class)

                if functions and instance:
                    plugin_service = PluginServiceDefinition()
                    plugin_service.instance = instance
                    plugin_service.functions = functions
                    plugin_service.config = config
                    services.append(plugin_service)

            plugin_info = PluginRegistration(
                name=name,
                plugin_services=services,
                metadata=metadata,
                path=path,
                entry_file=entry_file.name,
                requirements=dependencies,
                tags=tags,
                load_status="loaded",
                registered_at=datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).isoformat()
            )
            return plugin_info
        except Exception as e:
            logger.error(f"Error loading plugin from {plugin.path}: {str(e)}")
            return None

    def _load_instance(self, class_obj: Any) -> Any | None:
        try:
            if hasattr(class_obj, "GET_PLUGIN"):
                get_plugin = getattr(class_obj, "GET_PLUGIN")
                if callable(get_plugin):
                    invoke_fun = get_plugin()
                    if isinstance(invoke_fun, dict) and 'instance' in invoke_fun:
                        return invoke_fun['instance']
        except Exception as e:
            logger.warning(f"Failed to load instance from class {class_obj}: {str(e)}")
        return None

    def _load_dependencies(self, plugin_path: str, metadata: dict) -> List[str]:
        dependencies = metadata.get("project", {}).get("dependencies", [])

        requirements_file = Path(plugin_path) / "requirements.txt"
        if requirements_file.exists():
            try:
                with requirements_file.open("r") as f:
                    file_dependencies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    dependencies.extend(file_dependencies)
                logger.debug(f"Loaded dependencies from requirements.txt: {file_dependencies}")
            except Exception as e:
                logger.warning(f"Failed to read requirements.txt from {plugin_path}: {str(e)}")
        return list(set(dependencies))

    def _load_functinos(self, class_obj: Any) -> Any | None:
        try:
            if hasattr(class_obj, "FUNCTIONS"):
                funcs = getattr(class_obj, "FUNCTIONS")
                return funcs
        except Exception as e:
            logger.warning(f"Failed to load functions from class {class_obj}: {str(e)}")
        return None

    def _load_config(self, class_obj: Any) -> Dict[str, Any]:
        try:
            if hasattr(class_obj, "PLUGIN_CONFIG"):
                conf = getattr(class_obj, "PLUGIN_CONFIG")
                if callable(conf):
                    config_data = conf()
                else:
                    config_data = conf

                if self.validator.validate_config(config_data):
                    return config_data
                else:
                    logger.warning(f"Invalid plugin configuration for class {class_obj}")
        except Exception as e:
            logger.warning(f"Failed to load config from class {class_obj}: {str(e)}")
        return {}


class ProjectMetadataReader:
    """
    Metadata Extractor
    Reads pyproject.toml from specified plugin directory and caches the result
    """

    __slots__ = ("_metadata",)

    def __init__(self, plugin_path: str | Path) -> None:
        self._metadata: Dict[str, Any] = self._load(plugin_path)

    # ------------- Public Interface -------------
    @property
    def metadata(self) -> Dict[str, Any]:
        """Read-only access to metadata"""
        return self._metadata

    @property
    def project(self) -> Dict[str, Any]:
        return self._metadata.get("project", {})

    @property
    def dependencies(self) -> List[str]:
        return self.project.get("dependencies", [])

    @property
    def urls(self) -> Dict[str, str]:
        return self.project.get("urls", {})

    # ------------- Internal Implementation -------------
    @staticmethod
    def _load(plugin_path: str | Path) -> Dict[str, Any]:
        path = Path(plugin_path, "pyproject.toml")
        if not path.exists():
            logger.warning(f"pyproject.toml not found at path: {path}")
            return {}

        try:
            with path.open("rb") as fp:
                data = tomllib.load(fp)

            logger.debug(f"Successfully loaded metadata from: {path}")
            return {
                "build_system": data.get("build-system", {}),
                "project": data.get("project", {}),
                "loaded_at": datetime.datetime.now(tz=datetime.timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
                "loaded_by": data.get("loaded_by", "unknown"),
            }
        except Exception as exc:
            logger.error(f"Error loading pyproject.toml from {path}: {str(exc)}")
            return {"error": str(exc)}


if __name__ == '__main__':
    # Configure logging for standalone execution
    logger = setup_logging("structured_test")

    config = PluginLoadConfig(max_retry_attempts=3, validate_dependencies=True)
    loader = PluginLoader(config)
    loader.load_plugin()
