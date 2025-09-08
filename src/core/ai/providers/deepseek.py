from abc import ABC
from typing import Dict, Any

import requests

from src.core.ai.providers import BaseAIProvider
from src.core.config.ai import AiConfigLoader
from src.core.config.models import AIProviderEnum


class DeepSeekProvider(BaseAIProvider, ABC):

    def __init__(self, config):
        super().__init__(config)

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

    def _build_payload(self, model: str = None) -> Dict[str, Any]:
        return {
            "model": model or self.get_default_model(),
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt}
            ],
            "max_tokens": getattr(self.config, 'max_tokens', 2048),
            "temperature": getattr(self.config, 'temperature', 0.7)
        }

    def _get_api_endpoint(self) -> str:
        return f"/chat/completions"

    def _extract_response_content(self, response_data: Dict[str, Any]) -> str:
        return response_data["choices"][0]["message"]["content"]

    def get_default_model(self) -> str:
        return getattr(self.config, "model")

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        headers = self._build_headers()
        payload = self._build_payload()
        url = self._get_api_endpoint()
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return self._extract_response_content(response.json())


async def simple_test():
    from src.core.ai.providers.response import PluginsSelectionResponse
    system_prompt = """You are an intelligent plugin routing system. Filter suitable plugins based on user requirements. Current Time: 2025-09-03 10:37:02, 
    User: Gordon. Available: [{'plugin_name':'camera-plugin','plugin_id':'db111534-bddd-4a05-be3f-2c222c069a53','description':'Plugin for camera operations and configurations',
    'tags':['camera','recording','photo','video','plugin','mcp']}]. Return JSON: {"analysis":"User intent analysis","selected_plugins":
    [{"plugin_name":"Plugin name","plugin_id":"Plugin ID","reason":"Selection reason","confidence":0.9}],"overall_confidence":0.8}. Principles: 1.Match descriptions/tags 
    2.Consider relevance 3.Multiple if needed 4.Confidence 0.0-1.0 5.Only needed plugins 6.Plugin-level only."""

    user_prompt = "User Requirement: Help me take a photo. Analyze intent and filter suitable plugins."

    config = AiConfigLoader()
    confs = config.ai_configs

    for conf in confs:
        if conf.provider == AIProviderEnum.DEEPSEEK:
            provider = DeepSeekProvider(conf.config)
            provider.set_prompts(system_prompt, user_prompt)

            try:
                response: PluginsSelectionResponse = await provider.get_completion()
                print("Response:", response)
                print("Response (dict):", response.__dict__)
            except Exception as e:
                print(f"Error: {e}")
            break


if __name__ == '__main__':
    import asyncio

    asyncio.run(simple_test())
