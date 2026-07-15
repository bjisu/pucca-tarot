"""후속 대화 세션 — 무상태(stateless) 토큰 방식.

세션 정보(질문·뽑은 카드 id·리딩 요약)를 서버에 저장하지 않고,
프론트에 돌려주는 session_id(=인코딩 토큰) 안에 담는다. 대화 기록(history)은
프론트가 매 요청에 함께 보낸다. 덕분에 서버리스(여러 인스턴스, 재시작)에서도
대화가 끊기지 않는다.
"""
import base64
import json
from typing import List, Optional


def create_token(question: str, cards: List[dict], reading_summary: str) -> str:
    """리딩 결과를 담은 세션 토큰을 만든다(카드는 id 만 저장해 가볍게 유지)."""
    payload = {
        "q": question,
        "c": [c["id"] for c in cards],
        "s": reading_summary,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_token(token: str) -> Optional[dict]:
    """세션 토큰을 복원한다. 손상/구버전 토큰이면 None."""
    if not token:
        return None
    try:
        raw = base64.urlsafe_b64decode(token.encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict) or "c" not in data:
            return None
        return data
    except Exception:
        return None
