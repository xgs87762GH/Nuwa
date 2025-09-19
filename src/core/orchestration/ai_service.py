from src.core.ai import AIManager
from src.core.config import get_logger

Logger = get_logger(__name__)


class AIService:
    def __init__(
            self,
            ai_manager: AIManager,
            preferred_provider: str = None,
            fallback_providers: str = None,
            model: str = None
    ):
        self.ai_manager = ai_manager
        self.preferred_provider = preferred_provider
        self.fallback_providers = fallback_providers or []
        self.model = model

    def validate_ai_manager(self):
        try:
            available_providers = self.ai_manager.list_available_providers()
            if not available_providers:
                Logger.warning("⚠️ 没有可用的AI提供者")
                return False
            Logger.info(f"🤖 可用AI提供者: {available_providers}")
            if self.preferred_provider and self.preferred_provider not in available_providers:
                Logger.warning(f"⚠️ 首选提供者 '{self.preferred_provider}' 不可用，将使用备选方案")
            return True
        except Exception as e:
            Logger.error(f"❌ AI管理器验证失败: {e}")
            return False

    async def call_ai_with_fallback(self, system_prompt, user_prompt):
        if self.preferred_provider:
            return await self.ai_manager.call_with_fallback(
                primary_provider=self.preferred_provider,
                fallback_providers=self.fallback_providers,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.model
            )
        else:
            return await self.ai_manager.call_best_available(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.model
            )
