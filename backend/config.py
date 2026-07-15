"""환경 변수 및 경로 설정 — API 키는 .env(로컬) 또는 배포 환경변수로 관리한다."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
FRONTEND_DIR = ROOT_DIR / "frontend"
PROMPTS_DIR = ROOT_DIR / "prompts" / "templates"


def _writable_runtime_dir() -> Path:
    """쓰기 가능한 런타임 디렉터리를 고른다.

    Vercel 등 서버리스 환경은 프로젝트 폴더가 읽기 전용이라 mkdir 이 실패한다.
    이 경우 조용히 /tmp 로 폴백해 앱이 죽지 않게 한다.
    """
    candidate = Path(os.getenv("PUCCA_RUNTIME_DIR", ROOT_DIR / "runtime"))
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    except OSError:
        fallback = Path("/tmp/pucca_runtime")
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


RUNTIME_DIR = _writable_runtime_dir()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
