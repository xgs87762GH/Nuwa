"""
Simple Logger Manager
"""

import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.core.config.config import ConfigManager
from src.core.config.models.models import AppConfig, LoggingConfig

# 全局配置
_logging_configured = False

def setup_logging():
    """Setup logging configuration once"""
    global _logging_configured

    if _logging_configured:
        return

    try:
        cfg = ConfigManager()
        app_config: AppConfig = cfg.load_config_model(AppConfig, "app")
        logging_config: LoggingConfig = cfg.load_config_model(LoggingConfig, "logging")

        # Ensure log directory exists
        log_file_path = Path(logging_config.file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create handlers
        handlers = []

        # File handler
        if logging_config.rotation == "time":
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=logging_config.file,
                when=logging_config.rotation_when,
                interval=1,
                backupCount=logging_config.backup_count,
                encoding="utf-8"
            )
        elif logging_config.rotation == "size":
            max_bytes = _parse_size(logging_config.max_file_size)
            file_handler = logging.handlers.RotatingFileHandler(
                filename=logging_config.file,
                maxBytes=max_bytes,
                backupCount=logging_config.backup_count,
                encoding="utf-8"
            )
        else:
            file_handler = logging.FileHandler(
                filename=logging_config.file,
                encoding="utf-8"
            )

        file_handler.setLevel(logging_config.level)
        handlers.append(file_handler)

        # Console handler
        if logging_config.console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging_config.level)
            handlers.append(console_handler)

        # Create formatter
        formatter = logging.Formatter(
            fmt=f"%(asctime)s - Nuwa - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Apply formatter to all handlers
        for handler in handlers:
            handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging_config.level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Add new handlers
        for handler in handlers:
            root_logger.addHandler(handler)

        _logging_configured = True
        print("Logging configured successfully")

    except Exception as e:
        # Fallback configuration
        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s - Nuwa - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        _logging_configured = True
        print(f"Using fallback logging configuration: {e}")


def _parse_size(size_str: str) -> int:
    """Parse size string and return bytes"""
    size_str = size_str.upper().strip()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        try:
            return int(size_str)
        except ValueError:
            return 10 * 1024 * 1024


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance

    Args:
        name: Logger name, defaults to caller's module name

    Returns:
        logging.Logger: Logger instance
    """
    setup_logging()

    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')

    return logging.getLogger(name)