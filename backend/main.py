"""뿌까 오라클 — FastAPI 앱 진입점.

실행:  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
접속:  http://localhost:8000
"""
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import ASSETS_DIR, FRONTEND_DIR
from .schemas import (
    ClassicReadingResponse,
    CrisisResponse,
    ReadingRequest,
    TodayReadingResponse,
)
from .services import card_service, question_service, reading_service

app = FastAPI(title="뿌까 오라클 (Pucca Oracle)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    from .llm.factory import get_provider

    provider = get_provider()
    return {"status": "ok", "llm_provider": provider.name if provider else "fallback"}


@app.get("/api/cards")
def cards():
    return card_service.deck_payload()


@app.get("/api/categories")
def categories():
    return question_service.categories_payload()


@app.post(
    "/api/reading/today",
    response_model=Union[TodayReadingResponse, CrisisResponse],
)
def reading_today(req: ReadingRequest):
    return reading_service.today_reading(req.uuid or "anonymous", req.question)


@app.post(
    "/api/reading/classic",
    response_model=Union[ClassicReadingResponse, CrisisResponse],
)
def reading_classic(req: ReadingRequest):
    return reading_service.classic_reading(req.uuid or "anonymous", req.question)


# 정적 파일: 카드/캐릭터 이미지 → /assets, 프론트엔드 → /
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
