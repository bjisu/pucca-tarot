"""LLM Factory — .env 설정에 따라 제공사를 선택한다.

LLM_PROVIDER 가 비어 있으면 키가 입력된 제공사를 자동 선택하고,
키가 하나도 없으면 None 을 반환한다(→ 내장 해석 폴백 모드).
"""
from functools import lru_cache
from typing import Optional

from .. import config
from .base import LLMProvider


def _build(name: str) -> Optional[LLMProvider]:
    if name == "anthropic" and config.ANTHROPIC_API_KEY:
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    if name == "openai" and config.OPENAI_API_KEY:
        from .openai_provider import OpenAIProvider

        return OpenAIProvider()
    if name == "gemini" and config.GEMINI_API_KEY:
        from .gemini_provider import GeminiProvider

        return GeminiProvider()
    return None


@lru_cache(maxsize=1)
def get_provider() -> Optional[LLMProvider]:
    if config.LLM_PROVIDER:
        return _build(config.LLM_PROVIDER)
    for name in ("anthropic", "openai", "gemini"):
        provider = _build(name)
        if provider:
            return provider
    return None
