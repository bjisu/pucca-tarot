@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  ✦ 뿌까 오라클 서버를 시작합니다...
echo  ✦ 브라우저에서  http://localhost:8000  으로 접속하세요.
echo  ✦ 끄려면 이 창에서 Ctrl+C 를 누르거나 창을 닫으세요.
echo.
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
