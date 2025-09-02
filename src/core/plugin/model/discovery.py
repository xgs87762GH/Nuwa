"""
Plugin Discovery Models
Contains models related to plugin discovery process
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List


@dataclass
class PluginDiscoveryResult:
    """Result of plugin discovery process"""
    path: str  # Plugin directory path
    entry_file: Path  # Main entry file (e.g., __init__.py or main.py)
    plugin_classes: List[Any]  # Discovered plugin classes
