import logging
from typing import TypeVar, Optional, Dict, List

from src.core.config import ConfigManager
from src.core.config.models import AIConfig, AIModel, AIProviderEnum

T = TypeVar('T')

logger = logging.getLogger(__name__)


class AiConfigLoader:
    """Database manager for SQLAlchemy async operations."""

    def __init__(self, db_url: Optional[str] = None):
        self.cfg = ConfigManager()
        self.ai_configs: List[AIModel] = self._initialize_configs()

    def _initialize_configs(self) -> List[AIModel]:
        """Load specific configuration section"""
        configs: Dict[str, AIConfig] = self.cfg.load_multi_configs(AIConfig, "ai")
        ai_models = []
        for provider_name, config in configs.items():
            provider_enum = AIProviderEnum.get_by_name(provider_name)
            if provider_enum is None:
                logger.warning(f"Invalid AI provider name: {provider_name}")
                continue

            ai_models.append(AIModel(
                provider=provider_enum,
                config=config
            ))
        return ai_models


if __name__ == '__main__':
    ai_manager = AiConfigLoader()
    print(ai_manager.ai_configs)
