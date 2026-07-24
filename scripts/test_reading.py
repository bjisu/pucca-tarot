# 리딩 API 자동 검증 — 스키마 완전성 / 카드 이름 일치 / 질문 반영 / 반말 체크 / 오늘의 카드 고정
import json
import re
import sys
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8000"
ROOT = str(Path(__file__).resolve().parents[1])

cats = json.load(open(ROOT + "/data/question_categories.json", encoding="utf-8"))["categories"]

def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

# 존댓말 어미 검출 — 문장 끝(구두점/공백/끝)에 오는 경우만.
# "필요한", "요즘" 같은 단어 중간 '요'는 제외
POLITE = re.compile(
    r"(습니다|입니다|세요|해요|예요|이에요|어요|아요|네요|지요|까요|군요|돼요|되요|줘요|봐요|와요|냥)"
    r"(?=[\s.,!?~'\")”]|$)"
)

def polite_hits(text):
    return [m.group(0) for m in POLITE.finditer(text)]

def check_today(d, question):
    errs = []
    for k in ("reading_type", "question", "card", "one_line", "interpretation", "advice", "llm_provider"):
        if k not in d:
            errs.append(f"스키마 누락: {k}")
    if errs:
        return errs, ""
    card = d["card"]
    text = d["one_line"] + " " + d["interpretation"] + " " + d["advice"]
    if card["name_en"] not in d["interpretation"]:
        errs.append(f"카드 이름 불일치: '{card['name_en']}'이 해석에 없음")
    if question and question not in d["interpretation"]:
        errs.append("질문 미반영: 해석에 질문 문구 없음")
    hits = polite_hits(text)
    if hits:
        errs.append(f"존댓말 검출: {hits[:5]}")
    return errs, text

def check_classic(d, question):
    errs = []
    for k in ("reading_type", "question", "positions", "overall", "advice", "llm_provider"):
        if k not in d:
            errs.append(f"스키마 누락: {k}")
    if errs:
        return errs, ""
    if len(d["positions"]) != 3:
        errs.append(f"포지션 {len(d['positions'])}개 (3개 아님)")
    text_all = d["overall"] + " " + d["advice"]
    for p in d["positions"]:
        for k in ("position", "card", "interpretation"):
            if k not in p:
                errs.append(f"포지션 스키마 누락: {k}")
                break
        else:
            text_all += " " + p["interpretation"]
            if p["card"]["name_en"] not in p["interpretation"]:
                errs.append(f"카드 이름 불일치: {p['position']}의 '{p['card']['name_en']}'이 해석에 없음")
    if question and question not in d["overall"]:
        errs.append("질문 미반영: 종합 해석에 질문 문구 없음")
    hits = polite_hits(text_all)
    if hits:
        errs.append(f"존댓말 검출: {hits[:5]}")
    return errs, text_all

results = []
# 8개 카테고리 질문을 today/classic 번갈아 + 직접 입력형 2개
cases = []
for i, c in enumerate(cats):
    q = c["questions"][i % len(c["questions"])]["text"]
    cases.append(("today" if i % 2 == 0 else "classic", f"[{c['name']}] {q}", q))
cases.append(("today", "[직접입력] 이직 준비 중인데 지금 회사를 계속 다녀야 할까?", "이직 준비 중인데 지금 회사를 계속 다녀야 할까?"))
cases.append(("classic", "[직접입력] 요즘 매일 무기력한데 어떻게 벗어날 수 있을까?", "요즘 매일 무기력한데 어떻게 벗어날 수 있을까?"))

for mode, label, q in cases:
    d = post(f"/api/reading/{mode}", {"uuid": f"test-{mode}-{len(results)}", "question": q})
    errs, _ = (check_today if mode == "today" else check_classic)(d, q)
    results.append((mode, label, errs))

# 오늘의 카드 고정 확인 — 같은 uuid 2회 호출
d1 = post("/api/reading/today", {"uuid": "same-uuid-check", "question": "오늘 어때?"})
d2 = post("/api/reading/today", {"uuid": "same-uuid-check", "question": "오늘 어때?"})
same = d1["card"]["id"] == d2["card"]["id"]
results.append(("today×2", f"[동일 uuid 카드 고정] {d1['card']['name_en']} vs {d2['card']['name_en']}",
                [] if same else ["같은 uuid인데 다른 카드"]))

fail = 0
for mode, label, errs in results:
    status = "PASS" if not errs else "FAIL"
    if errs:
        fail += 1
    print(f"{status} | {mode:8s} | {label}")
    for e in errs:
        print(f"       └ {e}")
print(f"\n합계: {len(results)}건 중 통과 {len(results)-fail} / 실패 {fail}")
sys.exit(1 if fail else 0)
