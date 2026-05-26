
// ── UI UPDATE ───────────────────────────────────────────
function updateUI(msg) {
  const label = msg.label;
  const conf  = msg.confidence || 0;
  const qual  = msg.signal_quality;

  document.getElementById('output').textContent = label ?? '?';

  const pct = Math.round(conf * 100);
  const bc  = document.getElementById('bar-conf');
  bc.style.width      = pct + '%';
  bc.style.background = pct > 60 ? '#4caf50' : pct > 35 ? '#ff9800' : '#f44336';
  document.getElementById('val-conf').textContent = pct + '%';

  if (qual !== undefined) {
    const qpct = Math.min(100, Math.round(qual / 5));
    const bq   = document.getElementById('bar-qual');
    bq.style.width      = qpct + '%';
    bq.style.background = qpct > 60 ? '#4caf50' : qpct > 20 ? '#ff9800' : '#f44336';
    document.getElementById('val-qual').textContent = qual.toFixed(1) + ' µV²';
  }

  document.querySelectorAll('.key.predicted').forEach(k => k.classList.remove('predicted'));
  if (label) {
    const el = document.querySelector(`.key[data-key="${label}"]`);
    if (el) el.classList.add('predicted');
  }

  if (label === 'RESET')            buffer = '';
  else if (label && label !== 'ENTER') buffer += label;
  document.getElementById('buffer').textContent = buffer || '—';

  if (msg.scores) renderScores(msg.scores, label);
}

function renderScores(scores, top) {
  const div = document.getElementById('scores');
  div.innerHTML = Object.entries(scores)
    .sort((a, b) => a[0] - b[0])
    .map(([k, v]) => `
      <div class="score-cell ${k === top ? 'top' : ''}">
        <b>${k}</b>${(v * 100).toFixed(1)}%
      </div>`)
    .join('');
}

connect();