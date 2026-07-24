"""리딩 생성 — 카드 데이터 + 질문 + 뿌까 페르소나(YAML) → LLM 호출.

LLM 키가 없거나 호출이 실패하면 카드 고정 데이터 기반의 내장 해석으로 폴백한다.
"""
import json
import logging
import re
from typing import List, Optional

import yaml

from ..config import PROMPTS_DIR
from ..llm.factory import get_provider
from . import card_service

logger = logging.getLogger("pucca")

CLASSIC_POSITIONS = ["현재 상황", "필요한 조언", "결과·전망"]
DEFAULT_TODAY_QUESTION = "오늘 하루는 어떨까?"

with open(PROMPTS_DIR / "pucca_persona.yaml", encoding="utf-8") as f:
    _PERSONA = yaml.safe_load(f)

_SYSTEM = _PERSONA["persona"]["system"]
_TEMPLATES = _PERSONA["templates"]
_CRISIS_KEYWORDS = _PERSONA["safety"]["crisis_keywords"]
CRISIS_RESPONSE = _PERSONA["safety"]["crisis_response"].strip()


# ── 안전 분기 ────────────────────────────────────────────────

def is_crisis(text: str) -> bool:
    return any(kw in text for kw in _CRISIS_KEYWORDS)


# ── 프롬프트 재료 ────────────────────────────────────────────

def _card_block(cards: List[dict], positions: Optional[List[str]] = None) -> str:
    # 카드 이름은 항상 name_en 정식 영문으로 전달 — 해석 문장 속 이름도 영문으로 나오게 한다
    lines = []
    for i, card in enumerate(cards):
        prefix = f"({positions[i]}) " if positions else ""
        lines.append(
            f"- {prefix}{card['name_en']} / {card['arcana']}\n"
            f"  의미: {card['meaning']}\n"
            f"  한 줄 리딩: {card['reading_sentence']}\n"
            f"  키워드: {', '.join(card['keywords'])}"
        )
    return "\n".join(lines)


def _parse_json(text: str) -> dict:
    """LLM 응답에서 첫 JSON 오브젝트를 추출해 파싱한다."""
    text = re.sub(r"```(?:json)?", "", text).strip("` \n")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no json object in response")
    return json.loads(text[start : end + 1])


def _call_llm(prompt: str, max_tokens: int = 1500) -> str:
    provider = get_provider()
    if provider is None:
        raise RuntimeError("no llm provider configured")
    return provider.generate(_SYSTEM, [{"role": "user", "content": prompt}], max_tokens)


def _provider_name() -> str:
    provider = get_provider()
    return provider.name if provider else "fallback"


# ── 반말 변환 (폴백 해석용) ──────────────────────────────────

_BANMAL_RULES = [
    ("때이에요", "때야"),
    ("이에요", "이야"),
    ("예요", "야"),
    ("에요", "야"),
    ("으세요", "어봐"),
    ("이세요", "여봐"),
    ("하세요", "해봐"),
    ("세요", "어봐"),
    ("되어요", "돼"),
    ("돼요", "돼"),
    ("해요", "해"),
    ("봐요", "봐"),
    ("와요", "와"),
    ("줘요", "줘"),
    ("여요", "여"),
    ("네요", "네"),
    ("어요", "어"),
    ("아요", "아"),
    ("지요", "지"),
    ("죠", "지"),
]


def _banmal(text: str) -> str:
    for before, after in _BANMAL_RULES:
        text = text.replace(before, after)
    return text


def _josa(word: str, with_final: str, without_final: str) -> str:
    """받침 유무에 따라 조사를 고른다. 예: _josa('직관', '이라는', '라는')"""
    if not word:
        return without_final
    code = ord(word[-1])
    if 0xAC00 <= code <= 0xD7A3 and (code - 0xAC00) % 28 != 0:
        return with_final
    return without_final


# ── 폴백 해석 (LLM 미사용 시) ────────────────────────────────

def _fallback_today(card: dict, question: str) -> dict:
    kw = card["keywords"]
    return {
        "one_line": _banmal(card["reading_sentence"]),
        "interpretation": (
            f"'{question}' — 이 고민에 '{card['name_en']}' 카드가 나왔어. "
            f"{_banmal(card['meaning'])} "
            f"이 카드의 키워드는 {', '.join(kw)}인데, 지금 네 상황에 꼭 필요한 힌트야. "
            f"카드가 보여주는 흐름은 정해진 미래가 아니라 가능성이니까, 가볍게 참고하면서 네 마음이 가는 쪽을 살펴봐."
        ),
        "advice": f"오늘은 '{kw[0]}'{_josa(kw[0], '을', '를')} 마음에 품고 움직여봐. 작은 한 걸음이면 충분해.",
    }


def _fallback_classic(cards: List[dict], question: str) -> dict:
    c1, c2, c3 = cards
    positions = [
        {
            "position": CLASSIC_POSITIONS[0],
            "interpretation": (
                f"지금 네 상황 자리엔 '{c1['name_en']}' 카드가 나왔어. "
                f"{_banmal(c1['meaning'])} 요즘 네 마음의 배경이 이 카드와 닮아 있을 거야."
            ),
        },
        {
            "position": CLASSIC_POSITIONS[1],
            "interpretation": (
                f"조언 자리엔 '{c2['name_en']}'! {_banmal(c2['meaning'])} "
                f"특히 '{c2['keywords'][0]}'{_josa(c2['keywords'][0], '이라는', '라는')} 키워드를 기억해."
            ),
        },
        {
            "position": CLASSIC_POSITIONS[2],
            "interpretation": (
                f"결과·전망 자리의 '{c3['name_en']}' 카드는 이렇게 말해. "
                f"{_banmal(c3['reading_sentence'])} {_banmal(c3['meaning'])}"
            ),
        },
    ]
    overall = (
        f"'{question}'에 대해 세 카드의 흐름을 정리해볼게. "
        f"지금은 '{c1['keywords'][0]}'의 시기를 지나고 있고, "
        f"'{c2['keywords'][0]}'{_josa(c2['keywords'][0], '이', '가')} 필요한 때야. "
        f"그 흐름을 잘 타면 '{c3['keywords'][0]}' 쪽으로 이어질 가능성이 커. "
        f"미래는 정해진 게 아니라 네 선택으로 만들어지는 거니까, 카드가 준 힌트를 가볍게 참고해봐."
    )
    advice = (
        f"오늘 할 수 있는 가장 작은 것부터 시작해봐. "
        f"'{c2['keywords'][0]}'{_josa(c2['keywords'][0], '을', '를')} 실천하는 하루가 되면 흐름이 달라질 거야."
    )
    return {"positions": positions, "overall": overall, "advice": advice}


# ── 리딩 생성 ────────────────────────────────────────────────

def today_reading(uid: str, question: str) -> dict:
    question = (question or "").strip() or DEFAULT_TODAY_QUESTION
    if is_crisis(question):
        return {"crisis": True, "message": CRISIS_RESPONSE}

    card, _cached = card_service.get_daily_card(uid)
    provider_name = _provider_name()
    result = None
    if provider_name != "fallback":
        try:
            prompt = _TEMPLATES["today_reading"].format(
                question=question, card_block=_card_block([card])
            )
            data = _parse_json(_call_llm(prompt))
            result = {
                "one_line": str(data["one_line"]),
                "interpretation": str(data["interpretation"]),
                "advice": str(data["advice"]),
            }
        except Exception:
            logger.exception("today reading LLM failed — using fallback")
            provider_name = "fallback"
    if result is None:
        result = _fallback_today(card, question)

    return {
        "reading_type": "today",
        "crisis": False,
        "question": question,
        "card": card,
        **result,
        "llm_provider": provider_name,
    }


def classic_reading(uid: str, question: str) -> dict:
    question = (question or "").strip() or "요즘 내 고민, 어떻게 풀릴까?"
    if is_crisis(question):
        return {"crisis": True, "message": CRISIS_RESPONSE}

    cards = card_service.draw_cards(3)
    provider_name = _provider_name()
    result = None
    if provider_name != "fallback":
        try:
            prompt = _TEMPLATES["classic_reading"].format(
                question=question,
                card_block=_card_block(cards, CLASSIC_POSITIONS),
            )
            data = _parse_json(_call_llm(prompt, max_tokens=2000))
            positions = [
                {
                    "position": CLASSIC_POSITIONS[i],
                    "interpretation": str(p["interpretation"]),
                }
                for i, p in enumerate(data["positions"][:3])
            ]
            if len(positions) != 3:
                raise ValueError("positions incomplete")
            result = {
                "positions": positions,
                "overall": str(data["overall"]),
                "advice": str(data["advice"]),
            }
        except Exception:
            logger.exception("classic reading LLM failed — using fallback")
            provider_name = "fallback"
    if result is None:
        result = _fallback_classic(cards, question)

    positions_out = [
        {**p, "card": cards[i]} for i, p in enumerate(result["positions"])
    ]
    return {
        "reading_type": "classic",
        "crisis": False,
        "question": question,
        "positions": positions_out,
        "overall": result["overall"],
        "advice": result["advice"],
        "llm_provider": provider_name,
    }
