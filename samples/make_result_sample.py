# 제안용 "정산 맞추기 결과" 견본 한 장 (가짜 숫자). 같은 날짜끼리 두 짝:
#   가. 판 날끼리  ① 포스 판 돈 ↔ ② 카드사 승인·앱 주문내역  (판 게 다 잡혔나)
#   나. 입금 날끼리 ③ 정산내역 입금액 ↔ ④ 통장 입금          (적힌 대로 들어왔나)
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


cell(1, 1, '10월 정산 맞추기 결과', font=F(size=16, bold=True, color=GOLD)); merge(1, 1, 8); ws.row_dimensions[1].height = 26
cell(2, 1, '○○가게 · 2026년 10월 · 견본 (숫자는 모두 가짜예요)', font=F(size=9, color=MUTE)); merge(2, 1, 8)

# ── 한눈에 (4~7행) ───────────────────────────────────────
title(4, '한눈에')
boxes = [(1, '10월에 판 돈 (포스)', '=B13', INK), (4, '10월에 통장에 들어온 돈', '=E20', INK), (7, '살펴볼 것', '5건 (아래 ④)', RED)]
for c, label, v, color in boxes:
    cell(5, c, label, font=F(size=9, color=MUTE), fill=PALE)
    cell(6, c, v, font=F(size=14, bold=True, color=color), fill=PALE, nf=W + '"원"')
    merge(5, c, c + 1 if c < 7 else 8); merge(6, c, c + 1 if c < 7 else 8)
ws.row_dimensions[6].height = 24
cell(7, 1, '판 날과 입금 날이 달라서 위 두 숫자를 바로 빼면 안 돼요. 같은 날짜끼리 아래 가·나로 맞춰요.', font=F(size=8, color=MUTE)); merge(7, 1, 8)

# ── 가. 판 날끼리 (8~13행) ─────────────────────────────────
title(8, '① 가. 판 날끼리 — 판 게 다 잡혔나 (10월 1일~31일 판매)')
head(9, ['길', '① 판 돈\n(포스)', '② 주문 합계\n(카드사·앱)', '차이\n(① − ②)', '결과', '메모', '', ''])
merge(9, 6, 8)
ga = [('매장 카드', 18000000, 18000000, '카드사 승인 내역'),
      ('배민', 3215000, 3200000, '10/31 밤 취소된 주문 1건(15,000원)이 포스에 남아 있었어요. 돈이 샌 건 아니에요'),
      ('쿠팡이츠', 1800000, 1800000, '매출 내역서의 주문금액 (결제금액 아님)')]
for i, (n, a, o, memo) in enumerate(ga):
    r = 10 + i
    cell(r, 1, n, b=True); cell(r, 2, a, b=True, nf=W); cell(r, 3, o, b=True, nf=W)
    cell(r, 4, f'=B{r}-C{r}', b=True, nf=W)
    cell(r, 5, f'=IF(ABS(D{r})<1,"맞음","확인 필요")', b=True, font=F(size=10, bold=True))
    cell(r, 6, memo, b=True, font=F(size=9, color=MUTE)); merge(r, 6, 8)
    ws.row_dimensions[r].height = 30 if len(memo) > 20 else 18
cell(13, 1, '합계', font=F(size=10, bold=True), fill=PALE, b=True)
for c in (2, 3, 4):
    col = 'ABCD'[c - 1]
    cell(13, c, f'=SUM({col}10:{col}12)', font=F(size=10, bold=True), fill=PALE, b=True, nf=W)
cell(13, 5, '', fill=PALE, b=True); cell(13, 6, '', fill=PALE, b=True); merge(13, 6, 8)

# ── 나. 입금 날끼리 (15~21행) ──────────────────────────────
title(15, '② 나. 입금 날끼리 — 적힌 대로 들어왔나 (10월 1일~31일 입금)')
head(16, ['길', '정산 매출', '③ 정산\n입금액', '빠진 비율', '④ 통장\n입금', '차이\n(④ − ③)', '결과', '메모'])
# 나는 정산내역 기준: 카드는 카드사 입금 내역, 앱은 아래 '빠진 돈 나눠 보기'에서
na = [('매장 카드', 17950000, '=ROUND(B17*(1-0.011),0)', '카드사 입금 내역 (수수료 1.1% 예시)'),
      ('배민', '=B26', '=B35', '정산내역. 지난달 광고비 38,000원이 이번에 빠졌어요 (아래)'),
      ('쿠팡이츠', '=C26', '=C35', '출금 내역 (출금해야 통장에)')]
for i, (n, sale, paid, memo) in enumerate(na):
    r = 17 + i
    cell(r, 1, n, b=True); cell(r, 2, sale, b=True, nf=W); cell(r, 3, paid, b=True, nf=W)
    cell(r, 4, f'=IF(B{r}=0,"",(B{r}-C{r})/B{r})', b=True, nf=P)
    cell(r, 5, f'=C{r}', b=True, nf=W)  # 견본에선 통장이 정산내역과 같음 (보통 그래요)
    cell(r, 6, f'=E{r}-C{r}', b=True, nf=W)
    cell(r, 7, f'=IF(ABS(F{r})<1,"맞음","확인 필요")', b=True, font=F(size=10, bold=True))
    cell(r, 8, memo, b=True, font=F(size=9, color=MUTE))
    ws.row_dimensions[r].height = 30
r = 20
cell(r, 1, '합계', font=F(size=10, bold=True), fill=PALE, b=True)
for c, col in ((2, 'B'), (3, 'C'), (5, 'E'), (6, 'F')):
    cell(r, c, f'=SUM({col}17:{col}19)', font=F(size=10, bold=True), fill=PALE, b=True, nf=W)
cell(r, 4, '=(B20-C20)/B20', font=F(size=10, bold=True), fill=PALE, b=True, nf=P)
cell(r, 7, '', fill=PALE, b=True); cell(r, 8, '', fill=PALE, b=True)
cell(22, 1, '나는 앱이 정산내역에 적은 대로 넣어 주니 대개 맞아요. 안 맞으면 정산내역의 상태(이월·정산보류·미납금 차감)부터 봐요.', font=F(size=8, color=MUTE)); merge(22, 1, 8)

# ── 배민 공식 그대로 나눠 보기 (24~37행, 10월 입금분 정산내역 상세) ──
# 배민 정산의 이해: 매출 + 배민지원금 − 비용 및 차감 ± 조정 − 부가세 = 입금금액
SG = '+#,##0;-#,##0;0'
title(24, '③ 배달앱 정산, 배민 공식대로 나눠 보기 (10월 입금분 정산내역)')
head(25, ['항목', '배민', '쿠팡이츠', '설명', '', '', '', '']); merge(25, 4, 8)
items = [
    ('매출 (주문금액)', 3180000, 1790000, '고객이 주문한 금액 (가게배달이면 가게배달팁 매출도)'),
    ('+ 배민지원금', 12000, 0, '배민이 함께 낸 돈 (배민클럽 지원 등) → 입금에 더해져요 · 배민 혜택 내역에서 확인'),
    ('− 중개 수수료 (7.8%)', '=-ROUND((B26+B31)*0.078,0)', '=-ROUND(C26*0.078,0)', '정해진 돈 · 배민은 가게 할인 뺀 금액에, 쿠팡은 할인 전 금액에 (약관)'),
    ('− 결제 수수료 (3%)', '=-ROUND((B26+B31)*0.03,0)', '=-ROUND((C26+C31)*0.03,0)', '정해진 돈 · 가게 할인 뺀 금액에 · 배민은 연매출 구간별 1.4~3% (견본은 3%)'),
    ('− 가게 부담 배달비 (건당 2,900원)', '=-159*2900', '=-89*2900', '정해진 돈 · 배민 159건, 쿠팡 89건'),
    ('− 할인·쿠폰 (가게 부담분)', -120000, -60000, '가게가 고르는 돈'),
    ('− 광고', 0, -30000, '가게가 고르는 돈'),
    ('± 조정: 광고 미수금', -38000, 0, "지난달 클릭 광고비 중 덜 낸 돈 · 만나서결제·부분환불도 여기('정산 제외')로 빠져요. 만나서결제는 카드사·현금으로 따로 와요"),
    ('− 부가세 (수수료·배달비·광고비의 10%)', '=ROUND((B28+B29+B30+B32)*0.1,0)', '=ROUND((C28+C29+C30+C32)*0.1,0)', '배민이 받는 수수료·배달비·광고비에 붙는 세금 (배민 예시 화면: 우리가게클릭 이용요금의 10%) · 할인엔 안 붙어요'),
    ('③ 입금금액 (위를 모두 더한 값)', '=SUM(B26:B34)', '=SUM(C26:C34)', ''),
]
for i, (n, a, c, note) in enumerate(items):
    r = 26 + i
    bold = n.startswith(('매출', '③'))
    cell(r, 1, n, b=True, font=F(size=10, bold=bold), fill=PALE if bold else None)
    nf = W if r in (26, 35) else SG
    cell(r, 2, a, b=True, nf=nf, font=F(size=10, bold=bold)); cell(r, 3, c, b=True, nf=nf, font=F(size=10, bold=bold))
    cell(r, 4, note, b=True, font=F(size=9, color=GOLD if '고르는' in note else MUTE)); merge(r, 4, 8)
    if len(note) > 30: ws.row_dimensions[r].height = 28
cell(36, 1, '빠진 돈 (매출 − 입금)', b=True)
cell(36, 2, '=B26-B35', b=True, nf=W); cell(36, 3, '=C26-C35', b=True, nf=W)
cell(36, 4, '비용 + 부가세 + 조정 − 배민지원금', b=True, font=F(size=9, color=MUTE)); merge(36, 4, 8)
cell(37, 1, '→ 배달 1만 원 팔면 통장에 오는 돈', font=F(size=10, bold=True, color=GOLD))
cell(37, 2, '=ROUND(B35/B26*10000,0)', font=F(size=10, bold=True, color=GOLD), nf=W + '"원"')
cell(37, 3, '=ROUND(C35/C26*10000,0)', font=F(size=10, bold=True, color=GOLD), nf=W + '"원"')
cell(37, 4, '재료비 빼기 전, 부가세 신고 전 · 배민은 지난달 광고비 포함', font=F(size=9, color=MUTE)); merge(37, 4, 8)

# ── 살펴볼 것 (39~44행) ─────────────────────────────────
title(39, '④ 살펴볼 것')
head(40, ['', '내용', '', '', '', '어떻게', '', '']); merge(40, 2, 5); merge(40, 6, 8)
todo = [('1', '포스에 10/31 취소 주문 15,000원이 남아 있어요. 포스 매출이 실제보다 많게 잡혀요.', '포스에서 그 주문을 취소 처리'),
        ('2', '배민 정산에서 지난달 클릭 광고비 38,000원이 이번에 빠졌어요.', '정산내역 "정산 제외 및 조정"에서 확인 · 광고를 계속 쓸지 정할 때 참고'),
        ('3', '가게가 고르는 돈(할인·광고)이 배민 120,000원, 쿠팡이츠 90,000원이에요.', '다음 달 할인·광고를 그대로 둘지 정할 때 참고'),
        ('4', '배민이 지원금 12,000원(배민클럽 지원)을 더해 줬어요.', '배민 혜택 내역에서 확인 · 지원이 끝나면 그만큼 덜 들어와요'),
        ('5', '쿠팡이츠 중개 수수료는 할인 전 금액에 붙어요 (약관). 할인 60,000원에 약 5,100원.', '공개된 약관 기준 · 앱 공지가 바뀌면 다시 계산')]
for i, (n, a, how) in enumerate(todo):
    r = 41 + i
    cell(r, 1, n, b=True, al=Alignment(horizontal='center', vertical='center'))
    cell(r, 2, a, b=True); merge(r, 2, 5)
    cell(r, 6, how, b=True, font=F(size=9, color=MUTE)); merge(r, 6, 8)
    ws.row_dimensions[r].height = 34

foot = ['근거 자료: 가 = 포스 매출 리포트 · 카드사 승인 내역 · 앱 주문내역 (판매일 10/1~10/31) / 나 = 앱 정산내역 · 카드사 입금 내역 · 인터넷뱅킹 거래내역 (입금일 10/1~10/31)',
        '빠진 돈은 줄마다 "얼마 × 몇 %"로 적어서 직접 검산하실 수 있어요. 받은 자료는 맞추는 데만 쓰고 저장하지 않아요.',
        '수수료율·배달비는 예시예요. 실제로는 사장님 정산내역에 적힌 숫자로 맞춰 드려요.',
        '문의: 존슨거라지 · 인스타 DM @johnsongarage_ · johnsongarage.official@gmail.com']
for i, t in enumerate(foot):
    cell(47 + i, 1, t, font=F(size=8, color=MUTE)); merge(47 + i, 1, 8)
    if i == 0: ws.row_dimensions[47].height = 24

ws.page_setup.orientation = 'portrait'; ws.page_setup.paperSize = 9
ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)
ws.sheet_view.showGridLines = False
wb.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), '맞추기_결과_견본.xlsx'))
print('saved')
