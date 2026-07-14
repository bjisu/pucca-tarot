"""Google Gemini 제공사 (REST 호출)."""
from typing import Dict, List

import httpx

from ..config import GEMINI_API_KEY, GEMINI_MODEL
from .base import LLMProvider

_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self):
        self.model = GEMINI_MODEL
        self.api_key = GEMINI_API_KEY

    def generate(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1500,
    ) -> str:
        contents = [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [{"text": m["content"]}],
            }
            for m in messages
        ]
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        url = f"{_BASE}/{self.model}:generateContent"
        with httpx.Client(timeout=60) as client:
            r = client.post(url, params={"key": self.api_key}, json=body)
            r.raise_for_status()
            data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
