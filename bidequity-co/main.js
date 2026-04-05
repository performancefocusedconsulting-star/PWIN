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

      fetch('/', {
        method: 'POST',
        body: new URLSearchParams(data).toString(),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
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

  // Qualify form — special handling: store registration + redirect to tool
  (function () {
    var form = document.getElementById('qualify-registration');
    var success = document.getElementById('form-success');
    if (!form || !success) return;

    // If already registered, show direct link to tool
    var existing = localStorage.getItem('bidequity_qualify_user');
    if (existing) {
      form.hidden = true;
      success.hidden = false;
      success.innerHTML = '<h3 class="color-teal mb-16">Welcome back.</h3>'
        + '<p class="text-muted mb-16">You\'re already registered.</p>'
        + '<a href="qualify-app.html" class="btn">Launch Qualification Tool</a>';
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.textContent = 'Starting...'; }

      // Store registration in localStorage
      var userData = {
        firstName: data.get('first-name'),
        lastName: data.get('last-name'),
        email: data.get('email'),
        company: data.get('company'),
        role: data.get('role'),
        sector: data.get('sector'),
        contractValue: data.get('contract-value'),
        registeredAt: new Date().toISOString()
      };
      localStorage.setItem('bidequity_qualify_user', JSON.stringify(userData));

      // Submit to Netlify forms for lead capture
      fetch('/', {
        method: 'POST',
        body: new URLSearchParams(data).toString(),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      }).then(function (response) {
        // Redirect to tool regardless of Netlify form success
        // (don't block the user experience on form submission)
        form.hidden = true;
        success.hidden = false;
        setTimeout(function () { window.location.href = 'qualify-app.html'; }, 800);
      }).catch(function () {
        // Still redirect even if Netlify form fails — user data is in localStorage
        form.hidden = true;
        success.hidden = false;
        setTimeout(function () { window.location.href = 'qualify-app.html'; }, 800);
      });
    });
  })();

  handleFormSubmit('contact-form', 'contact-success');
})();
