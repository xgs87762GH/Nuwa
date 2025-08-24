"""使用 dataclasses 的配置文件"""

import logging
import logging.config
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------- 数据模型 ----------
@dataclass
class AppConfig:
    """应用程序配置"""
    name: str = "HomeGuard"
    version: str = "1.0.0"
    debug: bool = False


@dataclass
class LoggingConfig:
    """日志配置"""
    root_level: str = "INFO"
    file_level: str = "DEBUG"
    console: bool = True
    log_dir: str = "{system_tmp}/logs/{app_name}"

    def get_log_dir_path(self, app_name: str) -> Path:
        """渲染 log_dir 模板"""
        system_tmp = tempfile.gettempdir() if os.name == "nt" else "/tmp"
        resolved_path = self.log_dir.format(
            system_tmp=system_tmp,
            app_name=app_name,
        )
        return Path(resolved_path)


@dataclass
class GlobalConfig:
    """全局配置"""
    app: AppConfig = field(default_factory=AppConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @property
    def log_dir_path(self) -> Path:
        """获取日志目录路径"""
        return self.logging.get_log_dir_path(self.app.name)


# ---------- 日志初始化 ----------
def setup_logging(cfg: Optional[GlobalConfig] = None) -> GlobalConfig:
    """
    设置日志配置

    Args:
        cfg: 全局配置，如果为None则使用默认配置

    Returns:
        使用的配置对象
    """
    if cfg is None:
        cfg = GlobalConfig()

    # 确保日志目录存在
    cfg.log_dir_path.mkdir(parents=True, exist_ok=True)

    # 构建处理器配置
    handlers = {
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": cfg.logging.file_level,
            "formatter": "verbose",
            "filename": str(cfg.log_dir_path / f"{cfg.app.name}.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
        }
    }

    if cfg.logging.console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": cfg.logging.root_level,
            "formatter": "simple",
        }

    # 配置日志
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d | %(message)s"
            },
            "verbose": {
                "format": "%(asctime)s [%(levelname)s] %(name)s %(filename)s:%(lineno)d %(funcName)s() | %(message)s"
            },
        },
        "handlers": handlers,
        "root": {
            "level": cfg.logging.root_level,
            "handlers": list(handlers.keys())
        },
    }

    logging.config.dictConfig(logging_config)

    # 记录配置信息
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {cfg.app.name}")
    logger.info(f"Log directory: {cfg.log_dir_path}")
    logger.debug(f"Full config: {cfg}")

    return cfg


# ---------- 配置工厂函数 ----------
def create_default_config() -> GlobalConfig:
    """创建默认配置"""
    return GlobalConfig()


def create_debug_config() -> GlobalConfig:
    """创建调试配置"""
    config = GlobalConfig()
    config.app.debug = True
    config.logging.root_level = "DEBUG"
    config.logging.console = True
    return config


def create_production_config() -> GlobalConfig:
    """创建生产环境配置"""
    config = GlobalConfig()
    config.app.debug = False
    config.logging.root_level = "INFO"
    config.logging.file_level = "WARNING"
    config.logging.console = False
    return config



# ---------- 使用示例 ----------
if __name__ == "__main__":
    # 基本使用
    config = setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    # 自定义配置
    custom_config = GlobalConfig(
        app=AppConfig(name="CameraService", debug=True),
        logging=LoggingConfig(root_level="DEBUG", console=True)
    )
    setup_logging(custom_config)

    print(f"App name: {config.app.name}")
    print(f"Log directory: {config.log_dir_path}")