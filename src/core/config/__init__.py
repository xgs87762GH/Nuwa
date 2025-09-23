"""
Nuwa Core Configuration Module

Provides all configuration management functionalities for the application,
including database, logging, and application configurations.

Author: Gordon
Created: 2025-08-19
Updated: 2025-08-19 11:59:09
User: Gordon
"""

import logging
from typing import Optional

from .config import ConfigManager
from .database import DataBaseManager
from .models import (
    AppConfig,
    LoggingConfig,
    DatabaseConfig,
    PluginConfig
)

# Global cache variables for singleton behavior
_config_manager_instance: Optional[ConfigManager] = None
# _logger_manager_instance: Optional[LoggerManager] = None
_app_config_instance: Optional[AppConfig] = None
_database_config_instance: Optional[DatabaseConfig] = None
_logging_config_instance: Optional[LoggingConfig] = None
_plugin_config_instance: Optional[PluginConfig] = None


def create_config_manager() -> ConfigManager:
    """
    Factory function to create a ConfigManager instance (singleton).

    Returns:
        ConfigManager: An instance of ConfigManager.
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance


def create_database_manager(db_url: Optional[str] = None) -> DataBaseManager:
    """
    Factory function to create a DataBaseManager instance.

    Args:
        db_url: Optional database URL. If not provided, uses config file.

    Returns:
        DataBaseManager: An instance of DataBaseManager.
    """
    return DataBaseManager(db_url)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    from src.core.config.logger import get_logger
    return get_logger(name)


def get_app_config() -> AppConfig:
    """
    Get application configuration (cached singleton).

    Returns:
        AppConfig: Application configuration instance.
    """
    global _app_config_instance
    if _app_config_instance is None:
        cfg = create_config_manager()
        _app_config_instance = cfg.load_config_model(AppConfig, "app")
    return _app_config_instance


def get_database_config() -> DatabaseConfig:
    """
    Get database configuration (cached singleton).

    Returns:
        DatabaseConfig: Database configuration instance.
    """
    global _database_config_instance
    if _database_config_instance is None:
        cfg = create_config_manager()
        _database_config_instance = cfg.load_config_model(DatabaseConfig, "database")
    return _database_config_instance


def get_plugin_config() -> PluginConfig:
    """
    Get plugin configuration (cached singleton).

    Returns:
        PluginConfig: Plugin configuration instance.
    """
    global _plugin_config_instance
    if _plugin_config_instance is None:
        cfg = create_config_manager()
        _plugin_config_instance = cfg.load_config_model(PluginConfig, "plugin")
    return _plugin_config_instance


def reload_all_configs():
    """
    Reload all configurations by clearing the cache.

    Useful for development or when configuration files are updated.
    """
    global _config_manager_instance, _logger_manager_instance
    global _app_config_instance, _database_config_instance, _logging_config_instance

    # Clear all cached instances
    _config_manager_instance = None
    _logger_manager_instance = None
    _app_config_instance = None
    _database_config_instance = None
    _logging_config_instance = None

    print(f"✅ All configurations reloaded at 2025-08-19 11:59:09 by user Gordon")



# 公共API
__all__ = [
    # 核心类
    'ConfigManager',
    'DataBaseManager',
    # 'LoggerManager',

    # 配置模型
    'AppConfig',
    'DatabaseConfig',
    'LoggingConfig',
    'PluginConfig',

    # 工厂函数
    'create_config_manager',
    'create_database_manager',
    'get_logger',

    # 配置获取函数
    'get_app_config',
    'get_database_config',
    'get_plugin_config',

    # 工具函数
    'reload_all_configs'
]
