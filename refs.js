/*
 * 참고 문서 — 세 화면 위쪽의 콤보 박스. 고르면 그 문서로 이동.
 * 문서는 docs/ 안의 공개용 HTML 사본 (로그인 없이 열림). 원본 Claude 문서에서 가게·브랜드 이름은 일반 표현으로 바꿈.
 */
(function () {
  'use strict';
  var DOCS = [
    { title: '가맹점 돈길 지도', note: '들어오는 돈·나가는 돈을 눌러 보는 지도', url: 'docs/money-map.html' },
    { title: '가맹점 돈의 흐름', note: '항목별 설명 · 안 맞는 이유 · 다음 질문', url: 'docs/money-flow.html' },
    { title: '정산 맞추기 시뮬레이션 기록', note: '현실형 예시 파일로 돌려 본 과정과 결과', url: 'simulation.html' }
  ];
  function open(url) { location.href = url; }
  Array.prototype.forEach.call(document.querySelectorAll('[data-refs]'), function (host) {
    var label = document.createElement('label');
    label.className = 'refs-pick';
    label.appendChild(document.createTextNode('참고 문서 '));
    var sel = document.createElement('select');
    sel.setAttribute('aria-label', '참고 문서 열기');
    sel.innerHTML = '<option value="">골라서 열기…</option>' + DOCS.map(function (d, i) {
      return '<option value="' + i + '" title="' + d.note + '">' + d.title + ' — ' + d.note + '</option>';
    }).join('');
    sel.addEventListener('change', function () {
      var d = DOCS[+sel.value];
      if (d) open(d.url);
      sel.value = '';
    });
    label.appendChild(sel);
    host.appendChild(label);
  });
})();
