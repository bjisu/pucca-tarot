"""LLM 제공사 공통 인터페이스."""
from abc import ABC, abstractmethod
from typing import Dict, List


class LLMProvider(ABC):
    """messages: [{"role": "user"|"assistant", "content": str}, ...]"""

    name: str = "base"

    @abstractmethod
    def generate(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1500,
    ) -> str:
        raise NotImplementedError
