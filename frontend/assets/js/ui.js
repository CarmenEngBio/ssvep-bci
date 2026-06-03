
 
var buffer = '';   
 
function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (state === 'connected') {
    el.textContent = '● Cyton connected';
    el.classList.add('ok');
  } else {
    el.textContent = '● No connection — re-attempting...';
    el.classList.remove('ok');
  }
}
 
function updateUI(msg) {
  var label = msg.label;
  var conf  = msg.confidence || 0;
  var qual  = msg.signal_quality;
 
  document.getElementById('output').textContent = label ?? '?';
 
  var pct = Math.round(conf * 100);
  var bc  = document.getElementById('bar-conf');
  bc.style.width      = pct + '%';
  bc.style.background = pct > 60 ? '#4caf50' : pct > 35 ? '#ff9800' : '#f44336';
  document.getElementById('val-conf').textContent = pct + '%';
 
  if (qual !== undefined) {
    var qpct = Math.min(100, Math.round(qual / 5));
    var bq   = document.getElementById('bar-qual');
    bq.style.width      = qpct + '%';
    bq.style.background = qpct > 60 ? '#4caf50' : qpct > 20 ? '#ff9800' : '#f44336';
    document.getElementById('val-qual').textContent = qual.toFixed(1) + ' µV²';
  }
 
  document.querySelectorAll('.key.predicted').forEach(function(k) {
    k.classList.remove('predicted');
  });
  if (label) {
    var el = document.querySelector('.key[data-key="' + label + '"]');
    if (el) el.classList.add('predicted');
  }
 
  var MAX_DIGITS = 50; // 11 maximum digits according to Cheng paper!
  if (label === 'RESET')              buffer = '';
  else if (label && label !== 'ENTER' && buffer.length < MAX_DIGITS) buffer += label;
  document.getElementById('buffer').textContent = buffer || '—';
 
  if (msg.scores) renderScores(msg.scores, label);
}
 
function renderScores(scores, top) {
  var div = document.getElementById('scores');
  div.innerHTML = Object.entries(scores)
    .sort(function(a, b) { return a[0] - b[0]; })
    .map(function(entry) {
      var k = entry[0], v = entry[1];
      return '<div class="score-cell ' + (k === top ? 'top' : '') + '">'
           + '<b>' + k + '</b>' + (v * 100).toFixed(1) + '%'
           + '</div>';
    })
    .join('');
}