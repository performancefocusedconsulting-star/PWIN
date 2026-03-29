/* ══════════════════════════════════════════
   BIDEQUITY — Main JS
   Nav toggle, form handling, accessibility
   ══════════════════════════════════════════ */

(function () {
  'use strict';

  /* ─── MOBILE NAV TOGGLE ─── */
  var toggle = document.querySelector('.nav__toggle');
  var navLinks = document.getElementById('nav-links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      var isOpen = navLinks.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    // Close nav when a link is clicked (mobile)
    navLinks.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        navLinks.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close nav on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) {
        navLinks.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* ─── FORM HANDLING ─── */
  function handleFormSubmit(formId, successId) {
    var form = document.getElementById(formId);
    var success = document.getElementById(successId);

    if (!form || !success) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.hidden = true;
      success.hidden = false;
      success.setAttribute('tabindex', '-1');
      success.focus();
    });
  }

  handleFormSubmit('qualify-registration', 'form-success');
  handleFormSubmit('contact-form', 'contact-success');
})();
