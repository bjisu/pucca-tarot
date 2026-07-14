"""카드 데이터 로드, 랜덤 드로우, 오늘의 카드(같은 날 동일 카드) 캐시."""
import json
import random
from datetime import date
from typing import Dict, List, Tuple

from ..config import DATA_DIR, RUNTIME_DIR

_CARDS_PATH = DATA_DIR / "tarot_cards.json"
_DAILY_PATH = RUNTIME_DIR / "daily_cards.json"

with open(_CARDS_PATH, encoding="utf-8") as f:
    _DECK = json.load(f)

CARDS: List[dict] = _DECK["cards"]
_BY_ID: Dict[int, dict] = {c["id"]: c for c in CARDS}


def deck_payload() -> dict:
    return _DECK


def draw_cards(count: int) -> List[dict]:
    return random.sample(CARDS, count)


def _load_daily() -> dict:
    if _DAILY_PATH.exists():
        try:
            return json.loads(_DAILY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def get_daily_card(uid: str) -> Tuple[dict, bool]:
    """uuid+날짜 기준으로 같은 날 같은 카드를 보장한다. (card, cached) 반환."""
    today = date.today().isoformat()
    store = _load_daily()
    day = store.get(today, {})
    if uid in day:
        return _BY_ID[day[uid]], True
    card = random.choice(CARDS)
    # 지난 날짜는 버리고 오늘 것만 유지
    store = {today: {**day, uid: card["id"]}}
    _DAILY_PATH.write_text(
        json.dumps(store, ensure_ascii=False), encoding="utf-8"
    )
    return card, False
