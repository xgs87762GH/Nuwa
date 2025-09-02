"""
Plugin Loader Utils Package
Provides utilities for plugin loading, environment management, and metadata processing
"""

# Import environment management
from .environment import PluginEnvironment

# Import module rewriting utilities
from .module_rewriter import PluginModuleRewriter

# Import metadata reading utilities
from .metadata_reader import ProjectMetadataReader

# Export all utilities for easy importing
__all__ = [
    # Environment Management
    'PluginEnvironment',

    # Module Rewriting
    'PluginModuleRewriter',

    # Metadata Reading
    'ProjectMetadataReader',
]
