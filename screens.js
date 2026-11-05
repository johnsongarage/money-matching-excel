/*
 * 화면 고르기 — 모든 화면 위쪽의 콤보 박스. [data-screens] 자리에 그려짐.
 */
(function () {
  'use strict';
  var SCREENS = [
    { file: 'index.html', title: '포스 매출 ↔ 통장' },
    { file: 'delivery.html', title: '배달 정산 (카드형)' },
    { file: 'dashboard.html', title: '배달 정산 (대시보드형)' },
    { file: 'upload.html', title: '내 파일로 맞추기' },
    { file: 'hq-check.html', title: '본사 정산 확인' }
  ];
  var here = location.pathname.split('/').pop() || 'index.html';
  Array.prototype.forEach.call(document.querySelectorAll('[data-screens]'), function (host) {
    var label = document.createElement('label');
    label.className = 'design-pick';
    label.appendChild(document.createTextNode('화면 '));
    var sel = document.createElement('select');
    sel.setAttribute('aria-label', '화면 고르기');
    sel.innerHTML = SCREENS.map(function (s) {
      return '<option value="' + s.file + '"' + (s.file === here ? ' selected' : '') + '>' + s.title + '</option>';
    }).join('');
    sel.addEventListener('change', function () { location.href = sel.value; });
    label.appendChild(sel);
    host.appendChild(label);
  });
})();
