"""
Legacy Plugin Models File
This file has been refactored and split into multiple files for better organization.

For backward compatibility, this file re-exports all models from the new structure.
Please update your imports to use the new modular structure:
- from .discovery import PluginDiscoveryResult
- from .service import PluginInfoProviderDefinition
- from .registration import PluginMetadata, PluginRegistration
"""

# Re-export all models for backward compatibility
from .discovery import PluginDiscoveryResult
from .service import PluginInfoProviderDefinition
from .registration import PluginMetadata, PluginRegistration

# Maintain backward compatibility
__all__ = [
    'PluginDiscoveryResult',
    'PluginInfoProviderDefinition',
    'PluginMetadata',
    'PluginRegistration'
]
