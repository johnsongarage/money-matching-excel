# money-matching-excel

포스 매출 ↔ 통장 맞추기 데모 (처음엔 배달 정산 맞추기 최소 데모) (hq 이름: `delivery-profit`).

- 빌드 없음, Vanilla JS. 첫 화면 `index.html` = **포스 매출 ↔ 통장 맞추기** (11/3 방향 전환, 11/5 출발점을 본사 엑셀 → 포스 매출로. 본사 엑셀은 청구·상계 자료. 예시 데이터는 파일 안).
- 배달 정산 화면: `delivery.html`(카드형)·`dashboard.html`(대시보드형), 예시 데이터·계산은 `data.js`(window.DEMO).
- 모든 화면 위쪽 "화면" 콤보 박스 = `screens.js`.
- `upload.html`: 정산서·통장 엑셀을 올려 맞추는 화면. 파일은 브라우저 안에서만 처리(서버·저장 없음). 가짜 양식은 `upload.html` 안 `fakeSettlement`/`fakeBank`.
- `hq-check.html`: 본사 정산서 ↔ 계약 조건 ↔ 통장 확인. 예시 `samples/본사_정산서_2026-10_예시.xlsx` (만드는 코드 `samples/make_samples.py`, 정답지 `answer.json`의 `hq`).
- `refs.js`: 세 화면 위쪽 "참고 문서" 콤보 박스 목록(제목·한 줄 설명·링크). 문서 추가는 여기 배열에.
- `docs/`: 참고 문서의 공개용 HTML 사본(원본은 Claude 문서). 옮길 때 가게·브랜드·실명은 일반 표현으로 바꾸고, 내부용(영업 멘트·수익 모델) 문서는 넣지 않는다.
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
