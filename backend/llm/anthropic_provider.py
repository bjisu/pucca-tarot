"""Anthropic Claude 제공사 (공식 SDK 사용)."""
from typing import Dict, List

import anthropic

from ..config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = ANTHROPIC_MODEL

    def generate(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1500,
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("anthropic refusal")
        return "".join(
            block.text for block in response.content if block.type == "text"
        )
