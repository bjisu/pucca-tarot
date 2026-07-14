"""후속 대화 세션 — 서버 인메모리 관리 (MVP: 재시작 시 초기화 허용)."""
import time
import uuid as uuid_lib
from typing import Dict, List, Optional

_SESSIONS: Dict[str, dict] = {}
_MAX_SESSIONS = 500
_MAX_HISTORY = 20


def create_session(question: str, cards: List[dict], reading_summary: str) -> str:
    if len(_SESSIONS) >= _MAX_SESSIONS:
        oldest = min(_SESSIONS, key=lambda k: _SESSIONS[k]["created_at"])
        _SESSIONS.pop(oldest, None)
    sid = uuid_lib.uuid4().hex
    _SESSIONS[sid] = {
        "created_at": time.time(),
        "question": question,
        "cards": cards,
        "reading_summary": reading_summary,
        "history": [],
    }
    return sid


def get_session(sid: str) -> Optional[dict]:
    return _SESSIONS.get(sid)


def append_history(sid: str, role: str, content: str) -> None:
    session = _SESSIONS.get(sid)
    if not session:
        return
    session["history"].append({"role": role, "content": content})
    if len(session["history"]) > _MAX_HISTORY:
        session["history"] = session["history"][-_MAX_HISTORY:]
