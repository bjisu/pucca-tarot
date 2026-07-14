"""OpenAI 제공사 (공식 SDK 사용)."""
from typing import Dict, List

from openai import OpenAI

from ..config import OPENAI_API_KEY, OPENAI_MODEL
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    def generate(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1500,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, *messages],
        )
        return response.choices[0].message.content or ""
