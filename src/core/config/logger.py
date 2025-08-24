"""
Nuwa 日志管理器 - 修复配置问题版本
"""

import logging
import logging.config
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.core.config.config import ConfigManager
from src.core.config.models.models import AppConfig, LoggingConfig


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""

    def __init__(self, extra_fields: Dict[str, Any] = None):
        super().__init__()
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        # 构建基础日志结构
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "user": "Gordon",  # 添加当前用户
            "current_time": "2025-08-19 07:42:36"  # 添加当前时间
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        log_data.update(self.extra_fields)

        # 添加记录中的自定义属性
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                           'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                           'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                           'thread', 'threadName', 'processName', 'process', 'getMessage'):
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, default=str)


class JsonFormatter(logging.Formatter):
    """JSON日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "time": datetime.fromtimestamp(record.created).isoformat(),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "user": "Gordon",
            "current_time": "2025-08-19 07:42:36"
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class LoggerManager:
    """日志管理器"""

    def __init__(self, logger_name: str = None):
        """
        Initialize the LoggerManager with a specific logger name.

        Args:
            logger_name: 日志器名称
        """
        # 修复配置获取方式
        cfg = ConfigManager()
        self.app_config: AppConfig = cfg.load_config_model(AppConfig, "app")
        self.logging_config: LoggingConfig = cfg.load_config_model(LoggingConfig, "logging")

        # 修复logger名称逻辑
        self.logger_name = logger_name if logger_name else f"nuwa.{self.app_config.name}"

        print(f"🔧 初始化日志管理器:")
        print(f"  - Logger名称: {self.logger_name}")
        print(f"  - 日志级别: {self.logging_config.level}")
        print(f"  - 日志格式: {self.logging_config.format}")
        print(f"  - 日志文件: {self.logging_config.file}")
        print(f"  - 控制台输出: {self.logging_config.console}")

        # 确保日志目录存在 - 修复字段名
        log_file_path = Path(self.logging_config.file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"  - 日志目录: {log_file_path.parent}")

        # 配置日志
        self._configure_logging()

    def _configure_logging(self):
        """配置日志系统"""

        # 创建格式化器
        formatters = self._create_formatters()

        # 创建处理器
        handlers = self._create_handlers()

        # 日志配置字典
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "loggers": {
                self.logger_name: {  # 使用正确的logger名称
                    "handlers": list(handlers.keys()),
                    "level": self.logging_config.level,
                    "propagate": False
                }
            }
        }

        print(f"🔧 应用日志配置:")
        print(f"  - 格式化器: {list(formatters.keys())}")
        print(f"  - 处理器: {list(handlers.keys())}")
        print(f"  - Logger: {self.logger_name}")

        try:
            # 应用配置
            logging.config.dictConfig(log_config)
            print("✅ 日志配置应用成功")
        except ValueError as e:
            print(f"⚠️ 日志配置失败，使用简化配置: {e}")
            # 如果自定义格式化器不存在，使用默认格式化器
            if "Unable to configure formatter" in str(e):
                # 移除有问题的格式化器，使用simple格式
                log_config["formatters"] = {"simple": formatters["simple"]}
                # 更新处理器使用simple格式
                for handler in log_config["handlers"].values():
                    if handler.get("formatter") in ["json", "structured"]:
                        handler["formatter"] = "simple"
                logging.config.dictConfig(log_config)
                print("✅ 使用简化日志配置成功")
            else:
                raise

    def _create_formatters(self) -> Dict[str, Dict[str, Any]]:
        """创建格式化器配置"""
        formatters = {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "src.core.utils.logger.JsonFormatter"
            },
            "structured": {
                "()": "src.core.utils.logger.StructuredFormatter",
                "extra_fields": self.logging_config.structured_fields
            }
        }

        return formatters

    def _create_handlers(self) -> Dict[str, Dict[str, Any]]:
        """创建处理器配置"""
        handlers = {}

        # 文件处理器 - 修复字段名
        if self.logging_config.rotation == "time":
            handlers["file"] = {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": self.logging_config.file,  # 修复字段名
                "when": self.logging_config.rotation_when,
                "interval": 1,
                "backupCount": self.logging_config.backup_count,
                "encoding": "utf-8",
                "formatter": self.logging_config.format,
                "level": self.logging_config.level
            }
        elif self.logging_config.rotation == "size":
            # 解析文件大小
            max_bytes = self._parse_size(self.logging_config.max_file_size)
            handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": self.logging_config.file,  # 修复字段名
                "maxBytes": max_bytes,
                "backupCount": self.logging_config.backup_count,
                "encoding": "utf-8",
                "formatter": self.logging_config.format,
                "level": self.logging_config.level
            }
        else:
            # 普通文件处理器
            handlers["file"] = {
                "class": "logging.FileHandler",
                "filename": self.logging_config.file,  # 修复字段名
                "encoding": "utf-8",
                "formatter": self.logging_config.format,
                "level": self.logging_config.level
            }

        # 控制台处理器
        if self.logging_config.console:
            # 控制台使用简单格式
            console_format = "simple" if self.logging_config.format in ["json",
                                                                        "structured"] else self.logging_config.format
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": console_format,
                "level": self.logging_config.level
            }

        return handlers

    def _parse_size(self, size_str: str) -> int:
        """解析大小字符串，返回字节数"""
        size_str = size_str.upper().strip()

        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            # 默认认为是字节
            try:
                return int(size_str)
            except ValueError:
                return 10 * 1024 * 1024  # 默认10MB

    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        """
        # 修复: 使用正确的logger名称
        logger = logging.getLogger(self.logger_name)

        # 验证logger是否正确配置
        if not logger.handlers:
            print(f"⚠️ Logger {self.logger_name} 没有处理器，重新配置...")
            self._configure_logging()
            logger = logging.getLogger(self.logger_name)

        print(f"📝 Logger {self.logger_name} 配置完成:")
        print(f"  - 处理器数量: {len(logger.handlers)}")
        print(f"  - 日志级别: {logger.level}")
        print(f"  - 有效级别: {logger.getEffectiveLevel()}")

        # 记录日志器初始化信息
        logger.info(
            "🚀 日志器初始化完成",
            extra={
                "logger_name": self.logger_name,
                "log_level": self.logging_config.level,
                "log_format": self.logging_config.format,
                "log_file": self.logging_config.file,
                "console_output": self.logging_config.console,
                "current_user": "Gordon",
                "init_time": "2025-08-19 07:42:36"
            }
        )

        return logger

    # 保持向后兼容
    def getLogger(self) -> logging.Logger:
        """向后兼容的方法名"""
        return self.get_logger()


def setup_logging(app_name: str = "nuwa") -> logging.Logger:
    """
    设置全局日志配置

    Args:
        app_name: 应用名称

    Returns:
        logging.Logger: 根日志器
    """
    manager = LoggerManager(app_name)
    return manager.get_logger()


if __name__ == '__main__':
    # 测试日志管理器
    logger = setup_logging("test")
    logger.info("这是一个测试日志")
    logger.error("这是一个错误日志")
    logger.debug("这是一个调试日志")
    logger.warning("这是一个警告日志")
    logger.critical("这是一个严重错误日志")

    # 测试结构化日志
    structured_logger = setup_logging("structured_test")
    structured_logger.info("结构化日志测试", extra={"user_id": 123, "action": "test_action"})
