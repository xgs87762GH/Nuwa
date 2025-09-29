"""
Plugin Service Models
Contains models related to plugin service definitions
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class PluginInfoProviderDefinition:
    """Definition of a plugin service with its configuration and functions"""
    instance: Any = None  # Plugin instance
    config: Dict[str, Any] = field(default_factory=dict)  # Plugin configuration (e.g., PLUGIN_CONFIG)
    functions: Optional[Dict[str, Any]] = None  # Plugin function list, JSON object
