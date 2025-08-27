from dataclasses import dataclass
from pathlib import Path
from typing import List, Any


# @dataclass
# class PluginDiscoveryResult:
#     name: str  # 插件名称
#     path: str  # 插件目录绝对路径
#     entry_file: str  # 插件主入口文件（如 __init__.py 或 main.py）
#     plugin_class: Any  # 插件注册类（如 CameraPlugin）
#     id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 插件唯一标识符（UUID
#     metadata: Dict[str, Any] = field(default_factory=dict)  # 插件元信息（如 METADATA）
#     config: Dict[str, Any] = field(default_factory=dict)  # 插件配置（如 PLUGIN_CONFIG）
#     tools: Optional[str] = None  # 插件工具列表
#     requirements: Optional[List[str]] = None  # Python依赖包
#     tags: Optional[List[str]] = None  # 插件标签
#     category: Optional[str] = None  # 插件分类
#     permissions: Optional[List[str]] = None  # 插件权限声明
#     load_status: Optional[str] = "pending"  # 加载状态（pending/loaded/failed）
#     error: Optional[str] = None  # 加载失败原因
#     discovered_at: Optional[str] = None  # 发现时间戳

@dataclass
class PluginDiscoveryResult:
    # name: str
    path: str
    entry_file: Path
    plugin_classes: List[Any]
