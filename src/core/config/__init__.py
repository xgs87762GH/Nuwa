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
from typing import Optional, Dict, Any

from .config import ConfigManager
from .database import DataBaseManager
from .logger import LoggerManager
from .models.models import (
    AppConfig,
    DatabaseConfig,
    LoggingConfig,
    PluginConfig
)

# Global cache variables for singleton behavior
_config_manager_instance: Optional[ConfigManager] = None
_logger_manager_instance: Optional[LoggerManager] = None
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


def create_logger_manager() -> LoggerManager:
    """
    Factory function to create a LoggerManager instance (singleton).

    Returns:
        LoggerManager: An instance of LoggerManager.
    """
    global _logger_manager_instance
    if _logger_manager_instance is None:
        _logger_manager_instance = LoggerManager()
    return _logger_manager_instance


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieves the logger instance from the LoggerManager.

    Args:
        name: Optional logger name. If not provided, uses the default logger.

    Returns:
        logging.Logger: The logger instance.
    """
    logger_manager = create_logger_manager()
    return logger_manager.getLogger(name) if name else logger_manager.getLogger()


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


def get_logging_config() -> LoggingConfig:
    """
    Get logging configuration (cached singleton).

    Returns:
        LoggingConfig: Logging configuration instance.
    """
    global _logging_config_instance
    if _logging_config_instance is None:
        cfg = create_config_manager()
        _logging_config_instance = cfg.load_config_model(LoggingConfig, "logging")
    return _logging_config_instance


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


def get_config_status() -> Dict[str, Any]:
    """
    Get current configuration loading status.

    Returns:
        Dict containing the status of all configuration instances.
    """
    return {
        "config_manager_loaded": _config_manager_instance is not None,
        "logger_manager_loaded": _logger_manager_instance is not None,
        "app_config_loaded": _app_config_instance is not None,
        "database_config_loaded": _database_config_instance is not None,
        "logging_config_loaded": _logging_config_instance is not None,
        "timestamp": "2025-08-19 11:59:09",
        "user": "Gordon",
        "author": "Gordon"
    }


def debug_config_info():
    """
    Print configuration debug information.
    """
    status = get_config_status()
    print("🔍 Configuration Status Debug Info:")
    print(f"├── ConfigManager loaded: {status['config_manager_loaded']}")
    print(f"├── LoggerManager loaded: {status['logger_manager_loaded']}")
    print(f"├── AppConfig loaded: {status['app_config_loaded']}")
    print(f"├── DatabaseConfig loaded: {status['database_config_loaded']}")
    print(f"├── LoggingConfig loaded: {status['logging_config_loaded']}")
    print(f"├── Timestamp: {status['timestamp']}")
    print(f"├── User: {status['user']}")
    print(f"└── Author: {status['author']}")


# 公共API
__all__ = [
    # 核心类
    'ConfigManager',
    'DataBaseManager',
    'LoggerManager',

    # 配置模型
    'AppConfig',
    'DatabaseConfig',
    'LoggingConfig',
    'PluginConfig',

    # 工厂函数
    'create_config_manager',
    'create_database_manager',
    'create_logger_manager',
    'get_logger',

    # 配置获取函数
    'get_app_config',
    'get_database_config',
    'get_logging_config',
    'get_plugin_config',

    # 工具函数
    'reload_all_configs',
    'get_config_status',
    'debug_config_info'
]

# 模块元数据
__version__ = "1.0.0"
__author__ = "Gordon"
__description__ = "Configuration management module - Global variable cache version"
__created_date__ = "2025-08-19"
__updated_date__ = "2025-08-19 11:59:09"
__user__ = "Gordon"
