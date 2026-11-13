// news.html(배달앱 소식 — 그래서 우리 가게는?) 확인: 검산 · 휴대폰 화면 · 주소에 숫자 담기 · 이미지 저장
// 실행: node tests/news.test.js   (Playwright + Chromium 필요)
// 요율이나 문구를 고치면 다시 돌린다. 기대값은 손계산(아래 주석)과 공개 예시에서 온 것.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const page = 'file://' + encodeURI(path.join(__dirname, '..', 'news.html'));
let fails = 0;
function ok(cond, name, extra) { if (cond) console.log('  ok  ' + name); else { fails++; console.log('  FAIL ' + name + (extra !== undefined ? ' → ' + JSON.stringify(extra) : '')); } }

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 1, acceptDownloads: true });
  const p = await ctx.newPage();
  const errors = [];
  p.on('pageerror', e => errors.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  p.on('dialog', d => d.dismiss().catch(() => {}));
  await p.goto(page);
  const txt = id => p.$eval('#' + id, e => e.textContent);
  const chip = (key, label) => p.click('.chips[data-key="' + key + '"] .chip:text-is("' + label + '")');
  const news = fn => p.evaluate(f => window.__news[f](), fn);

  console.log('처음 화면 (예시 숫자)');
  // 배민: 1,500 × (7.8% + 3%) × 1.1 = 178.2 → 178원, × 300건 = 53,400원
  ok((await txt('bm-how')).includes('1건 178원 × 300건 = 53,400원'), '배민 1건 178원 × 300건', await txt('bm-how'));
  ok((await txt('bm-big')).includes('많아야 5만 3천 원쯤'), '구간을 모르면 "많아야 5만 3천 원쯤"', await txt('bm-big'));
  ok((await txt('bm-how')).includes('1년이면 많아야 64만 원쯤'), '1년 어림 64만 원', await txt('bm-how'));
  // 쿠팡: 2,000 × 7.8% × 1.1 = 171.6 → 172원, × 300건 = 51,600원
  ok((await txt('cp-how')).includes('1건 172원 × 300건 = 51,600원'), '쿠팡 1건 172원 × 300건', await txt('cp-how'));
  ok((await txt('cp-big')).includes('많아야 5만 2천 원쯤'), '쿠팡 "많아야 5만 2천 원쯤"', await txt('cp-big'));
  // 주문 1건 수수료: 20,000 × 10.8% × 1.1 = 2,376원
  ok((await txt('mfn-how')).includes('= 2,376원'), '2만 원 주문 수수료 2,376원', await txt('mfn-how'));
  ok(!(await p.evaluate(() => location.search)), '처음엔 주소에 숫자를 붙이지 않음');

  console.log('공개 예시와 맞는지');
  // 보도 예시: 2만 5천 원 주문 · 배달팁 3천 원 할인 → 수수료 2,700 → 2,376원, 324원(부가세 제외) → 부가세 포함 356원
  await chip('bt', '3,000원');
  ok(await news('perBm') === 356, '배달팁 3,000원 → 1건 356원 (기사 324원 + 부가세)', await news('perBm'));
  ok(Math.round(3000 * 0.108) === 324, '부가세 빼면 324원');
  // 공정위 예시: 2만 원 메뉴를 5천 원 할인 → 중개 1,560 − 1,170 = 390원 → 부가세 포함 429원
  await chip('cd', '5,000원');
  ok(await news('perCp') === 429, '쿠팡 할인 5,000원 → 1건 429원 (공정위 예시 390원 + 부가세)', await news('perCp'));
  // 본사 행사: (7.8% + 3%) → 중개 390 + 결제 150 = 540원 → 부가세 포함 594원
  await chip('hq', '본사 행사 할인 (가맹점)');
  ok(await news('perCp') === 594, '본사 행사 할인 → 1건 594원', await news('perCp'));
  ok((await txt('cp-eq')).includes('(중개 7.8% + 결제 3%)'), '본사 행사는 식에 결제 3%가 보임', await txt('cp-eq'));
  // 근거표의 "할인 1만 원당 약 860원 / 1,190원"
  await chip('cd', '직접');
  await p.fill('.chips[data-key="cd"] + .own input', '10000');
  ok(await news('perCp') === 1188, '할인 1만 원 · 본사 행사 → 1,188원', await news('perCp'));
  await chip('hq', '내가 직접 건 할인');
  ok(await news('perCp') === 858, '할인 1만 원 · 직접 건 할인 → 858원', await news('perCp'));

  console.log('수수료 구간을 고르면');
  await chip('bt', '1,500원');
  await chip('br', '2.0%');
  await chip('sl', '3억 이하');
  // 1,500 × (2.0% + 1.4%) × 1.1 = 56.1 → 56원 × 300 = 16,800원
  ok(await news('perBm') === 56, '중개 2.0% · 결제 1.4% → 1건 56원', await news('perBm'));
  ok((await txt('bm-big')).includes('약 1만 7천 원') && !(await txt('bm-big')).includes('많아야'), '구간을 알면 "약 1만 7천 원"', await txt('bm-big'));
  ok((await txt('bm-cav')).includes('중개 2% · 결제 1.4% 기준'), '기준 요율을 밝힘', await txt('bm-cav'));

  console.log('해당 없는 가게');
  await chip('bn', '직접');
  await p.fill('.chips[data-key="bn"] + .own input', '0');
  ok((await txt('bm-big')).includes('달라지는 게 없어요'), '배달팁 할인 주문 0건 → 달라지는 게 없어요', await txt('bm-big'));

  console.log('주소에 숫자 담기');
  const search = await p.evaluate(() => location.search);
  ok(/bn=0/.test(search) && /bt=1500/.test(search) && /cd=10000/.test(search) && /br=c/.test(search) && /sl=s1/.test(search), '바꾼 숫자가 주소에 담김', search);
  const p2 = await ctx.newPage();
  p2.on('pageerror', e => errors.push(String(e)));
  await p2.goto(page + '?bn=600&bt=2000&cn=100&cd=3000&hq=1&op=25000&br=b&sl=s2');
  // 600건 × round(2,000 × (6.8% + 2.0%) × 1.1 = 193.6) = 194 → 116,400원
  ok((await p2.$eval('#bm-how', e => e.textContent)).includes('1건 194원 × 600건 = 116,400원'), '숫자가 담긴 주소로 열면 그 숫자로', await p2.$eval('#bm-how', e => e.textContent));
  ok(await p2.$eval('.chips[data-key="bn"] .chip[aria-pressed="true"]', e => e.textContent) === '600건', '고른 단추가 눌린 모양');
  ok(await p2.$eval('.chips[data-key="hq"] .chip[aria-pressed="true"]', e => e.textContent) === '본사 행사 할인 (가맹점)', '본사 행사도 그대로');
  // 이상한 값은 무시
  const p3 = await ctx.newPage();
  p3.on('pageerror', e => errors.push(String(e)));
  await p3.goto(page + '?bn=abc&bt=-5&br=zz&sl=%3Cscript%3E');
  ok((await p3.$eval('#bm-big', e => e.textContent)).length > 0 && await p3.evaluate(() => window.__news.S.br) === 'x', '주소의 이상한 값은 무시');
  await p3.close();

  console.log('이미지 저장');
  const [dl] = await Promise.all([p2.waitForEvent('download'), p2.click('#save')]);
  const file = path.join(require('os').tmpdir(), 'news-test-' + Date.now() + '.png');
  await dl.saveAs(file);
  ok(dl.suggestedFilename() === '배달앱소식_우리가게.png', '파일 이름', dl.suggestedFilename());
  ok(fs.statSync(file).size > 20000, 'PNG 크기가 충분함', fs.statSync(file).size);
  fs.unlinkSync(file);
  const ink = await p2.evaluate(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 0; i < d.length; i += 4 * 97) if (d[i] < 80 && d[i + 1] < 80 && d[i + 2] < 90) n++; return n; });
  ok(ink > 300, '이미지에 글자가 그려짐', ink);
  await p2.close();

  console.log('휴대폰 화면');
  for (const w of [320, 360, 412]) {
    await p.setViewportSize({ width: w, height: 740 });
    await p.goto(page);
    const r = await p.evaluate(() => ({
      over: document.documentElement.scrollWidth - innerWidth,
      small: [...document.querySelectorAll('.chip, .btn, details.more > summary')].filter(e => e.getBoundingClientRect().height < 43.5).map(e => e.textContent.trim().slice(0, 12)),
      out: [...document.querySelectorAll('main *')].filter(e => { const q = e.getBoundingClientRect(); return q.width > 0 && (q.right > innerWidth + 0.5 || q.left < -0.5); }).map(e => e.tagName + '.' + e.className).slice(0, 5)
    }));
    ok(r.over <= 0, w + 'px: 옆으로 넘치지 않음', r.over);
    ok(!r.small.length, w + 'px: 누르는 곳이 44px 이상', r.small);
    ok(!r.out.length, w + 'px: 화면 밖으로 나간 요소 없음', r.out);
  }
  ok(!errors.length, '오류 없음', errors);

  await b.close();
  console.log(fails ? '\n실패 ' + fails + '개' : '\n모두 통과');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
