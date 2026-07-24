# 카드 앞면 이미지 (78장)

정통 78장 타로 이미지가 이 폴더에 들어 있습니다 (600×900 WebP, 2:3 비율).
`data/tarot_cards.json`의 `image` 값과 파일명이 일치해야 합니다.

## 네이밍 규칙

**메이저 아르카나 (22장)**
`major_00_the_fool.webp` ~ `major_21_the_world.webp` (번호 2자리 + 영문 이름)

**마이너 아르카나 (56장)** — 슈트별 14장
- 완드: `wands_01_ace.webp` ~ `wands_14_king.webp`
- 컵: `cups_01_ace.webp` ~ `cups_14_king.webp`
- 소드: `swords_01_ace.webp` ~ `swords_14_king.webp`
- 펜타클: `pentacles_01_ace.webp` ~ `pentacles_14_king.webp`

(숫자 01~10, 그다음 11=시종 / 12=기사 / 13=여왕 / 14=왕)

## 이미지 교체 시
- 같은 파일명으로 교체하면 `frontend/js/app.js` 상단 `ASSET_VER` 값을 올릴 것 (캐시 무효화).
- 뿌까 IP 라이선스 범위 내에서 제작/활용.
