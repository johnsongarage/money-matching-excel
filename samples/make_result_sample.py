# 제안용 "정산 맞추기 결과" 견본 한 장 (가짜 숫자). 같은 날짜끼리 두 짝:
#   가. 판 날끼리  ① 포스 판 돈 ↔ ② 카드사 승인·앱 주문내역  (판 게 다 잡혔나)
#   나. 입금 날끼리 ③ 정산내역 입금액 ↔ ④ 통장 입금          (적힌 대로 들어왔나)
# 길: 매장 카드 · 배민 · 쿠팡이츠 · 요기요 (요기요는 요기배달 · 영업일 5일 뒤 입금)
# 다시 만들기: python3 samples/make_result_sample.py
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.page import PageMargins

wb = Workbook(); ws = wb.active; ws.title = '맞추기 결과'
GOLD = '8A6400'; SOFT = 'FDF3CF'; PALE = 'FFFBEB'; RED = 'B42318'; INK = '1C1C1C'; MUTE = '6B6B6B'
thin = Side(style='thin', color='D9D2BF'); B = Border(top=thin, bottom=thin, left=thin, right=thin)
W = '#,##0'; P = '0.0%'


def F(**k):
    return Font(name='맑은 고딕', **k)


for col, w in zip('ABCDEFGH', [20, 13, 13, 12, 13, 11, 11, 24]):
    ws.column_dimensions[col].width = w


def cell(r, c, v, font=None, fill=None, nf=None, b=False, al=None):
    x = ws.cell(r, c, v)
    x.font = font or F(size=10, color=INK)
    x.alignment = al or Alignment(vertical='center', wrap_text=True)
    if fill: x.fill = PatternFill('solid', fgColor=fill)
    if nf: x.number_format = nf
    if b: x.border = B
    return x


def head(r, labels):
    for i, l in enumerate(labels, 1):
        cell(r, i, l, font=F(size=9, bold=True), fill=SOFT, b=True,
             al=Alignment(horizontal='center', vertical='center', wrap_text=True))


def merge(r, c1, c2):
    ws.merge_cells(start_row=r, start_column=c1, end_row=r, end_column=c2)


def title(r, t, size=12):
    cell(r, 1, t, font=F(size=size, bold=True)); merge(r, 1, 8)


# ── 행 위치 (길 4개) ─────────────────────────────────────
GA_T = 8; GA0 = GA_T + 2; GA_N = 4; GA_SUM = GA0 + GA_N              # 가: 8 제목 · 9 머리 · 10~13 · 14 합계
NA_T = GA_SUM + 2; NA0 = NA_T + 2; NA_N = 4; NA_SUM = NA0 + NA_N      # 나: 16 제목 · 17 머리 · 18~21 · 22 합계
NA_NOTE = NA_SUM + 2                                                 # 24
S3_T = NA_NOTE + 2; S30 = S3_T + 2                                   # ③: 26 제목 · 27 머리 · 28~37 항목
KEYS = ['sale', 'sup', 'brk', 'pay', 'dlv', 'disc', 'ad', 'adj', 'vat', 'paid']
R = {k: S30 + i for i, k in enumerate(KEYS)}                         # sale 28 … paid 37
S3_LOSS = R['paid'] + 1; S3_PER = S3_LOSS + 1                        # 38 · 39
TD_T = S3_PER + 2; TD0 = TD_T + 2                                    # ④: 41 제목 · 42 머리 · 43~48
COLS = {'B': '배민', 'C': '쿠팡이츠', 'D': '요기요'}

cell(1, 1, '10월 정산 맞추기 결과', font=F(size=16, bold=True, color=GOLD)); merge(1, 1, 8); ws.row_dimensions[1].height = 26
cell(2, 1, '○○가게 · 2026년 10월 · 견본 (숫자는 모두 가짜예요)', font=F(size=9, color=MUTE)); merge(2, 1, 8)

# ── 한눈에 (4~7행) ───────────────────────────────────────
todo = [('1', '포스에 10/31 취소 주문 15,000원이 남아 있어요. 포스 매출이 실제보다 많게 잡혀요.', '포스에서 그 주문을 취소 처리'),
        ('2', '배민 정산에서 지난달 클릭 광고비 38,000원이 이번에 빠졌어요.', '정산내역 "정산 제외 및 조정"에서 확인 · 광고를 계속 쓸지 정할 때 참고'),
        ('3', '가게가 고르는 돈(할인·광고)이 배민 120,000원, 쿠팡이츠 90,000원, 요기요 10,000원이에요.', '다음 달 할인·광고를 그대로 둘지 정할 때 참고'),
        ('4', '배민이 지원금 12,000원(배민클럽 지원)을 더해 줬어요.', '배민 혜택 내역에서 확인 · 지원이 끝나면 그만큼 덜 들어와요'),
        ('5', '쿠팡이츠 중개 수수료는 할인 전 금액에 붙어요 (약관). 할인 60,000원에 약 5,100원.', '공개된 약관 기준 · 앱 공지가 바뀌면 다시 계산'),
        ('6', '요기요 10/27 입금이 18,000원 적었어요. 10/14에 판 주문을 10/20에 부분취소한 환불이, 판 날이 아니라 취소한 날 기준으로 빠졌어요.', '요기요 정산내역 10/27 상세에서 확인 · 돈이 샌 게 아니에요')]
title(4, '한눈에')
boxes = [(1, '10월에 판 돈 (포스)', f'=B{GA_SUM}', INK), (4, '10월에 통장에 들어온 돈', f'=E{NA_SUM}', INK), (7, '살펴볼 것', f'{len(todo)}건 (아래 ④)', RED)]
for c, label, v, color in boxes:
    cell(5, c, label, font=F(size=9, color=MUTE), fill=PALE)
    cell(6, c, v, font=F(size=14, bold=True, color=color), fill=PALE, nf=W + '"원"')
    merge(5, c, c + 1 if c < 7 else 8); merge(6, c, c + 1 if c < 7 else 8)
ws.row_dimensions[6].height = 24
cell(7, 1, '판 날과 입금 날이 달라서 위 두 숫자를 바로 빼면 안 돼요. 같은 날짜끼리 아래 가·나로 맞춰요.', font=F(size=8, color=MUTE)); merge(7, 1, 8)

# ── 가. 판 날끼리 ─────────────────────────────────────────
title(GA_T, '① 가. 판 날끼리 — 판 게 다 잡혔나 (10월 1일~31일 판매)')
head(GA_T + 1, ['길', '① 판 돈\n(포스)', '② 주문 합계\n(카드사·앱)', '차이\n(① − ②)', '결과', '메모', '', ''])
merge(GA_T + 1, 6, 8)
ga = [('매장 카드', 18000000, 18000000, '카드사 승인 내역'),
      ('배민', 3215000, 3200000, '10/31 밤 취소된 주문 1건(15,000원)이 포스에 남아 있었어요. 돈이 샌 건 아니에요'),
      ('쿠팡이츠', 1800000, 1800000, '매출 내역서의 주문금액 (결제금액 아님)'),
      ('요기요', 620000, 620000, '주문내역의 주문금액 (배달요금 뺀 금액)')]
assert len(ga) == GA_N
for i, (n, a, o, memo) in enumerate(ga):
    r = GA0 + i
    cell(r, 1, n, b=True); cell(r, 2, a, b=True, nf=W); cell(r, 3, o, b=True, nf=W)
    cell(r, 4, f'=B{r}-C{r}', b=True, nf=W)
    cell(r, 5, f'=IF(ABS(D{r})<1,"맞음","확인 필요")', b=True, font=F(size=10, bold=True))
    cell(r, 6, memo, b=True, font=F(size=9, color=MUTE)); merge(r, 6, 8)
    ws.row_dimensions[r].height = 30 if len(memo) > 20 else 18
cell(GA_SUM, 1, '합계', font=F(size=10, bold=True), fill=PALE, b=True)
for c in (2, 3, 4):
    col = 'ABCD'[c - 1]
    cell(GA_SUM, c, f'=SUM({col}{GA0}:{col}{GA_SUM - 1})', font=F(size=10, bold=True), fill=PALE, b=True, nf=W)
cell(GA_SUM, 5, '', fill=PALE, b=True); cell(GA_SUM, 6, '', fill=PALE, b=True); merge(GA_SUM, 6, 8)

# ── 나. 입금 날끼리 ───────────────────────────────────────
title(NA_T, '② 나. 입금 날끼리 — 적힌 대로 들어왔나 (10월 1일~31일 입금)')
head(NA_T + 1, ['길', '정산 매출', '③ 정산\n입금액', '빠진 비율', '④ 통장\n입금', '차이\n(④ − ③)', '결과', '메모'])
# 나는 정산내역 기준: 카드는 카드사 입금 내역, 앱은 아래 '③ 나눠 보기'에서
na = [('매장 카드', 17950000, f'=ROUND(B{NA0}*(1-0.011),0)', '카드사 입금 내역 (수수료 1.1% 예시)'),
      ('배민', f"=B{R['sale']}", f"=B{R['paid']}", '정산내역. 지난달 광고비 38,000원이 이번에 빠졌어요 (아래)'),
      ('쿠팡이츠', f"=C{R['sale']}", f"=C{R['paid']}", '출금 내역 (출금해야 통장에)'),
      ('요기요', f"=D{R['sale']}", f"=D{R['paid']}", '정산내역 (주문일 + 영업일 5일 · 10/26~31 판 돈은 11월 초에)')]
assert len(na) == NA_N
for i, (n, sale, paid, memo) in enumerate(na):
    r = NA0 + i
    cell(r, 1, n, b=True); cell(r, 2, sale, b=True, nf=W); cell(r, 3, paid, b=True, nf=W)
    cell(r, 4, f'=IF(B{r}=0,"",(B{r}-C{r})/B{r})', b=True, nf=P)
    cell(r, 5, f'=C{r}', b=True, nf=W)  # 견본에선 통장이 정산내역과 같음 (보통 그래요)
    cell(r, 6, f'=E{r}-C{r}', b=True, nf=W)
    cell(r, 7, f'=IF(ABS(F{r})<1,"맞음","확인 필요")', b=True, font=F(size=10, bold=True))
    cell(r, 8, memo, b=True, font=F(size=9, color=MUTE))
    ws.row_dimensions[r].height = 30
r = NA_SUM
cell(r, 1, '합계', font=F(size=10, bold=True), fill=PALE, b=True)
for c, col in ((2, 'B'), (3, 'C'), (5, 'E'), (6, 'F')):
    cell(r, c, f'=SUM({col}{NA0}:{col}{NA_SUM - 1})', font=F(size=10, bold=True), fill=PALE, b=True, nf=W)
cell(r, 4, f'=(B{r}-C{r})/B{r}', font=F(size=10, bold=True), fill=PALE, b=True, nf=P)
cell(r, 7, '', fill=PALE, b=True); cell(r, 8, '', fill=PALE, b=True)
cell(NA_NOTE, 1, '나는 앱이 정산내역에 적은 대로 넣어 주니 대개 맞아요. 안 맞으면 정산내역의 상태(이월·정산보류·미납금 차감)부터 봐요. '
     '입금은 배민 영업일 3일, 쿠팡이츠 4일(출금해야), 요기요 5일 뒤라 월말에 판 돈은 다음 달 초에 와요.', font=F(size=8, color=MUTE)); merge(NA_NOTE, 1, 8)
ws.row_dimensions[NA_NOTE].height = 24

# ── ③ 배민 공식 그대로 나눠 보기 (10월 입금분 정산내역 상세) ──
# 배민 정산의 이해: 매출 + 배민지원금 − 비용 및 차감 ± 조정 − 부가세 = 입금금액 (쿠팡이츠·요기요도 같은 모양으로)
SG = '+#,##0;-#,##0;0'
title(S3_T, '③ 배달앱 정산, 배민 공식대로 나눠 보기 (10월 입금분 정산내역)')
head(S3_T + 1, ['항목', '배민', '쿠팡이츠', '요기요', '설명', '', '', '']); merge(S3_T + 1, 5, 8)


def fee(col, rate, base_after_disc=True):
    base = f"({col}{R['sale']}+{col}{R['disc']})" if base_after_disc else f"{col}{R['sale']}"
    return f'=-ROUND({base}*{rate},0)'


def vat(col):
    return f"=ROUND(({col}{R['brk']}+{col}{R['pay']}+{col}{R['dlv']}+{col}{R['ad']})*0.1,0)"


items = [
    ('sale', '매출 (주문금액)', 3180000, 1790000, 610000, '손님이 주문한 금액 · 배민 가게배달이면 배달팁 매출도 · 요기요는 배달요금 뺀 금액'),
    ('sup', '+ 배민지원금', 12000, 0, 0, '배민이 함께 낸 돈 (배민클럽 지원 등) → 입금에 더해져요 · 배민 혜택 내역에서 확인'),
    ('brk', '− 중개 수수료', fee('B', 0.078), fee('C', 0.078, False), fee('D', 0.097),
     '정해진 돈 · 배민·쿠팡 7.8%, 요기요 9.7% · 배민·요기요는 가게 할인 뺀 금액에, 쿠팡은 할인 전 금액에 (약관)'),
    ('pay', '− 결제 수수료 (3%)', fee('B', 0.03), fee('C', 0.03), fee('D', 0.03),
     '정해진 돈 · 가게 할인 뺀 금액에 · 배민은 연매출 구간별 1.4~3%, 요기요도 연매출 우대 (견본은 3%)'),
    ('dlv', '− 가게 부담 배달비 (건당 2,900원)', '=-159*2900', '=-89*2900', '=-30*2900', '정해진 돈 · 배민 159건, 쿠팡 89건, 요기요(요기배달) 30건'),
    ('disc', '− 할인·쿠폰 (가게 부담분)', -120000, -60000, -10000, '가게가 고르는 돈'),
    ('ad', '− 광고', 0, -30000, 0, '가게가 고르는 돈'),
    ('adj', '± 조정', -38000, 0, -18000,
     "배민: 지난달 클릭 광고비 중 덜 낸 돈 · 요기요: 10/20 부분취소 환불 (취소한 날 기준으로 빠져요) · 만나서결제·현장결제는 정산에서 빠지고 카드사·현금으로 따로 와요"),
    ('vat', '− 부가세 (수수료·배달비·광고비의 10%)', vat('B'), vat('C'), vat('D'), '앱이 받는 수수료·배달비·광고비의 10% · 할인엔 안 붙어요'),
    ('paid', '③ 입금금액 (위를 모두 더한 값)', f"=SUM(B{R['sale']}:B{R['vat']})", f"=SUM(C{R['sale']}:C{R['vat']})", f"=SUM(D{R['sale']}:D{R['vat']})", ''),
]
assert [k for k, *_ in items] == KEYS
for key, n, a, c, d, note in items:
    r = R[key]
    bold = key in ('sale', 'paid')
    cell(r, 1, n, b=True, font=F(size=10, bold=bold), fill=PALE if bold else None)
    nf = W if bold else SG
    for ci, v in ((2, a), (3, c), (4, d)):
        cell(r, ci, v, b=True, nf=nf, font=F(size=10, bold=bold))
    cell(r, 5, note, b=True, font=F(size=9, color=GOLD if '고르는' in note else MUTE)); merge(r, 5, 8)
    if len(note) > 60: ws.row_dimensions[r].height = 40
    elif len(note) > 28 or len(n) > 12: ws.row_dimensions[r].height = 28
cell(S3_LOSS, 1, '빠진 돈 (매출 − 입금)', b=True)
for ci, col in ((2, 'B'), (3, 'C'), (4, 'D')):
    cell(S3_LOSS, ci, f"={col}{R['sale']}-{col}{R['paid']}", b=True, nf=W)
cell(S3_LOSS, 5, '비용 + 부가세 + 조정 − 배민지원금', b=True, font=F(size=9, color=MUTE)); merge(S3_LOSS, 5, 8)
cell(S3_PER, 1, '→ 배달 1만 원 팔면 통장에 오는 돈', font=F(size=10, bold=True, color=GOLD))
for ci, col in ((2, 'B'), (3, 'C'), (4, 'D')):
    cell(S3_PER, ci, f"=ROUND({col}{R['paid']}/{col}{R['sale']}*10000,0)", font=F(size=10, bold=True, color=GOLD), nf=W + '"원"')
cell(S3_PER, 5, '재료비 빼기 전, 부가세 신고 전 · 배민은 지난달 광고비, 요기요는 부분취소 환불 포함', font=F(size=9, color=MUTE)); merge(S3_PER, 5, 8)
ws.row_dimensions[S3_PER].height = 28

# ── ④ 살펴볼 것 ───────────────────────────────────────────
title(TD_T, '④ 살펴볼 것')
head(TD_T + 1, ['', '내용', '', '', '', '어떻게', '', '']); merge(TD_T + 1, 2, 5); merge(TD_T + 1, 6, 8)
for i, (n, a, how) in enumerate(todo):
    r = TD0 + i
    cell(r, 1, n, b=True, al=Alignment(horizontal='center', vertical='center'))
    cell(r, 2, a, b=True); merge(r, 2, 5)
    cell(r, 6, how, b=True, font=F(size=9, color=MUTE)); merge(r, 6, 8)
    ws.row_dimensions[r].height = 44 if len(a) > 60 else 34

FOOT0 = TD0 + len(todo) + 1
foot = ['근거 자료: 가 = 포스 매출 리포트 · 카드사 승인 내역 · 앱 주문내역(쿠팡이츠는 매출 내역서) (판매일 10/1~10/31) / 나 = 앱 정산내역(쿠팡이츠는 출금 내역) · 카드사 입금 내역 · 인터넷뱅킹 거래내역 (입금일 10/1~10/31)',
        '빠진 돈은 줄마다 "얼마 × 몇 %"로 적어서 직접 검산하실 수 있어요. 받은 자료는 맞추는 데만 쓰고 저장하지 않아요.',
        '수수료율·배달비는 예시예요. 실제로는 사장님 정산내역에 적힌 숫자로 맞춰 드려요.',
        '문의: 존슨거라지 · 인스타 DM @johnsongarage_ · johnsongarage.official@gmail.com']
for i, t in enumerate(foot):
    cell(FOOT0 + i, 1, t, font=F(size=8, color=MUTE)); merge(FOOT0 + i, 1, 8)
    if i == 0: ws.row_dimensions[FOOT0].height = 24

ws.page_setup.orientation = 'portrait'; ws.page_setup.paperSize = 9
ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)
ws.sheet_view.showGridLines = False
wb.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), '맞추기_결과_견본.xlsx'))
print('saved')
