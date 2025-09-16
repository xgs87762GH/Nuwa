# AI Manager Module
import asyncio
import datetime
from typing import List, Dict, Optional, Any

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
        self.providers: Dict[str, BaseAIProvider] = {}
        self.configs: List[AIModel] = []
        self.provider_map = AIProviderMap()
        self.__initialize_providers()

    def __initialize_providers(self):
        """Initialize all AI providers based on configuration"""
        conf_loader = AiConfigLoader()
        self.configs = conf_loader.ai_configs

        LOGGER.info(f"Initializing {len(self.configs)} AI providers")

        for config in self.configs:
            try:
                provider_class = self.provider_map.get_provider_class(config.provider.name)
                if provider_class:
                    provider = provider_class(config.config)
                    self.providers[config.provider.name] = provider
                    LOGGER.info(f"Initialized provider: {config.provider.name}")
                else:
                    LOGGER.warning(f"Unknown provider type: {config.provider.name}")
            except Exception as e:
                LOGGER.error(f"Failed to initialize {config.provider.name}: {e}")

        LOGGER.info(f"Successfully initialized {len(self.providers)} providers")

    def get_provider(self, name: str) -> Optional[BaseAIProvider]:
        """Get specific provider by name"""
        provider = self.providers.get(name)
        if not provider:
            LOGGER.warning(f"Provider '{name}' not found. Available: {list(self.providers.keys())}")
        return provider

    def get_providers_by_type(self, provider_type: str) -> List[BaseAIProvider]:
        """Get all providers of specific type"""
        matching_providers = []
        for config in self.configs:
            if config.provider.name == provider_type and config.provider.name in self.providers:
                matching_providers.append(self.providers[config.provider.name])
        return matching_providers

    def list_available_providers(self) -> List[str]:
        """List all available provider names"""
        return list(self.providers.keys())

    def list_provider_types(self) -> Dict[str, str]:
        """List providers with their types"""
        provider_types = {}
        for config in self.configs:
            if config.provider.name in self.providers:
                provider_types[config.provider.name] = config.provider.name
        return provider_types

    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Get status of all providers"""
        status_list = []
        for name, provider in self.providers.items():
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

    async def call_provider(self, provider_name: str, system_prompt: str, user_prompt: str,
                            **kwargs) -> SelectionResponse:
        """Call specific provider with prompts"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        provider.set_prompts(system_prompt, user_prompt)

        try:
            response = await provider.get_completion(**kwargs)
            return response
        except Exception as e:
            LOGGER.error(f"Provider {provider_name} failed: {e}")
            raise e

    async def call_best_available(self, system_prompt: str, user_prompt: str, **kwargs) -> SelectionResponse:
        """Call providers in order until one succeeds or all fail"""
        if not self.providers:
            raise RuntimeError("No providers available")

        provider_names = list(self.providers.keys())
        last_exception = None

        for provider_name in provider_names:
            try:
                LOGGER.info(f"Trying provider: {provider_name}")
                response = await self.call_provider(provider_name, system_prompt, user_prompt, **kwargs)
                if response and response.success:
                    LOGGER.info(f"Successfully used provider: {provider_name}")
                    return response
                else:
                    LOGGER.warning(f"Provider {provider_name} returned unsuccessful response")
                    continue
            except Exception as e:
                LOGGER.warning(f"Provider {provider_name} failed: {e}")
                last_exception = e
                continue

        # All providers failed
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(f"All providers failed: {provider_names}")

    async def call_with_fallback(self,
                                 primary_provider: str,
                                 fallback_providers: List[str],
                                 system_prompt: str,
                                 user_prompt: str,
                                 **kwargs) -> SelectionResponse:
        """Call provider with fallback mechanism"""
        providers_to_try = [primary_provider] + fallback_providers
        last_exception = None

        for provider_name in providers_to_try:
            # Case-insensitive provider lookup
            actual_provider_name = next(
                (p for p in self.providers.keys() if p.lower() == provider_name.lower()),
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
        for name, provider in self.providers.items():
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
        self.providers.clear()
        self.configs.clear()
        self.__initialize_providers()

    def get_provider_count(self) -> int:
        """Get total number of active providers"""
        return len(self.providers)

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if specific provider is available"""
        return provider_name in self.providers

    async def test_provider_connectivity(self, provider_name: str) -> bool:
        """Test if provider can be reached"""
        try:
            test_response = await self.call_provider(
                provider_name,
                "You are a test assistant.",
                "Respond with 'OK' if you receive this message.",
                max_tokens=10
            )
            return test_response.success if test_response else False
        except Exception:
            return False