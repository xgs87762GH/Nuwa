# Local Model Provider Module
from abc import ABC

from src.core.ai.providers import BaseAIProvider
from src.core.config.models import AIConfig


class LocalProvider(BaseAIProvider, ABC):
    def __init__(self, config: AIConfig):
        super().__init__(config)
