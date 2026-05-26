
// ── WEBSOCKET ───────────────────────────────────────────
let buffer = '';
let socket = null;   // ← variable global accesible por sendTarget

function connect() {
  socket = new WebSocket('ws://localhost:8765');  // ← asigna a 'socket', no 'const ws'

  socket.onopen = () => {
    document.getElementById('status').textContent = '● Cyton conectado';
    document.getElementById('status').classList.add('ok');
    // Enviar tecla inicial al conectar
    sendTarget(document.getElementById('demo-target').value);
  };

  socket.onclose = () => {
    document.getElementById('status').textContent = '● Sin conexión — reintentando...';
    document.getElementById('status').classList.remove('ok');
    socket = null;
    setTimeout(connect, 2000);
  };

  socket.onmessage = e => updateUI(JSON.parse(e.data));
}
