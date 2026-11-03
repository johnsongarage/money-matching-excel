/*
 * 배달 정산 맞추기 — 예시 데이터와 계산 (두 디자인이 같이 씀)
 * 모든 주문·금액·입금일은 지어낸 숫자이고, 수수료율·배달비도 예시일 뿐 실제 앱 요율이 아님.
 */
(function () {
  'use strict';

  // ---------------------------------------------------------------- 예시 설정 (실제 앱 요율 아님)
  var APPS = {
    'A앱': { brokerRate: 0.078, payRate: 0.030, delivery: 3100, settleDays: 3 },
    'B앱': { brokerRate: 0.078, payRate: 0.030, delivery: 3400, settleDays: 4 },
    'C앱': { brokerRate: 0.068, payRate: 0.025, delivery: 2900, settleDays: 3 }
  };
  var VAT = 0.10; // 중개·결제 수수료와 배달비에 붙는 부가세

  var MENU = {
    '아메리카노': 2500, '카페라떼': 3500, '바닐라라떼': 4000, '호지차라떼': 4300,
    '딸기스무디': 4800, '초코쉐이크': 4500, '크로플': 3800, '아이스티': 3000
  };

  // ---------------------------------------------------------------- 가짜 주문 (10/19 월 ~ 10/25 일)
  // [주문일, 배달앱, 메뉴, 할인·쿠폰 가게 부담, 광고비, 이상(선택)]
  var ORDERS = [
    ['2026-10-19', 'A앱', [['아메리카노', 2], ['카페라떼', 1], ['크로플', 1]], 0, 300],
    ['2026-10-19', 'B앱', [['바닐라라떼', 2], ['아메리카노', 1]], 1000, 0],
    ['2026-10-19', 'A앱', [['호지차라떼', 1], ['카페라떼', 1], ['아메리카노', 1]], 0, 300],
    ['2026-10-20', 'C앱', [['딸기스무디', 2], ['크로플', 1]], 0, 0],
    ['2026-10-20', 'A앱', [['아메리카노', 4]], 0, 300, { late: 2 }],
    ['2026-10-20', 'B앱', [['초코쉐이크', 1], ['카페라떼', 2], ['크로플', 1]], 2000, 0],
    ['2026-10-21', 'A앱', [['카페라떼', 2], ['아이스티', 1]], 1000, 300],
    ['2026-10-21', 'A앱', [['아메리카노', 3], ['크로플', 2]], 0, 300],
    ['2026-10-21', 'C앱', [['호지차라떼', 2], ['아메리카노', 1]], 0, 0],
    ['2026-10-22', 'B앱', [['아메리카노', 2], ['바닐라라떼', 1]], 0, 0, { short: 1500, why: '정산서에 "기타 차감 1,500원" — 무슨 돈인지 적혀 있지 않음' }],
    ['2026-10-22', 'A앱', [['딸기스무디', 1], ['초코쉐이크', 1], ['아메리카노', 2]], 0, 300],
    ['2026-10-22', 'A앱', [['카페라떼', 1], ['아메리카노', 1], ['크로플', 1]], 1000, 300],
    ['2026-10-23', 'C앱', [['아이스티', 2], ['아메리카노', 2]], 0, 0],
    ['2026-10-23', 'A앱', [['바닐라라떼', 2], ['호지차라떼', 2], ['크로플', 1]], 2000, 300],
    ['2026-10-23', 'B앱', [['아메리카노', 3], ['카페라떼', 1]], 0, 0, { late: 3 }],
    ['2026-10-23', 'A앱', [['초코쉐이크', 2], ['아메리카노', 1]], 0, 300],
    ['2026-10-24', 'A앱', [['아메리카노', 2], ['카페라떼', 2], ['크로플', 2]], 1000, 300],
    ['2026-10-24', 'B앱', [['딸기스무디', 2], ['아이스티', 1]], 1000, 0],
    ['2026-10-24', 'C앱', [['카페라떼', 3]], 0, 0],
    ['2026-10-24', 'A앱', [['호지차라떼', 1], ['아메리카노', 2]], 0, 300, { short: 800, why: '정산서에 따로 설명 없음' }],
    ['2026-10-25', 'A앱', [['아메리카노', 5], ['크로플', 1]], 2000, 300],
    ['2026-10-25', 'B앱', [['바닐라라떼', 1], ['카페라떼', 1], ['아메리카노', 1]], 0, 0],
    ['2026-10-25', 'A앱', [['딸기스무디', 1], ['아메리카노', 1], ['크로플', 1]], 0, 300, { late: 1 }],
    ['2026-10-25', 'C앱', [['초코쉐이크', 1], ['호지차라떼', 1], ['크로플', 1]], 1000, 0]
  ];

  // ---------------------------------------------------------------- 계산
  var DOW = ['일', '월', '화', '수', '목', '금', '토'];
  function parse(ds) { var p = ds.split('-'); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])); }
  function iso(d) { return d.toISOString().slice(0, 10); }
  function addBizDays(ds, n) {
    var d = parse(ds), k = 0;
    while (k < n) { d.setUTCDate(d.getUTCDate() + 1); var w = d.getUTCDay(); if (w !== 0 && w !== 6) k++; }
    return iso(d);
  }
  function md(ds) { var d = parse(ds); return (d.getUTCMonth() + 1) + '/' + d.getUTCDate() + '(' + DOW[d.getUTCDay()] + ')'; }
  function won(n) { return Math.round(n).toLocaleString('ko-KR'); }
  function man(n) { var v = n / 10000; return (Math.round(v * 10) / 10).toLocaleString('ko-KR') + '만'; }

  var rows = ORDERS.map(function (o, i) {
    var app = APPS[o[1]], x = o[5] || {};
    var sale = o[2].reduce(function (s, it) { return s + MENU[it[0]] * it[1]; }, 0);
    var broker = Math.round(sale * app.brokerRate);
    var pay = Math.round(sale * app.payRate);
    var delivery = app.delivery;
    var vat = Math.round((broker + pay + delivery) * VAT);
    var coupon = o[3], ad = o[4];
    var cut = broker + pay + vat + delivery + coupon + ad;
    var expected = sale - cut;
    var due = addBizDays(o[0], app.settleDays);
    var paidOn = x.late ? addBizDays(due, x.late) : due;
    var paid = expected - (x.short || 0);
    return {
      no: i + 1, date: o[0], app: o[1], items: o[2], sale: sale,
      broker: broker, pay: pay, vat: vat, delivery: delivery, coupon: coupon, ad: ad, cut: cut,
      expected: expected, paid: paid, due: due, paidOn: paidOn,
      short: x.short || 0, why: x.why || '', lateDays: x.late || 0
    };
  });

  function sum(key, list) { return (list || rows).reduce(function (s, r) { return s + r[key]; }, 0); }
  var T = {
    sale: sum('sale'), paid: sum('paid'), expected: sum('expected'),
    broker: sum('broker'), pay: sum('pay'), vat: sum('vat'), delivery: sum('delivery'), coupon: sum('coupon'), ad: sum('ad')
  };
  T.cut = T.sale - T.paid;

  function menuText(items) {
    return items.map(function (it) { return it[0] + (it[1] > 1 ? ' ' + it[1] : ''); }).join(' · ');
  }

  window.DEMO = {
    APPS: APPS, VAT: VAT, MENU: MENU, rows: rows, T: T, TODAY: '2026-11-03',
    DOW: DOW, parse: parse, iso: iso, addBizDays: addBizDays, md: md, won: won, man: man, sum: sum, menuText: menuText
  };
})();
