var WebSocketService = (function () {
  var WS_BASE = '/ws/voice-stream';
  var ws = null;
  var channel = null;
  var listeners = {};
  var reconnectTimer = null;
  var reconnectAttempts = 0;
  var maxReconnectAttempts = 10;
  var baseDelay = 1000;
  var isConnected = false;
  var intentionalClose = false;

  function connect(ch) {
    if (ws && ws.readyState === WebSocket.OPEN) { return; }

    channel = ch || 'default';
    intentionalClose = false;
    var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    var host = window.location.host;
    var url = protocol + '//' + host + WS_BASE + '/' + channel;

    try {
      ws = new WebSocket(url);
    } catch (e) {
      console.warn('WebSocket connection failed:', e.message);
      scheduleReconnect();
      return;
    }

    ws.onopen = function () {
      isConnected = true;
      reconnectAttempts = 0;
      emit('connected', { channel: channel, timestamp: new Date().toISOString() });
      if (typeof DashboardStore !== 'undefined') {
        DashboardStore.setConnectionStatus('connected');
      }
    };

    ws.onmessage = function (event) {
      var data;
      try { data = JSON.parse(event.data); } catch (e) { data = { raw: event.data }; }
      emit('message', data);
      if (data.type) { emit(data.type, data); }
    };

    ws.onclose = function (event) {
      isConnected = false;
      emit('disconnected', { code: event.code, reason: event.reason });
      if (typeof DashboardStore !== 'undefined') {
        DashboardStore.setConnectionStatus('disconnected');
      }
      if (!intentionalClose) { scheduleReconnect(); }
    };

    ws.onerror = function () {
      if (typeof DashboardStore !== 'undefined') {
        DashboardStore.setConnectionStatus('error');
      }
    };
  }

  function disconnect() {
    intentionalClose = true;
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    if (ws) { ws.close(); ws = null; }
    isConnected = false;
  }

  function send(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    }
    return false;
  }

  function scheduleReconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
      console.warn('WebSocket max reconnect attempts reached');
      return;
    }
    if (reconnectTimer) { clearTimeout(reconnectTimer); }
    var delay = Math.min(baseDelay * Math.pow(2, reconnectAttempts), 30000);
    reconnectAttempts++;
    reconnectTimer = setTimeout(function () {
      connect(channel);
    }, delay);
  }

  function on(event, fn) {
    if (!listeners[event]) { listeners[event] = []; }
    listeners[event].push(fn);
    return function () {
      var idx = listeners[event].indexOf(fn);
      if (idx > -1) { listeners[event].splice(idx, 1); }
    };
  }

  function emit(event, data) {
    if (listeners[event]) {
      for (var i = 0; i < listeners[event].length; i++) {
        listeners[event][i](data);
      }
    }
  }

  function getStatus() {
    return {
      connected: isConnected,
      channel: channel,
      attempts: reconnectAttempts
    };
  }

  return {
    connect: connect,
    disconnect: disconnect,
    send: send,
    on: on,
    getStatus: getStatus
  };
})();
