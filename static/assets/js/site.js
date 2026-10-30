/* 全站共用的小脚本：首屏前应用主题、主题切换按钮、页脚年份 */
(function () {
  var root = document.documentElement;

  // 尽早执行：避免深色模式下的闪白/闪黑
  try {
    var saved = localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark') root.dataset.theme = saved;
  } catch (e) {}

  function init() {
    var year = document.getElementById('year');
    if (year) year.textContent = new Date().getFullYear();

    var btn = document.getElementById('theme-toggle');
    if (!btn) return;

    var media = window.matchMedia('(prefers-color-scheme: dark)');

    function current() {
      return root.dataset.theme || (media.matches ? 'dark' : 'light');
    }

    function render() {
      var dark = current() === 'dark';
      btn.textContent = dark ? '☀' : '◐';
      btn.setAttribute('aria-label', dark ? '切换到浅色模式' : '切换到深色模式');
      btn.title = btn.getAttribute('aria-label');
    }

    btn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) {}
      render();
    });

    if (media.addEventListener) media.addEventListener('change', render);
    else if (media.addListener) media.addListener(render);

    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
