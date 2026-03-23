/* ═══════════════════════════════════════
   NMITS – main.js
   ═══════════════════════════════════════ */

// ── Modal helper ──────────────────────────────────
function toggleModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle('hidden');
  // close on backdrop click
  el.addEventListener('click', (e) => {
    if (e.target === el) el.classList.add('hidden');
  }, { once: true });
}

// ── Flash auto-dismiss ────────────────────────────
document.querySelectorAll('.flash').forEach(f => {
  setTimeout(() => f.remove(), 5000);
});

// ── Highlight active nav on load ──────────────────
document.querySelectorAll('.nav-item').forEach(item => {
  if (item.getAttribute('href') === window.location.pathname) {
    item.classList.add('active');
  }
});

// ── Keyboard shortcut: Escape closes modals ───────
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay:not(.hidden)').forEach(m => {
      m.classList.add('hidden');
    });
  }
});
