"""
Plugin model definitions for the Nuwa MCP service plugin system.

This module contains the core data structures used for plugin discovery,
loading, and metadata management.
"""
from .plugins import PluginServiceDefinition, PluginMetadata, PluginDiscoveryResult

__all__ = [
    # Plugin discovery
    "PluginDiscoveryResult",

    # Plugin metadata and services
    "PluginServiceDefinition",
    "PluginMetadata",
]

__version__ = "1.0.0"
__author__ = "Gordon"
