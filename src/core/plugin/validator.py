# Schema Validator Module

from src.core.config import get_logger
from src.core.plugin.model.plugins import PluginDiscoveryResult

# Configure logger_handler
logger = get_logger("PluginValidator")


class PluginValidator:
    @staticmethod
    def validate_metadata(metadata: PluginDiscoveryResult) -> bool:
        required_fields = ["name", "version", "author"]
        for field in required_fields:
            if field not in metadata:
                logger.error(f"Metadata validation failed: missing required field '{field}'")
                return False
        logger.debug("Metadata validation passed")
        return True

    @staticmethod
    def validate_config(config: dict) -> bool:
        if not isinstance(config, dict):
            logger.error("Config validation failed: config should be a dictionary")
            return False
        logger.debug("Config validation passed")
        return True

    @staticmethod
    def validate_plugin(plugin: 'PluginDiscoveryResult') -> bool:
        logger.debug(f"Starting plugin validation for: {getattr(plugin, 'name', 'unknown')}")

        if not PluginValidator.validate_metadata(plugin):
            logger.warning("Plugin validation failed due to metadata validation failure")
            return False
        if not PluginValidator.validate_config(plugin.config):
            logger.warning("Plugin validation failed due to config validation failure")
            return False

        logger.info(f"Plugin validation successful for: {getattr(plugin, 'name', 'unknown')}")
        return True
