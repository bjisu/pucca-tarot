"""질문 카테고리 데이터 로드."""
import json

from ..config import DATA_DIR

with open(DATA_DIR / "question_categories.json", encoding="utf-8") as f:
    _DATA = json.load(f)


def categories_payload() -> dict:
    return _DATA
