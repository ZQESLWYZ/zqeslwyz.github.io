/* ==========================================================================
   Yizhao Wang — academic homepage
   One job only: if assets/photo.jpg is missing, replace the broken <img>
   with a tidy initials placeholder so the page never shows a broken icon.
   No dependencies, no tracking, no build step.
   ========================================================================== */
(function () {
  'use strict';

  var img = document.getElementById('portrait');
  if (!img) return;

  var replaced = false;

  function useFallback() {
    if (replaced) return;
    replaced = true;

    var box = document.createElement('div');
    box.className = 'portrait-fallback';
    box.setAttribute('role', 'img');
    box.setAttribute('aria-label', 'Placeholder for portrait photo');

    var initials = document.createElement('span');
    initials.className = 'initials';
    initials.textContent = 'YW';

    var hint = document.createElement('span');
    hint.className = 'hint';
    hint.textContent = 'add assets/photo.jpg';

    box.appendChild(initials);
    box.appendChild(hint);

    if (img.parentNode) img.parentNode.replaceChild(box, img);
  }

  /* The error may already have fired before this script ran, so check first. */
  if (img.complete && img.naturalWidth === 0) {
    useFallback();
  } else {
    img.addEventListener('error', useFallback);
  }
})();
