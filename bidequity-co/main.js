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
      var data = new FormData(form);
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }

      fetch(form.action, {
        method: 'POST',
        body: data,
        headers: { 'Accept': 'application/json' }
      }).then(function (response) {
        if (response.ok) {
          form.hidden = true;
          success.hidden = false;
          success.setAttribute('tabindex', '-1');
          success.focus();
        } else {
          if (btn) { btn.disabled = false; btn.textContent = 'Send Message'; }
          alert('Something went wrong. Please try again.');
        }
      }).catch(function () {
        if (btn) { btn.disabled = false; btn.textContent = 'Send Message'; }
        alert('Something went wrong. Please try again.');
      });
    });
  }

  handleFormSubmit('qualify-registration', 'form-success');
  handleFormSubmit('contact-form', 'contact-success');
})();
