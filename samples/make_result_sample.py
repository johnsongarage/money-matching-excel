from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.page import PageMargins
wb = Workbook(); ws = wb.active; ws.title = '맞추기 결과'
GOLD='8A6400'; SOFT='FDF3CF'; PALE='FFFBEB'; RED='B42318'; GRN='1E7B34'; INK='1C1C1C'; MUTE='6B6B6B'
thin=Side(style='thin', color='D9D2BF'); B=Border(top=thin,bottom=thin,left=thin,right=thin)
F=lambda **k: Font(name='맑은 고딕', **k)
W='#,##0'; P='0.0%'
for c,w in zip('ABCDEFGH',[22,14,14,14,14,10,12,22]): ws.column_dimensions[c].width=w
def cell(r,c,v,**s):
    x=ws.cell(r,c,v); x.font=s.get('font',F(size=10,color=INK)); x.alignment=s.get('al',Alignment(vertical='center',wrap_text=True))
    if 'fill' in s: x.fill=PatternFill('solid',fgColor=s['fill'])
    if s.get('b'): x.border=B
    if 'nf' in s: x.number_format=s['nf']
    return x
def head(r,labels):
    for i,l in enumerate(labels,1): cell(r,i,l,font=F(size=9,bold=True,color=INK),fill=SOFT,b=1,al=Alignment(horizontal='center',vertical='center',wrap_text=True))
r=1
cell(r,1,'10월 정산 맞추기 결과',font=F(size=16,bold=True,color=GOLD)); ws.merge_cells('A1:H1'); ws.row_dimensions[1].height=26
cell(2,1,'○○가게 · 판매월 2026년 10월 · 견본 (숫자는 모두 가짜예요)',font=F(size=9,color=MUTE)); ws.merge_cells('A2:H2')
# 한눈에
r=4; cell(r,1,'한눈에',font=F(size=12,bold=True,color=INK))
r=5
for i,(l,f,col) in enumerate([('판 돈 합계','=B11',INK),('빠진 돈 (정산서로 설명됨)','=E11',INK),('확인할 차이','=-G11',RED)]):
    c=1+i*3 if i<2 else 7
    cell(r,c,l,font=F(size=9,color=MUTE),fill=PALE)
    cell(r+1,c,f,font=F(size=14,bold=True,color=col),fill=PALE,nf=W+'"원"')
    if c<7: ws.merge_cells(start_row=r,start_column=c,end_row=r,end_column=c+1); ws.merge_cells(start_row=r+1,start_column=c,end_row=r+1,end_column=c+1)
    else: ws.merge_cells(start_row=r,start_column=7,end_row=r,end_column=8); ws.merge_cells(start_row=r+1,start_column=7,end_row=r+1,end_column=8)
ws.row_dimensions[6].height=24
# 길별 맞추기
r=8; cell(r,1,'① 길별로 맞춰 보기',font=F(size=12,bold=True,color=INK))
head(9,['길','① 판 돈\n(포스)','② 정산서\n지급액','③ 통장 입금\n(지급일 기준)','빠진 돈\n(① − ②)','빠진 비율','차이\n(③ − ②)','결과'])
rows=[('매장 카드',18000000,17802000,17802000),('배민',3200000,'=B16-B23',None),('쿠팡이츠',1800000,'=C16-C23',None)]
bank={'배민':'=C10','쿠팡이츠':'=C12-38000'}
for i,(n,a,b,c) in enumerate(rows):
    rr=10+i
    cell(rr,1,n,b=1); cell(rr,2,a,b=1,nf=W); cell(rr,3,b,b=1,nf=W)
    cell(rr,4,c if c is not None else bank[n],b=1,nf=W)
    cell(rr,5,f'=B{rr}-C{rr}',b=1,nf=W); cell(rr,6,f'=IF(B{rr}=0,"",E{rr}/B{rr})',b=1,nf=P)
    cell(rr,7,f'=D{rr}-C{rr}',b=1,nf=W)
    cell(rr,8,f'=IF(G{rr}=0,"맞음","확인 필요")',b=1,font=F(size=10,bold=True,color=INK))
# fix order: 배민 row10? adjust: rows at 10,11,12 -> 매장카드 10, 배민 11, 쿠팡 12
ws['D11']='=C11'; ws['D12']='=C12-38000'
cell(13,1,'합계',font=F(size=10,bold=True),fill=PALE,b=1)
for col in 'BCDEG':
    cell(13,' ABCDEFGH'.index(col),f'=SUM({col}10:{col}12)',font=F(size=10,bold=True),fill=PALE,b=1,nf=W)
cell(13,6,'=E13/B13',font=F(size=10,bold=True),fill=PALE,b=1,nf=P); cell(13,8,'',fill=PALE,b=1)
ws['B11']='=B16'; ws['B12']='=C16'
# 합계 참조 위 '한눈에'는 13행
ws['A6']='=B13'; ws['D6']='=E13'; ws['G6']='=-G13'
for k in ('A6','D6','G6'): ws[k].number_format=W+'"원"'
# 빠진 돈 나눠 보기
r=15; head(15,['배달앱 빠진 돈 나눠 보기','배민','쿠팡이츠','성격','','','',''])
cell(15,1,'② 배달앱에서 빠진 돈, 나눠 보기',font=F(size=9,bold=True),fill=SOFT,b=1)
ws.merge_cells('D15:H15')
items=[('판 돈 (주문금액)',3200000,1800000,''),
('중개 수수료 (7.8%)','=ROUND(B16*0.078,0)','=ROUND(C16*0.078,0)','정해진 돈'),
('결제 수수료 (3%)','=ROUND(B16*0.03,0)','=ROUND((C16-C21)*0.03,0)','정해진 돈 · 쿠팡은 가게 할인 뺀 금액에'),
('가게 부담 배달비 (건당 2,900원)','=160*2900','=90*2900','정해진 돈 · 배민 160건, 쿠팡 90건'),
('수수료·배달비 부가세 (10%)','=ROUND((B17+B18+B19)*0.1,0)','=ROUND((C17+C18+C19)*0.1,0)','정해진 돈'),
('가게가 건 할인·쿠폰',120000,60000,'가게가 고르는 돈'),
('가게가 건 광고',0,30000,'가게가 고르는 돈'),
('빠진 돈 합계','=SUM(B17:B22)','=SUM(C17:C22)','')]
for i,(n,a,b,note) in enumerate(items):
    rr=16+i; bold = i in (0,7)
    cell(rr,1,n,b=1,font=F(size=10,bold=bold),fill=PALE if bold else None) if bold else cell(rr,1,n,b=1)
    cell(rr,2,a,b=1,nf=W,font=F(size=10,bold=bold)); cell(rr,3,b,b=1,nf=W,font=F(size=10,bold=bold))
    cell(rr,4,note,b=1,font=F(size=9,color=GOLD if '고르는' in note else MUTE)); ws.merge_cells(start_row=rr,start_column=4,end_row=rr,end_column=8)
# items rows 16..23; 합계 row 23
cell(24,1,'→ 배달 1만 원 팔면 통장에 오는 돈',font=F(size=10,bold=True,color=GOLD))
cell(24,2,'=ROUND((B16-B23)/B16*10000,0)',font=F(size=10,bold=True,color=GOLD),nf=W+'"원"')
cell(24,3,'=ROUND((C16-C23)/C16*10000,0)',font=F(size=10,bold=True,color=GOLD),nf=W+'"원"')
cell(24,4,'재료비 빼기 전, 부가세 신고 전',font=F(size=9,color=MUTE)); ws.merge_cells('D24:H24')
# 확인할 것
cell(26,1,'③ 확인할 것',font=F(size=12,bold=True,color=INK))
todo=[('1','쿠팡이츠 10/21 지급분이 정산서보다 38,000원 덜 들어왔어요. 정산서에 사유가 없어요.','쿠팡이츠 사장님 고객센터에 "10/21 지급분 38,000원 차감 사유" 문의'),
('2','가게가 고르는 돈(할인·광고)이 배민 120,000원, 쿠팡이츠 90,000원이에요.','다음 달 할인·광고를 그대로 둘지 정할 때 참고'),
('3','쿠팡이츠 중개 수수료는 할인 전 금액에 붙어요 (약관). 할인 60,000원에 약 5,100원.','공개된 약관 기준, 앱 공지가 바뀌면 다시 계산')]
head(27,['','내용','','','','어떻게','',''])
ws.merge_cells('B27:E27'); ws.merge_cells('F27:H27')
for i,(n,a,b) in enumerate(todo):
    rr=28+i; cell(rr,1,n,b=1,al=Alignment(horizontal='center',vertical='center'))
    cell(rr,2,a,b=1); ws.merge_cells(start_row=rr,start_column=2,end_row=rr,end_column=5)
    cell(rr,6,b,b=1,font=F(size=9,color=MUTE)); ws.merge_cells(start_row=rr,start_column=6,end_row=rr,end_column=8)
    ws.row_dimensions[rr].height=34
# 근거
foot=['근거 자료: ① 포스 매출 리포트(판매월) · ② 각 앱 사장님 사이트 정산 내역(판매 기간 조회) · ③ 인터넷뱅킹 거래내역(그 정산서의 지급일들)',
'빠진 돈은 줄마다 "얼마 × 몇 %"로 적어서 직접 검산하실 수 있어요. 받은 자료는 맞추는 데만 쓰고 저장하지 않아요.',
'수수료율·배달비는 예시예요. 실제로는 사장님 정산서에 적힌 숫자로 맞춰 드려요.',
'문의: 존슨거라지 · 인스타 DM @johnsongarage_ · johnsongarage.official@gmail.com']
for i,t in enumerate(foot):
    cell(32+i,1,t,font=F(size=8,color=MUTE)); ws.merge_cells(start_row=32+i,start_column=1,end_row=32+i,end_column=8)
ws.page_setup.orientation='portrait'; ws.page_setup.paperSize=9; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=1
ws.sheet_properties.pageSetUpPr.fitToPage=True; ws.page_margins=PageMargins(left=0.4,right=0.4,top=0.5,bottom=0.5)
ws.sheet_view.showGridLines=False
import os; wb.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), '맞추기_결과_견본.xlsx')); print('saved')
