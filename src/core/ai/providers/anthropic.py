# Anthropic Provider Module
from abc import ABC
from typing import Dict, Any

import httpx

from src.core.ai.providers import BaseAIProvider
from src.core.config import get_logger
from src.core.config.models import AIConfig

LOGGER = get_logger(__name__)


class AnthropicProvider(BaseAIProvider, ABC):

    def __init__(self, config: AIConfig):
        super().__init__(config)

    def _build_payload(self, model: str = None) -> Dict[str, Any]:
        """
        Build the payload for the Anthropic API request.

        :param model: The name of the model.
        :return: The payload for the Anthropic API request.
        """
        return {
            "model": model or self.config.model,
            "max_tokens": self.get_max_tokens(),
            "temperature": self.get_temperature(),
            "system": self.system_prompt,
            "messages": [
                {"role": "user", "content": self.user_prompt}
            ]
        }

    def _build_headers(self) -> Dict[str, str]:
        """
        Build the headers for the Anthropic API request.

        :return: The headers for the Anthropic API request.
        """
        return {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": self.config.anthropic_version
        }

    def _get_api_endpoint(self) -> str:
        """
        Get the API endpoint for the Anthropic API.

        :return: The API endpoint for the Anthropic API.
        """
        return f"/messages"

    def _extract_error_message(self, response: 'httpx.Response') -> str:
        """
        Extract the error message from the Anthropic API response.

        :param response: The response from the Anthropic
        :return: The error message from the Anthropic API response.
        """
        return response.json().get("error", {}).get("message", "Unknown error")

    def _extract_response_content(self, response_data: Dict[str, Any]) -> str:
        """
        Extract the response content from the Anthropic API response.

        :param response_data: The response data from the Anthropic API.
        :return: The response content from the Anthropic API response.
        """
        return response_data["content"][0]["text"]

    def get_default_model(self) -> str:
        """
        Get the default model for the Anthropic API.

        :return: The default model for the Anthropic API.
        """
        return self.config.model
