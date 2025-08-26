"""
插件加载器
负责动态加载和实例化插件模块
"""
import uuid
from dataclasses import field, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any, Dict, List

from kombu.transport.sqlalchemy import metadata

from .discovery import PluginDiscovery, PluginDiscoveryResult
from .validator import PluginValidator


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
        self.metadata_extractor = MetadataExtractor()

    def load_plugin(self, plugin_path: Path) -> Optional[Any]:
        plugins: List[PluginDiscoveryResult] = self.discovery.plugins

        for plugin in plugins:
            name = plugin.name
            path = plugin.path
            entry_file: Path = plugin.entry_file
            plugin_class: List[Any] = plugin.plugin_class
            metadata: Dict[str, Any] = self.metadata_extractor.metadata
            config: Dict[str, Any] = self._load_configs(plugin_class)

    def _load_configs(self, class_obj: List[Any]) -> Dict[str, Any]:
        configs: List[Dict[str, Any]] = []
        for cls in class_obj:
            if hasattr(cls, "PLUGIN_CONFIG"):
                conf = getattr(cls, "PLUGIN_CONFIG")
                if self.validator.validate_config(conf):
                    configs.append(conf)

        return configs


class MetadataExtractor:
    """
    元数据提取器
    """

    def __init__(self, metadata_file: Path = None):
        if metadata_file is None:
            raise ValueError("Metadata file path cannot be None")
        self.metadata_file = metadata_file
        self.metadata: Dict[str, Any] = self._load_metadata(plugin)

    def _load_metadata(self, plugin: PluginDiscoveryResult, toml_lib=None) -> Dict[str, Any]:
        """从 pyproject.toml 加载插件元数据"""
        if toml_lib is None:
            import toml
            toml_lib = toml

        pyproject_path = Path(plugin.path) / "pyproject.toml"

        if not pyproject_path.exists():
            return {}

        try:
            pyproject_data = toml_lib.load(pyproject_path)

            # 提取各个部分的信息
            metadata = {
                "build_system": self._extract_build_system(pyproject_data),
                "project": self._extract_project_info(pyproject_data),
                "urls": self._extract_project_urls(pyproject_data),
                "nuwa_plugin": self._extract_nuwa_plugin_config(pyproject_data),
                "loaded_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "loaded_by": "ISAISAI"  # 当前用户
            }

            return metadata

        except Exception as e:
            print(f"Error loading pyproject.toml for {plugin.name}: {e}")
            return {"error": str(e)}
