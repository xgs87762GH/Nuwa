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
from src.core.plugin.model.plugins import PluginDiscoveryResult
from validator import PluginValidator


class PluginService:
    instance: any = None
    config: Dict[str, Any] = field(default_factory=dict)  # 插件配置（如 PLUGIN_CONFIG）
    function_schema: Optional[Dict[str, Any]] = None  # 插件功能列表，JSON对象


@dataclass
class PluginInfo:
    name: str  # 插件名称
    path: str  # 插件目录绝对路径
    entry_file: str  # 插件主入口文件（如 __init__.py 或 main.py）
    plugin_services: List[PluginService]  # 插件注册类（如 CameraPlugin）
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 插件唯一标识符（UUID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 插件元信息（如 METADATA）
    requirements: Optional[List[str]] = None  # Python依赖包
    tags: Optional[List[str]] = None  # 插件标签
    permissions: Optional[List[str]] = None  # 插件权限声明
    load_status: Optional[str] = "pending"  # 加载状态（pending/loaded/failed）
    error: Optional[str] = None  # 加载失败原因
    discovered_at: Optional[str] = None  # 发现时间戳


class PluginLoader:

    def __init__(self):
        self.plugin_instances: List[PluginInfo] = []
        self.discovery = PluginDiscovery()
        self.validator = PluginValidator()
        self.discovery.scan_plugins()

    def load_plugin(self) -> Optional[Any]:
        plugins: List[PluginDiscoveryResult] = self.discovery.plugins

        for plugin in plugins:
            print(f"正在加载插件 {plugin.path}...")
            self.metadata_extractor = MetadataExtractor(plugin.path)

            path = plugin.path
            entry_file: Path = plugin.entry_file
            # plugin_classes: List[Any] = plugin.plugin_classes
            metadata: Dict[str, Any] = self.metadata_extractor.metadata
            name = metadata.get("project.name")

            services: List[PluginService] = []
            for service_class in plugin.plugin_classes:
                config: Dict[str, Any] = self._load_config(service_class)
                functions = self._load_functinos(service_class)
                instance = self._load_instance(service_class)

                if functions and instance:
                    plugin_service = PluginService()
                    plugin_service.instance = instance
                    plugin_service.functions = functions
                    plugin_service.config = config
                    services.append(plugin_service)
            plugin_info = PluginInfo(
                name=name,
                plugin_services=services,
                metadata=metadata,
                path=path,
                entry_file=entry_file.name,
                requirements=metadata.get("project.dependencies", []),
                tags=metadata.get("project.tags", []),
                permissions=metadata.get("project.permissions", []),
                load_status="loaded",
                discovered_at=datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).isoformat()
            )
            print(f"Plugin {name} loaded successfully")
            print(f"plugin info: {plugin_info}")

    # def _load_configs(self, class_objs: List[Any]) -> List[Dict[str, Any]]:
    #     configs: List[Dict[str, Any]] = []
    #     for cls in class_objs:
    #         if hasattr(cls, "PLUGIN_CONFIG"):
    #             conf = getattr(cls, "PLUGIN_CONFIG")
    #
    #             if callable(conf):
    #                 config_data = conf()
    #             else:
    #                 config_data = conf
    #
    #             if self.validator.validate_config(config_data):
    #                 configs.append(config_data)
    #     return configs

    def _load_instance(self, class_obj: Any) -> Any | None:
        if hasattr(class_obj, "GET_PLUGIN"):
            get_plugin = getattr(class_obj, "GET_PLUGIN")
            if callable(get_plugin):
                invoke_fun = get_plugin()
                return invoke_fun['instance']
        return None

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


class MetadataExtractor:
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
