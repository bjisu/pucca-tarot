"""Vercel 서버리스 함수 진입점 — backend 패키지의 FastAPI 앱을 노출한다.

@vercel/python 런타임이 이 모듈의 최상위 `app`(ASGI)을 실행한다.
로컬 실행은 기존대로 backend.main:app 사용(start_server.bat 변경 없음).
"""
from backend.main import app
