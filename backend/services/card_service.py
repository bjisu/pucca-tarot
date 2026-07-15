"""카드 데이터 로드, 랜덤 드로우, 오늘의 카드(같은 날 동일 카드).

오늘의 카드는 uuid+날짜를 해시해 결정론적으로 고른다. 서버에 저장하지 않으므로
서버리스(여러 인스턴스)에서도 같은 사용자는 같은 날 항상 같은 카드를 받는다.
"""
import hashlib
import json
import random
from datetime import date
from typing import Dict, List, Tuple

from ..config import DATA_DIR

_CARDS_PATH = DATA_DIR / "tarot_cards.json"

with open(_CARDS_PATH, encoding="utf-8") as f:
    _DECK = json.load(f)

CARDS: List[dict] = _DECK["cards"]
_BY_ID: Dict[int, dict] = {c["id"]: c for c in CARDS}


def deck_payload() -> dict:
    return _DECK


def draw_cards(count: int) -> List[dict]:
    return random.sample(CARDS, count)


def cards_by_ids(ids: List[int]) -> List[dict]:
    """id 목록으로 카드 객체를 복원한다. 알 수 없는 id 는 건너뛴다."""
    return [_BY_ID[i] for i in ids if i in _BY_ID]


def get_daily_card(uid: str) -> Tuple[dict, bool]:
    """uuid+날짜 기준으로 같은 날 같은 카드를 보장한다(결정론적, 저장 없음).

    (card, cached) 튜플 반환. cached 는 하위 호환용으로 항상 True.
    """
    today = date.today().isoformat()
    digest = hashlib.sha256(f"{uid}:{today}".encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(CARDS)
    return CARDS[index], True
