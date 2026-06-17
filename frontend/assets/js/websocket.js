
import { CONFIG_WS_URL } from "./config.js";
import { CONFIG_VAR_RETRY } from "./config.js";

var WS_URL   = CONFIG_WS_URL;
var RETRY_MS = CONFIG_VAR_RETRY; // If server lost its connections with frontend, the socket waits 2s and tries to re-connect again
 
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
    const msg = JSON.parse(e.data);
    handleRecordingMessage(msg);
    updateUI(msg);
  };
}
