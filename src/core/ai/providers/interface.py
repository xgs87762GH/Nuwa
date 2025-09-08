from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any

import httpx

from src.core.ai.providers.response import SelectionResponse
from src.core.config import get_logger
from src.core.config.models import AIConfig
from src.core.utils import JsonValidator
from src.core.utils.global_tools import project_root
from src.core.utils.template import EnhancedPromptTemplates, PromptResponse

LOGGER = get_logger(__name__)


class BaseAIProvider(ABC):
    """Base class for AI providers with common interface and functionality"""

    def __init__(self, config: AIConfig):
        """Initialize AI provider with configuration

        Args:
            config: AI configuration object containing API keys, endpoints, etc.
        """
        self.config = config
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.system_prompt: Optional[str] = None
        self.user_prompt: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []

    @abstractmethod
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for API requests

        Returns:
            Dictionary of HTTP headers
        """
        pass

    @abstractmethod
    def _build_payload(self, model: str) -> Dict[str, Any]:
        """Build request payload for API call

        Args:
            model: Model name to use

        Returns:
            Dictionary containing the request payload
        """
        pass

    @abstractmethod
    def _extract_response_content(self, response_data: Dict[str, Any]) -> str:
        """Extract content from API response

        Args:
            response_data: Raw response data from API

        Returns:
            Extracted text content
        """
        pass

    @abstractmethod
    def _get_api_endpoint(self) -> str:
        """Get the API endpoint for this provider

        Returns:
            API endpoint path
        """
        pass

    def set_prompts(self, system_prompt: str, user_prompt: str) -> None:
        """Set system and user prompts for the conversation

        Args:
            system_prompt: Instructions for the AI model behavior
            user_prompt: User's input/question
        """
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def add_to_conversation(self, role: str, content: str) -> None:
        """Add message to conversation history

        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self.conversation_history.append({"role": role, "content": content})

    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self.conversation_history.clear()

    def get_max_tokens(self) -> int:
        """Get max tokens from config with fallback"""
        return getattr(self.config, 'max_tokens', 2048)

    def get_temperature(self) -> float:
        """Get temperature from config with fallback"""
        return getattr(self.config, 'temperature', 0.7)

    def get_timeout_config(self) -> 'httpx.Timeout':
        """Get timeout configuration"""
        import httpx
        return httpx.Timeout(
            timeout=self.config.request_timeout,
            connect=getattr(self.config, 'connect_timeout', 30),
            read=getattr(self.config, 'read_timeout', self.config.request_timeout)
        )

    async def _make_ai_request(self, model: Optional[str] = None) -> str:
        """
        Make a single AI request

        Args:
            model: Model name

        Returns:
            Raw response content

        Raises:
            Exception: If API request fails
        """
        if model is None:
            model = self.get_default_model()

        headers = self._build_headers()
        payload = self._build_payload(model)
        timeout = self.get_timeout_config()
        endpoint = f"{self.base_url}{self._get_api_endpoint()}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            LOGGER.debug(f"Requesting: {endpoint}")
            LOGGER.debug(f"Model: {model}")

            response = await client.post(endpoint, headers=headers, json=payload)

            if response.status_code == 200:
                response_data = response.json()
                content = self._extract_response_content(response_data)

                # Add to conversation history
                self.add_to_conversation("user", self.user_prompt)
                self.add_to_conversation("assistant", content)
                LOGGER.debug(f"Response: {content}")
                return content
            else:
                error_msg = self._extract_error_message(response)
                raise Exception(f"{self.__class__.__name__} API Error {response.status_code}: {error_msg}")

    async def get_completion(self, model: Optional[str] = None) -> SelectionResponse:
        """Get completion from AI model

        Args:
            model: Model name (uses default if not specified)

        Returns:
            Generated text response

        Raises:
            ValueError: If prompts are not set
            Exception: If API request fails
        """
        if not self.system_prompt or not self.user_prompt:
            raise ValueError("Prompts not set. Call set_prompts() first.")

        try:

            content = await self._make_ai_request(model)
            content = await self._fix_response_content(content, model)

            return SelectionResponse.success_response(content)

        except httpx.ConnectTimeout:
            raise Exception(f"Connection timeout to {self.base_url}")
        except httpx.ReadTimeout:
            raise Exception(f"Read timeout from {self.base_url}")
        except httpx.RequestError as e:
            raise Exception(f"Request error: {str(e)}")
        except Exception as e:
            if "API Error" in str(e):
                raise
            raise Exception(f"Unexpected error: {str(e)}")

    async def _fix_response_content(self, content: str, model: str) -> str:
        if JsonValidator.is_valid_json(content):
            return content
        else:

            enhancedPromptTemplates = EnhancedPromptTemplates(template_dir=f"{project_root()}/templates/prompts")
            prompt: PromptResponse = enhancedPromptTemplates.get_json_fix_prompt(invalid_json=content)
            self.set_prompts(prompt.system_prompt, prompt.user_prompt)
            return await self._make_ai_request(model=model)

    def _extract_error_message(self, response: 'httpx.Response') -> str:
        """Extract error message from response"""
        try:
            response_data = response.json()
            return response_data.get("error", {}).get("message", "Unknown error")
        except:
            return response.text or "Unknown error"

    @abstractmethod
    def get_default_model(self) -> str:
        """Get default model name for this provider

        Returns:
            Default model name
        """
        pass
