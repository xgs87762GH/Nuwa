"""
插件加载器
负责动态加载和实例化插件模块
"""
import datetime
import tomllib
import uuid
from dataclasses import field, dataclass
from pathlib import Path
from typing import Optional, Any, Dict, List

from discovery import PluginDiscovery
from model.plugins import PluginDiscoveryResult, PluginMetadata, PluginServiceDefinition
from validator import PluginValidator


class PluginLoader:

    def __init__(self):
        self.plugin_instances: List[PluginMetadata] = []
        self.discovery = PluginDiscovery()
        self.validator = PluginValidator()
        self.discovery.scan_plugins()

    def load_plugin(self) -> Optional[Any]:
        plugins: List[PluginDiscoveryResult] = self.discovery.plugins
        for plugin in plugins:
            print(f"正在加载插件 {plugin.path}...")
            plugin_info = self._load_plugin(plugin)
            if not plugin_info:
                print(f"Failed to load plugin at {plugin.path}")
                continue
            print(f"Plugin {plugin_info.name} loaded successfully")
            self.plugin_instances.append(plugin_info)

    def _load_plugin(self, plugin: Any) -> PluginMetadata | None:
        self.metadata_extractor = ProjectMetadataReader(plugin.path)
        path = plugin.path
        entry_file: Path = plugin.entry_file
        metadata: Dict[str, Any] = self.metadata_extractor.metadata
        # 获取项目信息
        name = metadata.get("project", {}).get("name")
        tags = metadata.get("project", {}).get("keywords", [])
        # 获取依赖
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

        plugin_info = PluginMetadata(
            name=name,
            plugin_services=services,
            metadata=metadata,
            path=path,
            entry_file=entry_file.name,
            requirements=dependencies,
            tags=tags,
            load_status="loaded",
            discovered_at=datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).isoformat()
        )
        return plugin_info

    def _load_instance(self, class_obj: Any) -> Any | None:
        if hasattr(class_obj, "GET_PLUGIN"):
            get_plugin = getattr(class_obj, "GET_PLUGIN")
            if callable(get_plugin):
                invoke_fun = get_plugin()
                return invoke_fun['instance']
        return None

    def _load_dependencies(self, plugin_path: str, metadata: dict) -> List[str]:
        dependencies = metadata.get("project", {}).get("dependencies", [])

        requirements_file = Path(plugin_path) / "requirements.txt"
        if requirements_file.exists():
            with requirements_file.open("r") as f:
                file_dependencies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                dependencies.extend(file_dependencies)
        return list(set(dependencies))

    def _load_functinos(self, class_obj: Any) -> Any | None:
        if hasattr(class_obj, "FUNCTIONS"):
            funcs = getattr(class_obj, "FUNCTIONS")
            return funcs
        return None

    def _load_config(self, class_obj: Any) -> Dict[str, Any]:
        if hasattr(class_obj, "PLUGIN_CONFIG"):
            conf = getattr(class_obj, "PLUGIN_CONFIG")
            if callable(conf):
                config_data = conf()
            else:
                config_data = conf

            if self.validator.validate_config(config_data):
                return config_data
        return {}


class ProjectMetadataReader:
    """
    元数据提取器
    从指定插件目录读取 pyproject.toml 并缓存结果
    """

    __slots__ = ("_metadata",)

    def __init__(self, plugin_path: str | Path) -> None:
        self._metadata: Dict[str, Any] = self._load(plugin_path)

    # ------------- 公开接口 -------------
    @property
    def metadata(self) -> Dict[str, Any]:
        """只读访问"""
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

    # ------------- 内部实现 -------------
    @staticmethod
    def _load(plugin_path: str | Path) -> Dict[str, Any]:
        path = Path(plugin_path, "pyproject.toml")
        if not path.exists():
            return {}

        try:
            with path.open("rb") as fp:
                data = tomllib.load(fp)

            return {
                "build_system": data.get("build-system", {}),
                "project": data.get("project", {}),
                "loaded_at": datetime.datetime.now(tz=datetime.timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
                "loaded_by": data.get("loaded_by", "unknown"),
            }
        except Exception as exc:
            return {"error": str(exc)}


if __name__ == '__main__':
    loader = PluginLoader()
    loader.load_plugin()
