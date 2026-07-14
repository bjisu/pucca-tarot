# 뿌까 오라클 (Pucca Oracle)

뿌까가 정통 78장 타로로 일상 고민(연애·직장·금전·인간관계 등)을 반말로 다정하게
풀어주는 모바일 웹 서비스입니다.

- 진행 캐릭터: **뿌까** (반말, 발랄하고 따뜻한 타로 친구)
- 카드: **정통 78장 타로** (메이저 22 + 마이너 56)
- 질문: **8개 생활 카테고리** (연애·사랑 / 직장·진로 / 금전·재물 / 뷰티·관리 / 인간관계 / 취미·덕질 / 학업·시험 / 기념일)
- 스택: FastAPI + Vanilla JS SPA (반응형, 모바일 우선)

> 뿌까는 부즈(VOOZ) IP입니다. 라이선스 범위 내에서만 이미지·표현을 사용하세요.

## 주요 기능

| 기능 | 설명 |
|---|---|
| 오늘의 타로 | 카드 1장 — 같은 날 재접속 시 같은 카드 유지 |
| 클래식 타로 | 카드 3장 스프레드 — 현재 상황 / 필요한 조언 / 결과·전망 |
| 질문 리딩 | 카테고리 선택 → 예시 질문 선택 또는 직접 입력 |
| 카드 뽑기 | 부채꼴 덱을 좌우 스와이프(터치·마우스)로 넘기고 탭해서 선택 |
| 뿌까와 대화 | 방금 뽑은 질문·카드·해석 맥락을 기억하는 후속 챗봇 |
| 타로카드 리스트 | 78장 전체를 슈트별 탭으로 열람하는 도감 |
| AI 해석 | LLM Factory(Anthropic/OpenAI/Gemini 교체 가능), 키가 없으면 내장 해석으로 폴백 |
| 안전 분기 | 위기 신호(자해 등) 감지 시 점술 대신 도움 자원 안내 |

## 실행 방법 (비개발자용)

### 준비물
- Windows PC + [Python 3.10 이상](https://www.python.org/downloads/) (설치 시 "Add to PATH" 체크)

### 최초 1회 설정
1. 이 프로젝트 폴더에서 주소창에 `cmd` 입력 → Enter (명령창이 열립니다)
2. 아래 두 줄을 차례로 입력:
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

### 서버 켜기 (매번)
1. **`start_server.bat` 더블클릭** (또는 명령창에서 아래 입력)
   ```
   .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```
2. 브라우저에서 **http://localhost:8000** 접속
3. 끌 때는 검은 창을 닫거나 `Ctrl + C`

더 자세한 안내(문제 해결 포함)는 [RUN_GUIDE.md](RUN_GUIDE.md) 참고.

### AI 해석 켜기 (선택)
1. `.env.example`을 복사해 `.env`로 저장
2. `ANTHROPIC_API_KEY=` / `OPENAI_API_KEY=` / `GEMINI_API_KEY=` 중 하나에 실제 키 입력
3. 서버 재시작 — 키가 없으면 카드 기본 의미 기반의 내장 해석으로 동작합니다

### 이미지 넣기 (선택)
- 카드 78장: `assets/cards/` (파일명은 `data/tarot_cards.json`의 `image` 값과 일치 — 규칙은 `assets/cards/README.md`)
- 뿌까: `assets/character/pucca_main.png`
- 파일만 넣으면 자동 반영됩니다 (없으면 카드 이름 플레이스홀더 표시)

## 폴더 구조

```
pucca tarot/
├── backend/                  # FastAPI 백엔드
│   ├── main.py               #   앱 진입점 (API + 정적 파일 서빙)
│   ├── config.py             #   .env 로드, 경로 설정
│   ├── schemas.py            #   Pydantic 요청/응답 스키마
│   ├── llm/                  #   LLM Factory (anthropic / openai / gemini)
│   └── services/             #   카드·질문·세션·리딩 로직
├── frontend/                 # 반응형 웹 (Vanilla JS SPA)
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js             #   해시 라우팅 + 카드 스와이프 인터랙션
├── prompts/templates/
│   └── pucca_persona.yaml    # 뿌까 페르소나·리딩 프롬프트 (여기서 말투 수정)
├── data/
│   ├── tarot_cards.json      # 78장 카드 데이터
│   └── question_categories.json  # 8개 카테고리 + 예시 질문 58개
├── assets/                   # 배경·카드·캐릭터 이미지
├── docs/                     # PRD, User Flow
├── .cursorrules              # 개발 규칙
├── .env.example              # 환경 변수 예시 (실제 키는 .env 에)
├── requirements.txt
├── start_server.bat          # 더블클릭 실행용
└── RUN_GUIDE.md              # 비개발자용 상세 실행 가이드
```

## API 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/cards` | 78장 카드 데이터 |
| GET | `/api/categories` | 질문 카테고리 8개 |
| POST | `/api/reading/today` | 오늘의 타로 (uuid+날짜로 동일 카드 유지) |
| POST | `/api/reading/classic` | 클래식 3장 리딩 |
| POST | `/api/chat` | 뿌까 후속 대화 (인메모리 세션) |
| GET | `/api/health` | 서버·LLM 상태 확인 |
