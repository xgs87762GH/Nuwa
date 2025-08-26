# Schema Validator Module
from src.core.plugin.discovery import PluginDiscoveryResult


class PluginValidator:
    @staticmethod
    def validate_metadata(metadata: dict) -> bool:
        required_fields = ["name", "version", "author"]
        for field in required_fields:
            if field not in metadata:
                print(f"Metadata missing required field: {field}")
                return False
        return True

    @staticmethod
    def validate_config(config: dict) -> bool:
        if not isinstance(config, dict):
            print("Config should be a dictionary.")
            return False
        return True

    @staticmethod
    def validate_plugin(plugin: 'PluginDiscoveryResult') -> bool:
        if not PluginValidator.validate_metadata(plugin.metadata):
            return False
        if not PluginValidator.validate_config(plugin.config):
            return False
        return True
