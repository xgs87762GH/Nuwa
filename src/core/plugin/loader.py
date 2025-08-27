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


@dataclass
class PluginInfo:
    name: str  # 插件名称
    path: str  # 插件目录绝对路径
    entry_file: str  # 插件主入口文件（如 __init__.py 或 main.py）
    plugin_class: List[Any]  # 插件注册类（如 CameraPlugin）
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 插件唯一标识符（UUID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 插件元信息（如 METADATA）
    config: Dict[str, Any] = field(default_factory=dict)  # 插件配置（如 PLUGIN_CONFIG）
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
            plugin_classes: List[Any] = plugin.plugin_classes
            metadata: Dict[str, Any] = self.metadata_extractor.metadata
            name = metadata.get("project.name")
            config: Dict[str, Any] = self._load_configs(plugin_classes)

            print(
                f"Loading plugin: {name} from {path} , entry: {entry_file}, class: {plugin_classes}, metadata: {metadata}, config: {config}")

    def _load_configs(self, class_objs: List[Any]) -> Dict[str, Any]:
        configs: List[Dict[str, Any]] = []
        for cls in class_objs:
            if hasattr(cls, "PLUGIN_CONFIG"):
                conf = getattr(cls, "PLUGIN_CONFIG")
                if self.validator.validate_config(conf):
                    configs.append(conf)

        return configs


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
