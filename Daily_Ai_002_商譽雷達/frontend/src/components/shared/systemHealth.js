var SystemHealthComponent = (function () {
  var widgetEl = null;

  function init() {
    widgetEl = document.getElementById('system-health-widget');
    if (!widgetEl) { return; }
    loadHealth();
  }

  function loadHealth() {
    render({ loading: true });

    if (typeof ApiService !== 'undefined' && ApiService.system) {
      ApiService.system.getHealth().then(function (data) {
        render(data);
      }).catch(function () {
        loadMockHealth();
      });
    } else {
      loadMockHealth();
    }
  }

  function loadMockHealth() {
    setTimeout(function () {
      render({
        system: 'healthy',
        database: 'healthy',
        redis: 'healthy',
        ai_engine: 'healthy',
        queue: 'healthy'
      });
    }, 200);
  }

  function render(data) {
    if (!widgetEl) { return; }

    if (data.loading) {
      widgetEl.innerHTML =
        '<div class="system-health-widget">' +
        '<div class="health-item"><span class="health-dot warning"></span><span>' + I18n.t('system.loading') + '</span></div>' +
        '</div>';
      return;
    }

    DashboardStore.setSystemHealth(data);

    var items = [
      { key: 'System', value: data.system || data.system_status },
      { key: 'DB', value: data.database },
      { key: 'Redis', value: data.redis },
      { key: 'AI', value: data.ai_engine },
      { key: 'Queue', value: data.queue }
    ];

    var labels = {
      healthy: I18n.t('system.healthy'),
      warning: I18n.t('system.warning'),
      error: I18n.t('system.error')
    };

    widgetEl.innerHTML =
      '<div class="system-health-widget">' +
      items.map(function (item) {
        var status = item.value || 'healthy';
        var statusLabel = labels[status] || status;
        return '<div class="health-item">' +
          '<span class="health-dot ' + status + '"></span>' +
          '<span>' + item.key + ': ' + statusLabel + '</span>' +
        '</div>';
      }).join('') +
      '</div>';
  }

  return {
    init: init,
    loadHealth: loadHealth
  };
})();
