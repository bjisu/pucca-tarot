"""Vercel 진입점 — 기본 탐색 위치(최상위 main.py)에 FastAPI 앱을 노출한다.

로컬 실행은 기존대로 `backend.main:app` 을 사용한다(start_server.bat 변경 없음).
"""
from backend.main import app as fastapi_app

app = fastapi_app
