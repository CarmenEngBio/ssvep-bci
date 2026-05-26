
// ── FLICKER ENGINE ──────────────────────────────────────
const flickerKeys = Array.from(document.querySelectorAll('.key[data-freq]'))
  .filter(el => parseFloat(el.dataset.freq) > 0)
  .map(el => ({
    el,
    period:  1000 / (parseFloat(el.dataset.freq) * 2),
    elapsed: 0,
    state:   false,
  }));

let lastT = null;
function flicker(ts) {
  if (!lastT) lastT = ts;
  const dt = ts - lastT; lastT = ts;
  flickerKeys.forEach(k => {
    k.elapsed += dt;
    if (k.elapsed >= k.period) {
      k.elapsed -= k.period;
      k.state = !k.state;
      k.el.classList.toggle('on',  k.state);
      k.el.classList.toggle('off', !k.state);
    }
  });
  requestAnimationFrame(flicker);
}
requestAnimationFrame(flicker);