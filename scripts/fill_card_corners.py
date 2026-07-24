# 카드 앞면 이미지 귀퉁이 처리 스크립트 (재사용 가능)
#
# 카드 앞면 원본(사각 캔버스 + 둥근 프레임)의 흰 귀퉁이를 프레임 색으로 채운다.
# 새 카드 이미지를 받았을 때 이 스크립트를 다시 돌리면 된다.
#
# 사용법:
#   1. 원본(600×900 WebP, 흰 귀퉁이)을 backup/cards_original/ 에 둔다
#   2. .venv\Scripts\python.exe scripts\fill_card_corners.py
#   3. 처리 결과가 assets/cards/ 에 저장됨 → frontend/js/app.js 의 ASSET_VER 올리기
#
# 처리 내용:
#   - 카드별 프레임 색 샘플링(상단 변 중앙 안쪽 픽셀)
#   - 네 귀퉁이 flood fill (근접 흰색까지, 프레임 어두운 경계에서 정지)
#   - 프레임 호의 안티앨리어싱 띠(호 안쪽 OVER px)까지 덮어 곡선 이음선 제거
#   - 원본에서 단일 패스 저장(품질 85) — 반복 재압축 잔상 방지
import glob
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "backup" / "cards_original"
DST = ROOT / "assets" / "cards"

R = 41       # 프레임 라운드 반경 (600px 폭 기준 실측값)
OVER = 8     # 호 안쪽으로 덮는 여유(px) — 안티앨리어싱 이음선 제거
BOX = R + 8  # 귀퉁이 처리 영역


def main() -> None:
    files = sorted(glob.glob(str(SRC / "*.webp")))
    if not files:
        raise SystemExit(f"원본이 없습니다: {SRC}")
    for src in files:
        name = os.path.basename(src)
        im = Image.open(src).convert("RGB")
        w, h = im.size
        frame = im.getpixel((w // 2, 4))
        for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
            if sum(abs(a - b) for a, b in zip(im.getpixel(seed), frame)) > 60:
                ImageDraw.floodfill(im, seed, frame, thresh=80)
        px = im.load()
        corners = [
            ((0, 0), (R, R)),
            ((w - 1, 0), (w - 1 - R, R)),
            ((0, h - 1), (R, h - 1 - R)),
            ((w - 1, h - 1), (w - 1 - R, h - 1 - R)),
        ]
        for (cx, cy), (ox, oy) in corners:
            x0, x1 = (0, BOX) if cx == 0 else (w - BOX, w)
            y0, y1 = (0, BOX) if cy == 0 else (h - BOX, h)
            for y in range(y0, y1):
                for x in range(x0, x1):
                    if math.hypot(x - ox, y - oy) >= R - OVER:
                        px[x, y] = frame
        im.save(str(DST / name), "WEBP", quality=85, method=6)
    print(f"{len(files)}장 처리 완료 → {DST}")
    print("frontend/js/app.js 의 ASSET_VER 값을 올려 캐시를 무효화하세요.")


if __name__ == "__main__":
    main()
