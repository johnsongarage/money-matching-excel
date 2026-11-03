# money-matching-excel

배달 정산 맞추기 최소 데모 (hq 이름: `delivery-profit`).

- `index.html` 한 파일. 빌드 없음, Vanilla JS, 데이터는 파일 안 배열.
- 작업 지시서: hq `projects/delivery-profit-demo.md` — 범위("하지 않을 것" 포함)를 먼저 확인할 것.
- **공개 저장소**: 가짜 데이터만. 실데이터·실명·가게 이름·브랜드명 절대 커밋 금지.
- 수수료율·배달비는 예시로만 쓰고 실제 앱 요율로 단정하지 않는다.

## 사업 본부 연동 (kery27/hq)

이 프로젝트는 가르시아의 사업 본부 저장소 `kery27/hq`와 연결되어 있다.

- 세션을 시작할 때: `kery27/hq`를 세션에 추가하고 `STRATEGY.md`, `DECISIONS.md` 최근 항목,
  `projects/delivery-profit.md`를 읽는다. 지금 방향과 어긋나는 작업이면 먼저 말한다.
- 작업을 마칠 때 (의미 있는 진척이 있었을 때만):
  - `projects/delivery-profit.md`의 "현재 상태"와 "남은 일"을 갱신한다.
  - 사업 방향에 영향을 주는 결정(범위·가격·고객·중단/재개)은 `DECISIONS.md` 맨 위에 추가한다.
  - 커밋 메시지는 `[delivery-profit] 무엇을` 형식으로 hq에 푸시한다.
- 고객 실데이터·개인정보·비밀번호는 hq에 절대 쓰지 않는다.
