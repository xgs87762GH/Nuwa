# AI Manager Module
import asyncio
import datetime
from typing import List, Dict, Optional, Any, Type

from src.core.ai.model import AIProviderMap
from src.core.ai.providers.interface import BaseAIProvider
from src.core.ai.providers.response import SelectionResponse
from src.core.config import get_logger
from src.core.config.ai import AiConfigLoader
from src.core.config.models import AIModel, AIProviderEnum

LOGGER = get_logger(__name__)


class AIManager:
    """AI Manager class for managing and calling different AI models"""

    def __init__(self):
        self.configs: List[AIModel] = []
        self._providers: Dict[str, BaseAIProvider] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []

        self._provider_map = AIProviderMap()
        self.__initialize_providers()

    def __initialize_providers(self):
        """Initialize all AI providers based on configuration"""
        conf_loader = AiConfigLoader()
        self.configs = conf_loader.ai_configs

        LOGGER.info(f"Initializing {len(self.configs)} AI providers")

        for config in self.configs:
            try:
                provider_class = self._provider_map.get_provider_class(config.provider.name)
                if provider_class:
                    provider = provider_class(config.config)
                    self._providers[config.provider.name] = provider
                    LOGGER.info(f"Initialized provider: {config.provider.name}")
                else:
                    LOGGER.warning(f"Unknown provider type: {config.provider.name}")
            except Exception as e:
                LOGGER.error(f"Failed to initialize {config.provider.name}: {e}")

        if not self.first_provider_name:
            raise RuntimeError("No valid AI providers configured")

        # Set default provider
        self.primary_provider = self.first_provider_name
        LOGGER.info(f"Successfully initialized {len(self._providers)} providers")

    async def call_provider(self, provider_name: str, system_prompt: str, user_prompt: str,
                            **kwargs) -> SelectionResponse:
        """Call specific provider with prompts"""
        activate_provider = self.get_provider(provider_name)
        if not activate_provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        activate_provider.set_prompts(system_prompt, user_prompt)

        try:
            response = await activate_provider.get_completion(**kwargs)
            return response
        except Exception as e:
            LOGGER.error(f"Provider {provider_name} failed: {e}")
            raise e

    async def call_with_fallback(self,
                                 system_prompt: str,
                                 user_prompt: str,
                                 **kwargs) -> SelectionResponse:
        """Call provider with fallback mechanism"""
        providers_to_try = [self.primary_provider] + self.fallback_providers
        last_exception = None

        for provider_name in providers_to_try:
            # Case-insensitive provider lookup
            actual_provider_name = next(
                (p for p in self._providers.keys() if p.lower() == provider_name.lower()),
                None
            )

            if not actual_provider_name:
                LOGGER.warning(f"Provider {provider_name} not available")
                continue

            try:
                LOGGER.info(f"Trying provider: {actual_provider_name}")
                response = await self.call_provider(actual_provider_name, system_prompt, user_prompt, **kwargs)
                if response and response.success:
                    return response
                else:
                    LOGGER.warning(f"Provider {actual_provider_name} returned unsuccessful response")
                    continue
            except Exception as e:
                LOGGER.warning(f"Provider {actual_provider_name} failed: {e}")
                last_exception = e
                continue

        # All providers failed
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(f"All providers failed: {providers_to_try}")

    def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}
        for name, provider in self._providers.items():
            try:
                health_status[name] = (
                        hasattr(provider, 'config') and
                        hasattr(provider, 'get_completion') and
                        provider.config is not None
                )
            except Exception as e:
                LOGGER.error(f"Health check failed for {name}: {e}")
                health_status[name] = False
        return health_status

    def reload_providers(self):
        """Reload all providers from configuration"""
        self._providers.clear()
        self.configs.clear()
        self.__initialize_providers()

    def get_models_by_provider(self, provider_name: str) -> List[str]:
        """Get available models for a specific provider"""
        config = next((c for c in self.configs if c.provider.name == provider_name), None)
        if config and hasattr(config.config, 'models'):
            return config.config.models
        return []

    def get_provider(self, name: str) -> Optional[BaseAIProvider]:
        """Get specific provider by name"""
        provider = self._providers.get(name)
        if not provider:
            LOGGER.warning(f"Provider '{name}' not found. Available: {list(self._providers.keys())}")
        return provider

    def list_available_providers(self) -> List[str]:
        """List all available provider names"""
        return list(self._providers.keys())

    def list_provider_types(self) -> Dict[str, str]:
        """List providers with their types"""
        provider_types = {}
        for config in self.configs:
            if config.provider.name in self._providers:
                provider_types[config.provider.name] = config.provider.name
        return provider_types

    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Get status of all providers"""
        status_list = []
        for name, provider in self._providers.items():
            config = next((c for c in self.configs if c.provider.name == name), None)
            status_list.append({
                "type": config.provider.name if config else "unknown",
                "default_model": getattr(provider.config, 'default_model', 'unknown'),
                "models": getattr(provider.config, 'models', []),
                "base_url": getattr(provider.config, 'base_url', 'default'),
                "status": "active",
                "initialized_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return status_list

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if specific provider is available"""
        return provider_name in self._providers

    def set_preferred_provider(self, provider_type: str, fallback_providers: Optional[list] = None):
        if not self.is_provider_available(provider_type):
            LOGGER.error(f"The specified provider {provider_type} is not available.")
            raise ValueError(f"Provider {provider_type} not found.")

        self.primary_provider = provider_type
        self.fallback_providers = fallback_providers or []
        LOGGER.info(f"Set the preferred AI provider as: {provider_type}")
        LOGGER.info(f"List of alternative AI providers: {self.fallback_providers}")
    @property
    def first_provider_name(self) -> Optional[str]:
        """Get the first available provider."""
        if not self._providers:
            return None
        first_provider_name = next(iter(self._providers))
        return first_provider_name

