const layout    = document.querySelector('.layout');
const openBtn   = document.getElementById('openLogin');
const closeBtn  = document.getElementById('closeLogin');
const form     = document.getElementById('loginForm');
const emailEl  = document.getElementById('email');
const passEl   = document.getElementById('password');
const btn      = document.getElementById('submitBtn');
const togglePw = document.getElementById('togglePw');
const eyeIcon  = document.getElementById('eyeIcon');

// ── Slide panel open / closed ──────────────────────────────
openBtn.addEventListener('click', () => layout.classList.add('open'));
closeBtn.addEventListener('click', () => layout.classList.remove('open'));

const EYE_OPEN = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`;
const EYE_SHUT = `<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>`;

// Password show/hide toggle
togglePw.addEventListener('click', () => {
  const show = passEl.type === 'password';
  passEl.type = show ? 'text' : 'password';
  eyeIcon.innerHTML = show ? EYE_SHUT : EYE_OPEN;
});

const validEmail = v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
const setErr = (id, on) => document.getElementById(id).classList.toggle('err', on);

// Validate on blur, clear on input
emailEl.addEventListener('blur',  () => setErr('f-email', emailEl.value && !validEmail(emailEl.value.trim())));
passEl.addEventListener('blur',   () => setErr('f-pass',  passEl.value && passEl.value.length < 8));
emailEl.addEventListener('input', () => setErr('f-email', false));
passEl.addEventListener('input',  () => setErr('f-pass',  false));

// Form submit
form.addEventListener('submit', async e => {
  e.preventDefault();

  const eOk = emailEl.value && validEmail(emailEl.value.trim());
  const pOk = passEl.value.length >= 8;

  if (!eOk) setErr('f-email', true);
  if (!pOk) setErr('f-pass',  true);
  if (!eOk || !pOk) return;

  // Show loading spinner
  btn.classList.add('loading');
  btn.disabled = true;

  // Simulate async sign-in request
  await new Promise(r => setTimeout(r, 1800));

  // Success state
  btn.classList.remove('loading');
  btn.disabled = false;
  btn.querySelector('.btn-lbl').textContent = 'Signed in ✓';
  btn.style.cssText += 'background:#34c759;box-shadow:0 2px 14px rgba(52,199,89,.35);pointer-events:none';
});