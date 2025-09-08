# AI Manager Module
import asyncio
import datetime
from typing import List, Dict, Optional

from src.core.ai.model import AIProviderMap
from src.core.ai.providers.interface import BaseAIProvider
from src.core.ai.providers.response import SelectionResponse
from src.core.config import get_logger
from src.core.config.ai import AiConfigLoader
from src.core.config.models import AIModel, AIProviderEnum

LOGGER = get_logger(__name__)


class AIManager:
    """AI管理器类，负责管理和调用不同的AI模型"""

    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.configs: List[AIModel] = []
        self.provider_map = AIProviderMap()
        self.__initialize_providers()

    def __initialize_providers(self):
        """Initialize all AI providers based on configuration"""
        conf_loader = AiConfigLoader()
        self.configs = conf_loader.ai_configs

        LOGGER.info(f"🚀 Initializing {len(self.configs)} AI providers...")

        for config in self.configs:
            try:
                # Get provider class by string name
                provider_class = self.provider_map.get_provider_class(config.provider.name)
                if provider_class:
                    # Create provider instance
                    provider = provider_class(config.config)
                    self.providers[config.provider.name] = provider
                    LOGGER.info(f"✅ Initialized provider: {config.provider.name} ({config.provider.name})")
                else:
                    LOGGER.warning(f"❌ Unknown provider type: {config.provider.name} for {config.provider.name}")
            except Exception as e:
                LOGGER.exception(e)
                LOGGER.error(f"❌ Failed to initialize {config.provider.name}: {e}")

        LOGGER.info(f"🎉 Successfully initialized {len(self.providers)} providers")

    def get_provider(self, name: str) -> Optional[BaseAIProvider]:
        """Get specific provider by name"""
        provider = self.providers.get(name)
        if not provider:
            LOGGER.warning(f"🔍 Provider '{name}' not found. Available: {list(self.providers.keys())}")
        return provider

    def get_providers_by_type(self, provider_type: str) -> List[BaseAIProvider]:
        """Get all providers of specific type (using string name)"""
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

    def get_provider_status(self) -> Dict[str, Dict]:
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            config = next((c for c in self.configs if c.provider.name == name), None)
            status[name] = {
                "type": config.provider.name if config else "unknown",
                "model": getattr(provider.config, 'model', 'unknown'),
                "base_url": getattr(provider.config, 'base_url', 'default'),
                "status": "active",
                "initialized_at": "2025-09-04 08:32:29"
            }
        return status

    async def call_provider(self, provider_name: str, system_prompt: str, user_prompt: str,
                            **kwargs) -> SelectionResponse:
        """Call specific provider with prompts"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        # Set prompts
        provider.set_prompts(system_prompt, user_prompt)

        # Call provider
        LOGGER.debug(
            f"🤖 Calling provider: {provider_name} at {datetime.datetime.now().__format__('%Y-%m-%d %H:%M:%S')}")
        try:
            response = await provider.get_completion(**kwargs)
            LOGGER.debug(f"✅ Provider {provider_name} responded successfully")
            return response
        except Exception as e:
            LOGGER.exception(e)
            LOGGER.error(f"❌ Provider {provider_name} failed: {e}")
            raise

    async def call_best_available(self, system_prompt: str, user_prompt: str, **kwargs) -> SelectionResponse:
        """Call the first available provider"""
        if not self.providers:
            raise RuntimeError("No providers available")

        provider_name = next(iter(self.providers))
        LOGGER.info(f"🎯 Using best available provider: {provider_name}")
        return await self.call_provider(provider_name, system_prompt, user_prompt, **kwargs)

    async def call_with_fallback(self,
                                 primary_provider: str,
                                 fallback_providers: List[str],
                                 system_prompt: str,
                                 user_prompt: str,
                                 **kwargs) -> SelectionResponse:
        """Call provider with fallback mechanism"""
        providers_to_try = [primary_provider] + fallback_providers
        LOGGER.debug(f"   providers to try: {providers_to_try}")
        LOGGER.debug(f"   available providers: {self.providers}")
        for provider_name in providers_to_try:
            # Ignore case provider lookups
            if not any(p.lower() == provider_name.lower() for p in self.providers.keys()):
                continue

            # Find the matching real provider name
            actual_provider_name = next((p for p in self.providers.keys() if p.lower() == provider_name.lower()), None)
            if not actual_provider_name:
                continue

            try:
                LOGGER.info(f"🔄 Trying provider: {actual_provider_name}")
                resp = await self.call_provider(actual_provider_name, system_prompt, user_prompt, **kwargs)
                if resp and resp.success:
                    return resp
                else:
                    LOGGER.warning(f"⚠️ Provider {actual_provider_name} returned unsuccessful response: {resp}")
                    continue
            except Exception as e:
                LOGGER.exception(e)
                LOGGER.warning(f"⚠️ Provider {actual_provider_name} failed: {e}")
                continue

        raise RuntimeError(f"All providers failed: {providers_to_try}")

    def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}
        for name, provider in self.providers.items():
            try:
                # Simple health check - check if provider has required attributes
                health_status[name] = (
                        hasattr(provider, 'config') and
                        hasattr(provider, 'get_completion') and
                        provider.config is not None
                )
            except Exception as e:
                LOGGER.exception(e)
                health_status[name] = False
        return health_status


system_prompt = """You are an intelligent plugin routing system. Filter suitable plugins based on user requirements. Current Time: 2025-09-03 10:37:02, 
User: Gordon. Available: [{'plugin_name':'camera-plugin','plugin_id':'db111534-bddd-4a05-be3f-2c222c069a53','description':'Plugin for camera operations and configurations',
'tags':['camera','recording','photo','video','plugin','mcp']}]. Return JSON: {"analysis":"User intent analysis","selected_plugins":
[{"plugin_name":"Plugin name","plugin_id":"Plugin ID","reason":"Selection reason","confidence":0.9}],"overall_confidence":0.8}. Principles: 1.Match descriptions/tags 
2.Consider relevance 3.Multiple if needed 4.Confidence 0.0-1.0 5.Only needed plugins 6.Plugin-level only."""

user_prompt = "User Requirement: Help me take a photo. Analyze intent and filter suitable plugins."


async def test_call_best_available():
    """Test AI providers"""
    manager = AIManager()
    resp = await manager.call_best_available(system_prompt, user_prompt, model="gpt-4-1106-preview")
    print("Response:", resp)
    print("Response (dict):", resp.__dict__)


async def test_call_with_fallback():
    """Test AI providers"""
    manager = AIManager()
    resp = await manager.call_with_fallback("anthropic", ["openai"], system_prompt, user_prompt)
    print("Response:", resp)
    print("Response (dict):", resp.__dict__)


if __name__ == '__main__':
    asyncio.run(test_call_best_available())
