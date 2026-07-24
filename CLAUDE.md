# 뿌까 오라클 — 프로젝트 작업 노트 (Claude Code용)

> 이 파일은 세션을 새로 시작할 때 Claude가 자동으로 읽는 작업 노트입니다.
> 기획 기준 문서: `.cursorrules`, `docs/PRD.md`, `docs/USER_FLOW.md` (개발 전 필독)
> 실행 안내: `README.md`, `RUN_GUIDE.md`

---

## 다음 세션 시작 시 지시사항 (먼저 할 일)

1. **커밋되지 않은 변경이 있으면 먼저 처리** — `git status`로 확인. (2026-07-15 기준 전부 커밋·푸시됨)
   커밋 전 반드시 `.env`가 스테이징에 없는지 확인. 커밋 메시지는 한국어로, 마지막 줄에
   `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
2. **서버 실행**: `start_server.bat` 더블클릭 또는
   `.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000` → http://localhost:8000
   (PATH의 `python`은 스토어 스텁이므로 쓰지 말 것. 실제 파이썬: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`)
3. **UI 수정 후에는 반드시 스크린샷으로 검증** (아래 "검증 방법" 참고). 사용자는 비개발자 —
   에러는 묻지 말고 직접 고치고 "뭐가 문제였는지 한 줄"로만 보고.

## 남은 작업 (백로그)

- [x] 카드 앞면 이미지 78장 — `assets/cards/*.webp`(600×900) 적용 완료 (2026-07-24)
- [ ] 뿌까 대화 아바타 이미지 (`assets/character/pucca_main.png` — 넣으면 자동 적용)
- [x] 이미지 압축 — 카드 78장·card·content_1~3 전부 WebP 전환 완료 (2026-07-24). 카드 뒷면 = `assets/image/card.webp`
- [ ] 결과·도감 화면 톤 미세 통일 검토 (전역 라이트 테마는 적용됨)
- [ ] `.env`에 LLM API 키 입력 시 AI 해석 활성화 (현재 내장 폴백 해석 동작 중)
- [ ] 뿌까 라이선스 확정 전까지 GitHub 저장소 Private 유지 권장

---

## 아키텍처 요약

- **백엔드**: FastAPI (`backend/`) — LLM Factory(`backend/llm/`, anthropic/openai/gemini, 키 없으면 폴백 해석),
  페르소나·프롬프트는 `prompts/templates/pucca_persona.yaml`, 오늘의 카드는 uuid+날짜 해시(결정론적, 저장 없음).
- **프론트**: 바닐라 JS SPA (`frontend/`) — 해시 라우팅(#/ → #/question → #/draw → #/result, #/dex).
  API: /api/cards, /api/categories, /api/reading/today, /api/reading/classic, /api/health.
  (후속 대화(챗) 기능은 2026-07-24 완전 제거 — /api/chat, 세션 토큰, chat_context 템플릿 삭제)
- **데이터**: `data/tarot_cards.json`(78장), `data/question_categories.json`(8카테고리) — 원본 유지, 화면에서 질문 이모지는 미표시.

## 디자인 컨벤션 (현재 확정 상태)

- **라이트 웜톤 테마**: 배경 크림 `--bg: #fcf5e7`(단색), 면 웜화이트 `#fffdf8`, 텍스트 브라운블랙 `#2b1a12`,
  포인트 딥레드 `#b3342a`(넓은 면적 금지, 포인트만), 보조 웜베이지. CSS 변수는 `style.css :root`.
- **홈**: 헤더 없음. 메뉴 카드 3개(클래식→오늘→리스트), 히어로 이미지 `assets/image/content_1~3.png`,
  다크 브라운블랙 뱃지 + 크림 테두리.
- **질문 선택**: 심플 상단(배경 이미지 없음) — 왼쪽 문구 2줄("요즘 어떤 고민이 있어?"/"고민을 알려줘!" 딥레드),
  오른쪽 뿌까 `hero.png`(가로 110px), 발끝이 입력창 상단에 살짝 겹침. 상단 여백 8px.
- **카드 뽑기**: 같은 히어로 스타일에 `hero2.png`. 카드 덱은 반원 아치(회전축 카드 아래 560px, 카드당 11°),
  풀블리드, 중앙 카드 강조. 카드 뒷면 = `assets/image/card.png`.
- **이모지**: 유니코드 12+(2019 이후) 이모지 금지 (구형 기기 네모 깨짐). 도감 탭: 🌟🔥🍷🗡️💰.

## 코드 패턴 (반드시 따를 것)

- **이미지 폴백**: 모든 에셋 이미지는 `<img src="..." onerror="this.remove()">` + 밑에 CSS 폴백.
  파일만 넣으면 자동 적용되는 구조 유지.
- **캐시 무효화**: 같은 파일명으로 이미지를 교체하면 `frontend/js/app.js` 상단 `ASSET_VER` 값을 올릴 것.
  CSS/JS는 `index.html`의 `?v=` 쿼리를 올릴 것. 사용자에게는 F5(또는 Ctrl+F5) 안내.
- **뿌까 PNG는 흰 배경(알파 없음)** → `mix-blend-mode: multiply`로 크림 배경에 녹임.
  multiply가 섞일 배경색이 같은 요소/조상에 있어야 함(없으면 흰 상자 노출).
- **클래스 충돌 주의**: 컴포넌트 클래스(.pucca)와 상태 클래스 이름 겹치지 않게 (과거 `msg pucca` 충돌 버그).
- **덱 인터랙션**: pointer 캡처 시 e.target이 컨테이너로 바뀌므로 pointerdown에서 탭 대상을 기억하는 방식 유지.

## 검증 방법 (UI 변경 시)

Edge 헤드리스 + puppeteer-core로 실제 화면 스크린샷 검증:
- puppeteer-core는 세션 scratchpad에 설치해 사용 (`npm i puppeteer-core`, Edge 경로:
  `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`).
- 전 플로우 스크립트 패턴: 홈 → `.menu-card` 클릭 → `.q-item` → `#qGo` → `.deck-card.centered` 3회 클릭(간격 1.1s)
  → `.result-q` 대기 → `location.hash='#/dex'`.
- 뷰포트 390×844(모바일 기준). API 검증은 `.venv` 파이썬으로 urllib POST (한글 출력은 `PYTHONIOENCODING=utf-8`).

## 작업 이력 (요약)

**2026-07-14**
- MVP 구축: FastAPI 백엔드(리딩/대화/위기 분기/오늘의 카드 고정), 바닐라 SPA(질문→스와이프 뽑기→결과→대화, 도감 78장), 페르소나 YAML, .env 키 관리, 폴백 해석(반말 변환+조사 처리).
- Python 3.12 winget 설치, venv 구성, start_server.bat, RUN_GUIDE.md.
- git 초기화, GitHub(bjisu/pucca-tarot) 연결. 커밋: MVP 초기 버전.
- 홈 화면 개편(히어로형 메뉴 카드), bg_1 배경 도입→이후 제거.

**2026-07-15**
- 전체 라이트 웜톤 전환 → 단색 크림 배경 확정. content_1~3 메뉴 이미지, 뱃지 가독성 개선.
- 버그 수정: 덱 초기 중앙 카드 부재, 대화 말풍선 클래스 충돌, 이모지 호환(🪄→🔥, 🪙→💰), 질문 이모지 제거.
- 커밋 3건: "홈 화면 개선…", "홈 메뉴 카드 뱃지…", "질문 선택 화면 개선 및 에셋 정리".
- 질문 선택 히어로 수차례 개편 → 최종: 심플 크림 + 좌 문구/우 뿌까(110px) + 입력창 살짝 겹침.
- 카드뽑기 히어로 hero2 적용, 카드 덱 아치형 개편, card.png 카드 뒷면 적용. 커밋: "카드뽑기 화면 개선…" (푸시 완료).
- caveman 플러그인 부산물(.agents, .cursor 등 8개 항목) 프로젝트에서 삭제.

## 사용자 소통 규칙

- 한국어, 비개발자 기준 단계별 안내. 에러는 직접 고치고 원인 한 줄 보고.
- 이동/수치 요청은 스크린샷 실측으로 확인 후 보고. 완료 시 커밋 여부를 물어볼 것(임의 커밋 금지).
