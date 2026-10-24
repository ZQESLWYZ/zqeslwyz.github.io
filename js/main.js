/* ==========================================================================
   Yizhao Wang — personal academic site
   Vanilla JS, no dependencies. Handles: theme toggle, mobile nav,
   active-section highlighting, and the footer year.
   ========================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var themeBtn = document.getElementById('theme-toggle');
  var navToggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('site-nav');

  /* ------------------------------------------------------------- theme */
  function currentTheme() {
    return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
    });
  }

  /* Follow the OS only while the visitor has not picked a theme manually. */
  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var onSystemChange = function (event) {
      var saved = null;
      try { saved = localStorage.getItem('theme'); } catch (e) { /* ignore */ }
      if (saved) return;
      root.setAttribute('data-theme', event.matches ? 'dark' : 'light');
    };
    if (mq.addEventListener) mq.addEventListener('change', onSystemChange);
    else if (mq.addListener) mq.addListener(onSystemChange);
  }

  /* ---------------------------------------------------------- mobile nav */
  function closeNav() {
    if (!nav || !navToggle) return;
    nav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  }

  if (navToggle && nav) {
    navToggle.addEventListener('click', function (event) {
      event.stopPropagation();
      var open = nav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeNav();
    });

    document.addEventListener('click', function (event) {
      if (nav.classList.contains('open') && !nav.contains(event.target)) closeNav();
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeNav();
    });
  }

  /* ----------------------------------------- active section in the header */
  var navLinks = nav ? Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]')) : [];
  var sections = navLinks
    .map(function (link) { return document.querySelector(link.getAttribute('href')); })
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    var visibility = new Map();

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visibility.set(entry.target.id, entry.isIntersecting ? entry.intersectionRatio : 0);
      });

      var bestId = null;
      var bestRatio = 0;
      visibility.forEach(function (ratio, id) {
        if (ratio > bestRatio) { bestRatio = ratio; bestId = id; }
      });

      navLinks.forEach(function (link) {
        link.classList.toggle('active', bestId !== null && link.getAttribute('href') === '#' + bestId);
      });
    }, { rootMargin: '-72px 0px -55% 0px', threshold: [0, 0.15, 0.35, 0.6, 1] });

    sections.forEach(function (section) { observer.observe(section); });
  }

  /* -------------------------------------------------------- footer year */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
