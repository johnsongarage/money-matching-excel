/*
 * 참고 문서 — 세 화면 위쪽의 콤보 박스. 고르면 새 탭으로 열림.
 * 문서 자체는 Claude 문서(링크)이고, 열람 권한은 문서 쪽 공유 설정을 따름.
 */
(function () {
  'use strict';
  var DOCS = [
    { title: '가맹점 돈길 지도', note: '들어오는 돈·나가는 돈을 눌러 보는 지도', url: 'https://claude.ai/artifact/48XQ5BsLYLubkC6gH2RBCk' },
    { title: '가맹점 돈의 흐름', note: '항목별 설명 · 안 맞는 이유 · 다음 질문', url: 'https://claude.ai/artifact/XLUboP5MBnNA65y6K5sthT' }
  ];
  function open(url) {
    var a = document.createElement('a');
    a.href = url; a.target = '_blank'; a.rel = 'noopener';
    document.body.appendChild(a); a.click(); a.remove();
  }
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
