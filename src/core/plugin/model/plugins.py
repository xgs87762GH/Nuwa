import uuid
from dataclasses import field, dataclass
from pathlib import Path
from typing import Optional, Any, Dict, List


@dataclass
class PluginDiscoveryResult:
    # name: str
    path: str
    entry_file: Path
    plugin_classes: List[Any]



class PluginServiceDefinition:
    instance: any = None
    config: Dict[str, Any] = field(default_factory=dict)  # 插件配置（如 PLUGIN_CONFIG）
    function_schema: Optional[Dict[str, Any]] = None  # 插件功能列表，JSON对象


@dataclass
class PluginMetadata:
    name: str  # 插件名称
    path: str  # 插件目录绝对路径
    entry_file: str  # 插件主入口文件（如 __init__.py 或 main.py）
    plugin_services: List[PluginServiceDefinition]  # 插件注册类（如 CameraPlugin）
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 插件唯一标识符（UUID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 插件元信息（如 METADATA）
    requirements: Optional[List[str]] = None  # Python依赖包
    tags: Optional[List[str]] = None  # 插件标签
    load_status: Optional[str] = "pending"  # 加载状态（pending/loaded/failed）
    error: Optional[str] = None  # 加载失败原因
    discovered_at: Optional[str] = None  # 发现时间戳
