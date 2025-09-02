"""
Plugin Models Package
Provides unified access to all plugin-related models
"""

# Import discovery models
from .discovery import PluginDiscoveryResult

# Import service models
from .service import PluginServiceDefinition

# Import registration models
from .registration import PluginMetadata, PluginRegistration, Author, License, ProjectUrls, BuildSystem, Project

# Export all models for easy importing
__all__ = [
    'PluginDiscoveryResult',
    'PluginServiceDefinition',
    'PluginMetadata',
    'PluginRegistration',

    'Author',
    'License',
    'ProjectUrls',
    'BuildSystem',
    'Project'
]
