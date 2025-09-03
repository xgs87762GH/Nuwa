# AI Manager Module
from typing import List

from src.core.config import get_logger
from src.core.config.ai import AiConfigLoader
from src.core.config.models import AIModel

LOGGER = get_logger(__name__)


class AIManager:
    """AI管理器类，负责管理和调用不同的AI模型"""

    def __init__(self):
        self.providers = {}
        self.configs = List[AIModel]
        self.__initialize_providers()

    def __initialize_providers(self):
        conf_loader = AiConfigLoader()
        self.configs = conf_loader.ai_configs

    

if __name__ == '__main__':
    manager = AIManager()
    LOGGER.debug(manager.configs)
