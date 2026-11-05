"""현실형 예시 파일 만들기 — 가상 분식집 2026년 10월 한 달치.

모두 지어낸 데이터다. 칸 구성은 공개 안내(배달앱 사장님 사이트의 정산 항목·정산 주기)를
참고해 비슷하게 만들었고, 수수료율·배달비는 예시일 뿐 실제 앱 요율이 아니다.

  python3 samples/make_samples.py   → samples/*.xlsx, samples/answer.json
"""
import datetime as dt
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

OUT = Path(__file__).parent
rnd = random.Random(1029)

HOLIDAYS = {dt.date(2026, 10, 5), dt.date(2026, 10, 9)}  # 개천절 대체공휴일, 한글날


def biz(d):
    return d.weekday() < 5 and d not in HOLIDAYS


def add_biz(d, n):
    while n:
        d += dt.timedelta(days=1)
        if biz(d):
            n -= 1
    return d


def days(a, b):
    d = a
    while d <= b:
        yield d
        d += dt.timedelta(days=1)


MENU = [("떡볶이 세트", 16000), ("김밥 2줄+라면", 13500), ("모둠튀김 세트", 19000),
        ("로제떡볶이 세트", 21000), ("치즈김밥 3줄", 15000), ("순대+떡볶이", 17500),
        ("가족 세트", 32000), ("쫄면+김밥", 14500)]

# 예시 요율 (실제 요율 아님)
A = dict(broker=0.068, pay=0.03, delivery=3100)   # 매일 정산, 3영업일 뒤 입금
B = dict(broker=0.078, pay=0.03, delivery=2900)   # 먼저 7.8% 떼고 다음 달 초 차액 환급, 주 단위 지급


def order_amount():
    _, p = rnd.choice(MENU)
    q = rnd.choice([1, 1, 1, 2])
    return p * q if q == 1 else p + rnd.choice(MENU)[1]


answer = {"planted": [], "notes": []}

# ------------------------------------------------------------------ A앱 (매일 정산형)
a_rows = []
a_seq = 0
for d in days(dt.date(2026, 10, 1), dt.date(2026, 10, 31)):
    n = rnd.randint(7, 12) if d.weekday() >= 4 else rnd.randint(5, 9)
    due = add_biz(d, 3)
    for i in range(n):
        a_seq += 1
        sale = order_amount()
        kind = "포장" if rnd.random() < 0.15 else "배달"
        broker = round(sale * A["broker"])
        pay = round(sale * A["pay"])
        deliv = A["delivery"] if kind == "배달" else 0
        disc = rnd.choice([0, 0, 0, 0, 1000, 2000])
        vat = round((broker + pay + deliv) * 0.1)
        adj, note = 0, ""
        cut = broker + pay + deliv + disc + vat
        a_rows.append(dict(t=dt.datetime(d.year, d.month, d.day, 11 + (i * 7) % 11, (i * 13) % 60),
                           no=f"A{d:%y%m%d}{i + 1:03d}", kind=kind, sale=sale, broker=broker, pay=pay,
                           deliv=deliv, disc=disc, ad=0, vat=vat, adj=adj, note=note, due=due, state="입금완료"))
    # 하루 한 줄: 클릭 광고비 (광고비에도 부가세)
    ad = rnd.choice([2400, 3000, 3600, 4200])
    a_rows.append(dict(t=dt.datetime(d.year, d.month, d.day, 23, 59), no="", kind="광고", sale=0, broker=0, pay=0,
                       deliv=0, disc=0, ad=ad, vat=round(ad * 0.1), adj=0, note="클릭 광고 이용료", due=due, state="입금완료"))

# 심은 문제 ①: 10/13 주문 묶음 정산보류
for r in a_rows:
    if r["t"].date() == dt.date(2026, 10, 13):
        r["state"] = "정산보류"
answer["planted"].append({"id": "hold", "app": "A앱", "due": str(add_biz(dt.date(2026, 10, 13), 3)),
                          "what": "10/13 주문분이 정산보류 — 통장에 입금 없음"})
# 심은 문제 ②: 조정금액 (고객 보상) — 정산서에 적혀 있음 → '기타'로 보여야 함
target = next(r for r in a_rows if r["t"].date() == dt.date(2026, 10, 17) and r["kind"] == "배달")
target["adj"], target["note"] = -3000, "고객 보상(조리 지연)"
answer["planted"].append({"id": "adj", "app": "A앱", "due": str(target["due"]),
                          "what": "10/17 주문 1건에 조정금액 −3,000원(고객 보상) — 정산서에는 있음"})

for r in a_rows:
    r["net"] = r["sale"] - (r["broker"] + r["pay"] + r["deliv"] + r["disc"] + r["ad"] + r["vat"]) + r["adj"]
    if r["state"] == "입금완료" and r["due"] > dt.date(2026, 11, 5):
        r["state"] = "입금예정"

# ------------------------------------------------------------------ B앱 (주 단위 지급형)
b_rows = []
for d in days(dt.date(2026, 9, 28), dt.date(2026, 11, 1)):
    n = rnd.randint(3, 6) if d.weekday() >= 4 else rnd.randint(2, 4)
    monday = d - dt.timedelta(days=d.weekday())
    pay_day = monday + dt.timedelta(days=9)  # 다음 주 수요일 (가정)
    for i in range(n):
        sale = order_amount()
        broker = round(sale * B["broker"])
        pay = round(sale * B["pay"])
        deliv = B["delivery"]
        coupon = rnd.choice([0, 0, 0, 1000])
        vat = round((broker + pay + deliv) * 0.1)
        b_rows.append(dict(d=d, no=f"B{rnd.randint(10**7, 10**8 - 1)}", sale=sale, broker=broker, pay=pay,
                           deliv=deliv, coupon=coupon, vat=vat, net=sale - broker - pay - deliv - coupon - vat,
                           pay_day=pay_day, note=""))
# 9월분 중개이용료 환급 (확정 구간 6.8% → 1.0%p 환급 + 부가세)
sept_sales = 2_140_000
refund = round(sept_sales * 0.01 * 1.1)
b_rows.append(dict(d=dt.date(2026, 10, 1), no="", sale=0, broker=0, pay=0, deliv=0, coupon=0, vat=0,
                   net=refund, pay_day=dt.date(2026, 10, 8), note="9월분 중개이용료 환급"))
b_rows.sort(key=lambda r: (r["d"], r["no"] == ""))
# 심은 문제 ③: 환급금이 통장에 안 들어옴
answer["planted"].append({"id": "refund", "app": "B앱", "due": "2026-10-08",
                          "what": f"9월분 중개이용료 환급 {refund:,}원이 통장에 안 들어옴"})

# ------------------------------------------------------------------ 통장
def batches(rows, key_due, key_net, skip=lambda r: False):
    m = {}
    for r in rows:
        if skip(r):
            continue
        m[r[key_due]] = m.get(r[key_due], 0) + r[key_net]
    return m


a_b = batches(a_rows, "due", "net", skip=lambda r: r["state"] == "정산보류")
b_b = batches(b_rows, "pay_day", "net", skip=lambda r: r["note"].startswith("9월분"))

lines = []
for due, amt in a_b.items():
    if due > dt.date(2026, 11, 5):
        continue
    if due == dt.date(2026, 10, 26):        # 심은 문제 ④: 사유 없이 덜 들어옴
        amt -= 3300
    if due == dt.date(2026, 10, 22):        # 심은 문제 ⑤: 하루 늦게 들어옴
        due = add_biz(due, 1)
    lines.append((dt.datetime.combine(due, dt.time(9, 40)), "타행입금", "A앱정산", 0, amt, "인터넷"))
answer["planted"].append({"id": "short", "app": "A앱", "due": "2026-10-26",
                          "what": "10/26 입금이 정산서보다 3,300원 덜 들어옴 (사유 안 적힘)"})
answer["planted"].append({"id": "late", "app": "A앱", "due": "2026-10-22",
                          "what": "10/22 예정 입금이 하루 늦은 10/23에 들어옴"})
# 9월 말 주문분 — 10월 초에 들어오지만 10월 정산서엔 없음 (정산 시점 차이)
for d, amt in [(dt.date(2026, 10, 1), 182_340), (dt.date(2026, 10, 2), 141_905), (dt.date(2026, 10, 6), 167_220)]:
    lines.append((dt.datetime.combine(d, dt.time(9, 40)), "타행입금", "A앱정산", 0, amt, "인터넷"))
answer["planted"].append({"id": "timing", "app": "A앱", "due": "2026-10-01~10-06",
                          "what": "9월 말 주문분 입금 3건 — 10월 정산서에 없는 입금 (정상, 시점 차이)"})
for due, amt in b_b.items():
    lines.append((dt.datetime.combine(due, dt.time(10, 5)), "타행입금", "B앱지급", 0, amt, "인터넷"))

# 배달앱이 아닌 돈 (대조 대상 아님)
for d in days(dt.date(2026, 10, 1), dt.date(2026, 11, 5)):
    if biz(d):
        lines.append((dt.datetime.combine(d, dt.time(14, 20)), "CMS입금", "카드사 매출대금",
                      0, rnd.randint(18, 46) * 10_000 + rnd.randint(0, 99) * 100, "CMS"))
lines += [
    (dt.datetime(2026, 10, 25, 9, 0), "자동이체", "임대료", 1_650_000, 0, "자동이체"),
    (dt.datetime(2026, 10, 15, 8, 30), "자동이체", "배달대행 충전", 300_000, 0, "인터넷"),
    (dt.datetime(2026, 10, 27, 11, 12), "자동이체", "전기요금", 238_400, 0, "자동이체"),
    (dt.datetime(2026, 10, 30, 18, 3), "체크카드", "식자재마트", 412_800, 0, "체크카드"),
]
lines.sort()


# ------------------------------------------------------------------ 본사 정산서 (바이저가 내려주는 엑셀)
# 예시 계약 (실제 브랜드 조건 아님): 로열티 = 공급가액(부가세 뺀 매출)의 3%, 고객 배달팁 제외
#   광고분담금 월 50,000원+VAT, 기프티콘 발행사 수수료 8%를 본사·점주 반반, 동의한 청구 항목만
CONTRACT = {"royalty_rate": 0.03, "royalty_basis": "공급가액", "include_tip": False, "ad_fee": 50_000,
            "gift_fee_rate": 0.08, "gift_owner_share": 0.5,
            "agreed": ["물품대금", "로열티", "광고분담금", "기프티콘", "본사앱"]}
a_del = [r for r in a_rows if r["kind"] == "배달"]
b_oct = [r for r in b_rows if r["no"] and r["d"].month == 10]
TIP = 2000  # 고객이 낸 배달팁 (주문당, 예시)
channels = [
    ("매장 카드", 612, 7_856_000, 0), ("매장 현금", 41, 384_500, 0),
    ("A앱 배달", sum(1 for r in a_rows if r["kind"] != "광고"), sum(r["sale"] for r in a_rows), len(a_del) * TIP),
    ("B앱 배달", len(b_oct), sum(r["sale"] for r in b_oct), len(b_oct) * TIP),
    ("본사앱", 38, 642_000, 0), ("기프티콘 사용", 97, 1_126_000, 0),
]
def supply(v): return round(v / 1.1)
sales_rows = [[c, n, v, supply(v), v - supply(v), t] for c, n, v, t in channels]
tot_v = sum(r[2] for r in sales_rows); tot_s = sum(r[3] for r in sales_rows); tot_t = sum(r[5] for r in sales_rows)
sales_rows.append(["합계", sum(r[1] for r in sales_rows), tot_v, tot_s, tot_v - tot_s, tot_t])

claims = []  # [청구일, 구분, 발주번호, 내용, 공급가액, 부가세, 출금예정일, 비고]
items = ["떡볶이 소스·떡", "튀김류 냉동", "김밥 재료 세트", "포장 용기·봉투", "소스·양념 묶음", "음료·부자재"]
po = 0
for d in days(dt.date(2026, 10, 1), dt.date(2026, 10, 31)):
    if d.weekday() in (0, 3):  # 월·목 발주
        po += 1
        sup = rnd.randint(28, 66) * 10_000 + rnd.randint(0, 9) * 1_000
        pay = dt.date(2026, 10, 20) if d.day <= 15 else dt.date(2026, 11, 5)
        claims.append([d, "물품대금", f"PO-2610{po:02d}", rnd.choice(items) + " 외", sup, round(sup * 0.1), pay, ""])
dup = next(c for c in claims if c[0] == dt.date(2026, 10, 22))
claims.insert(claims.index(dup) + 1, list(dup))  # 심은 문제: 같은 발주번호 두 번
end, pay2 = dt.date(2026, 10, 31), dt.date(2026, 11, 5)
roy_base_hq = tot_v + tot_t  # 본사 계산: 부가세 포함 매출 + 배달팁
roy_hq = round(roy_base_hq * CONTRACT["royalty_rate"])
roy_ok = round(tot_s * CONTRACT["royalty_rate"])
gift_use = 1_126_000
gift_fee_hq = round(gift_use * CONTRACT["gift_fee_rate"])          # 본사: 수수료 전부 점주에게
gift_fee_ok = round(gift_use * CONTRACT["gift_fee_rate"] * CONTRACT["gift_owner_share"])
app_pay = 642_000 - round(642_000 * 0.03)
claims += [
    [end, "로열티", "", "10월 로열티 (매출의 3%)", roy_hq, round(roy_hq * 0.1), pay2, f"기준 매출 {roy_base_hq:,}원"],
    [end, "광고분담금", "", "10월 광고분담금", 50_000, 5_000, pay2, ""],
    [end, "판촉분담금", "", "10월 할인 행사 분담금", 120_000, 12_000, pay2, "가을 할인 행사"],
    [end, "기프티콘", "", "기프티콘 사용액 지급", -gift_use, 0, pay2, "97건 사용"],
    [end, "기프티콘", "", "기프티콘 수수료", gift_fee_hq, 0, pay2, "발행사 수수료 8%"],
    [end, "본사앱", "", "본사앱 주문 지급 (결제수수료 3% 차감)", -app_pay, 0, pay2, "38건"],
]
claims.sort(key=lambda c: (c[6], c[0], c[1] != "물품대금"))
due_sum = {}
for c in claims:
    due_sum[c[6]] = due_sum.get(c[6], 0) + c[4] + c[5]
lines.append((dt.datetime(2026, 10, 20, 10, 0), "자동이체", "본사 정산", due_sum[dt.date(2026, 10, 20)], 0, "자동이체"))
lines.append((dt.datetime(2026, 11, 5, 10, 0), "자동이체", "본사 정산", due_sum[pay2] + 15_000, 0, "자동이체"))  # 심은 문제: 15,000원 더 빠짐
lines.sort()

wb = Workbook()
ws = wb.active; ws.title = "매출집계"
for r in [["가맹점 월 정산서 (예시 양식 · 지어낸 데이터)"], ["정산월: 2026년 10월 / 매장: 예시 분식 ○○점"], [],
          ["구분", "건수", "매출액(부가세포함)", "공급가액", "부가세", "고객 배달팁"]] + sales_rows:
    ws.append(r)
for i, w in enumerate([14, 7, 18, 13, 11, 12]): ws.column_dimensions[chr(65 + i)].width = w
ws2 = wb.create_sheet("청구내역")
ws2.append(["청구일", "구분", "발주번호", "내용", "공급가액", "부가세", "청구금액", "출금예정일", "비고"])
for c in claims:
    ws2.append([c[0].isoformat(), c[1], c[2], c[3], c[4], c[5], c[4] + c[5], c[6].isoformat(), c[7]])
ws2.append(["", "합계", "", "", sum(c[4] for c in claims), sum(c[5] for c in claims), sum(c[4] + c[5] for c in claims), "", ""])
for i, w in enumerate([11, 10, 11, 30, 11, 9, 11, 11, 18]): ws2.column_dimensions[chr(65 + i)].width = w
wb.save(OUT / "본사_정산서_2026-10_예시.xlsx")

answer["hq"] = {
    "contract": CONTRACT,
    "royalty": {"hq": roy_hq, "ok": roy_ok, "base_hq": roy_base_hq, "base_ok": tot_s},
    "gift_fee": {"hq": gift_fee_hq, "ok": gift_fee_ok},
    "dup_po": dup[2], "dup_amount": dup[4] + dup[5],
    "promo": 132_000,
    "withdraw": {"2026-10-20": due_sum[dt.date(2026, 10, 20)], "2026-11-05": due_sum[pay2], "extra_11_05": 15_000},
    "planted": [
        "로열티를 부가세 포함 매출 + 고객 배달팁으로 계산 (계약: 공급가액의 3%, 배달팁 제외)",
        f"같은 발주번호 {dup[2]}가 두 번 청구됨",
        "동의 항목에 없는 '판촉분담금' 132,000원",
        "기프티콘 수수료를 점주가 100% 냄 (계약: 반반)",
        "11/5 본사 출금이 청구보다 15,000원 많음",
    ],
}

# ------------------------------------------------------------------ 엑셀 쓰기
def write(name, title_rows, header, rows, widths):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    for t in title_rows:
        ws.append(t)
    ws.append(header)
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append(r)
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    wb.save(OUT / name)


write("A앱_정산내역_2026-10_예시.xlsx",
      [["A앱 정산내역 (예시 양식 · 지어낸 데이터)"], ["조회기간: 2026-10-01 ~ 2026-10-31 (주문일 기준)"], []],
      ["주문일시", "주문번호", "주문유형", "매출금액", "중개이용료", "결제정산수수료", "배달비", "고객할인비용",
       "광고비", "부가세", "조정금액", "정산금액", "입금예정일", "정산상태", "비고"],
      [[r["t"].strftime("%Y-%m-%d %H:%M"), r["no"], r["kind"], r["sale"], -r["broker"], -r["pay"], -r["deliv"],
        -r["disc"], -r["ad"], -r["vat"], r["adj"], r["net"], r["due"].isoformat(), r["state"], r["note"]]
       for r in a_rows],
      [17, 14, 8, 10, 10, 13, 8, 11, 8, 8, 9, 10, 11, 9, 18])

write("B앱_정산내역_2026-10_예시.xlsx",
      [["B앱 매출·정산 내역 (예시 양식 · 지어낸 데이터)"], ["주문기간 2026.09.28 ~ 2026.11.01 / 주 단위 지급"], []],
      ["주문일", "주문번호", "결제금액", "중개이용료", "결제대행수수료", "업주부담 배달비", "할인쿠폰(사장님부담)",
       "부가세", "지급금액", "지급일", "비고"],
      [[r["d"].strftime("%Y.%m.%d"), r["no"], r["sale"], r["broker"], r["pay"], r["deliv"], r["coupon"], r["vat"],
        r["net"], r["pay_day"].strftime("%Y.%m.%d"), r["note"]] for r in b_rows],
      [11, 11, 9, 10, 13, 13, 18, 8, 10, 11, 20])

bal = 4_350_000
bank = []
for t, memo, who, out, inn, br in lines:
    bal += inn - out
    bank.append([t.strftime("%Y.%m.%d %H:%M:%S"), memo, who, out, inn, bal, br])
write("통장_거래내역_2026-10_예시.xlsx",
      [["거래내역조회 (예시 은행 · 지어낸 데이터)"], ["계좌번호: 000-000000-00-000 / 조회기간: 2026.10.01 ~ 2026.11.05"], []],
      ["거래일시", "적요", "기재내용", "출금액", "입금액", "잔액", "거래점"], bank, [20, 10, 16, 11, 11, 12, 9])

answer["stats"] = {
    "a_orders": sum(1 for r in a_rows if r["kind"] != "광고"), "a_ad_rows": sum(1 for r in a_rows if r["kind"] == "광고"),
    "a_sale": sum(r["sale"] for r in a_rows), "a_net": sum(r["net"] for r in a_rows),
    "b_orders": sum(1 for r in b_rows if r["no"]), "b_sale": sum(r["sale"] for r in b_rows),
    "b_net": sum(r["net"] for r in b_rows), "bank_lines": len(bank), "refund": refund,
}
(OUT / "answer.json").write_text(json.dumps(answer, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(answer, ensure_ascii=False, indent=1))
