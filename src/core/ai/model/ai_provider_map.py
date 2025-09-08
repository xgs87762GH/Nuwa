# AI Manager Module
from typing import List, Optional, Type, Dict

from src.core.ai.providers import OpenAIProvider, DeepSeekProvider, AnthropicProvider, LocalProvider
from src.core.ai.providers.interface import BaseAIProvider
from src.core.config import get_logger
from src.core.config.models import AIProviderEnum

LOGGER = get_logger(__name__)


class AIProviderMap:
    """AI Provider mapping registry"""

    providers: Dict[str, Type[BaseAIProvider]] = {
        AIProviderEnum.OPENAI.name: OpenAIProvider,
        AIProviderEnum.DEEPSEEK.name: DeepSeekProvider,
        AIProviderEnum.ANTHROPIC.name: AnthropicProvider,
        AIProviderEnum.LOCAL.name: LocalProvider
    }

    @classmethod
    def get_provider_class(cls, provider_type: str) -> Optional[Type[BaseAIProvider]]:
        """Get provider class by type"""
        return cls.providers.get(provider_type)

    @classmethod
    def register_provider(cls, provider_type: str, provider_class: Type[BaseAIProvider]):
        """Register new provider type"""
        cls.providers[provider_type] = provider_class
        LOGGER.info(f"🔧 Registered new provider: {provider_type} -> {provider_class.__name__}")

    @classmethod
    def list_supported_providers(cls) -> List[str]:
        """List all supported provider types"""
        return list(cls.providers.keys())
