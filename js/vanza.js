(function () {
  'use strict';

  function updateScrollProgress() {
    var bar = document.getElementById('scroll-progress');
    if (!bar) return;
    var st = document.documentElement.scrollTop || document.body.scrollTop;
    var h = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var pct = h > 0 ? (st / h) * 100 : 0;
    bar.style.width = pct + '%';
  }

  window.addEventListener('scroll', updateScrollProgress, { passive: true });
  window.addEventListener('resize', updateScrollProgress);
  updateScrollProgress();

  function initMobileNav() {
    var header = document.getElementById('header');
    var nav = document.getElementById('primary-nav');
    if (!header || !nav) return;

    var toggle = header.querySelector('[data-nav-toggle]');
    if (!toggle) return;

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = document.body.classList.toggle('mobile-nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    document.addEventListener('click', function (e) {
      if (!document.body.classList.contains('mobile-nav-open')) return;
      if (e.target.closest('[data-nav-toggle]')) return;
      if (e.target.closest('#primary-nav a')) {
        document.body.classList.remove('mobile-nav-open');
        toggle.setAttribute('aria-expanded', 'false');
        return;
      }
      if (!e.target.closest('#primary-nav')) {
        document.body.classList.remove('mobile-nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        document.body.classList.remove('mobile-nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileNav);
  } else {
    initMobileNav();
  }
})();
