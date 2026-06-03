
var WS_URL   = 'ws://localhost:8765';
var RETRY_MS = 2000; //Será este tiempo en valor más óptimo para el WebSocket?  
 
var socket = null;
 
function sendTarget(key) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'set_target', key: key }));
  }
}
 
function connect() {
  socket = new WebSocket(WS_URL);
 
  socket.onopen = function() {
    setConnectionStatus('connected');
    var sel = document.getElementById('demo-target');
    if (sel) sendTarget(sel.value);
  };
 
  socket.onclose = function() {
    setConnectionStatus('disconnected');
    socket = null;
    setTimeout(connect, RETRY_MS);
  };
 
  socket.onmessage = function(e) {
    updateUI(JSON.parse(e.data));
  };
}
