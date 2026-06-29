var JourneyMapComponent = (function () {
  function initJourneyMap() {
    var storeFilter = document.getElementById('store-filter');
    if (!storeFilter) { return; }

    storeFilter.addEventListener('change', function (e) {
      var val = e.target.value;
      DashboardStore.setSelectedStore(val);
      handleStoreChange(val);
    });
  }

  function handleStoreChange(val) {
    var detailsContainer = document.getElementById('journey-details');
    var nodeWait = document.getElementById('node-wait');
    var nodeService = document.getElementById('node-service');
    var scoreWait = document.getElementById('node-score-wait');
    var scoreService = document.getElementById('node-score-service');

    if (val === 'all' || val === 'xinyi') {
      if (nodeWait) { nodeWait.className = 'journey-node warning'; }
      if (nodeService) { nodeService.className = 'journey-node error'; }
      if (scoreWait) { scoreWait.textContent = '84%'; }
      if (scoreService) { scoreService.textContent = '79%'; }
      if (detailsContainer) {
        detailsContainer.innerHTML = renderDiagnosticCards([
          { type: 'warning', title: I18n.t('journey.waitFriction'), store: '信義旗艦店', desc: I18n.t('journey.waitFrictionDesc') },
          { type: 'error', title: I18n.t('journey.serviceFriction'), store: '信義旗艦店', desc: I18n.t('journey.serviceFrictionDesc') }
        ]);
      }
      MetricsComponent.updateDashboardMetrics(92.4, 98.1, 4.82, 94.5, 12);
    } else if (val === 'zhongxiao') {
      if (nodeWait) { nodeWait.className = 'journey-node active'; }
      if (nodeService) { nodeService.className = 'journey-node active'; }
      if (scoreWait) { scoreWait.textContent = '97%'; }
      if (scoreService) { scoreService.textContent = '96%'; }
      if (detailsContainer) {
        detailsContainer.innerHTML = '<div class="diagnostic-card" style="background-color: rgba(16, 185, 129, 0.03); border-color: rgba(16, 185, 129, 0.15); grid-column: span 2;"><div class="diag-header"><span class="diag-title" style="color: var(--accent-emerald)">' + I18n.t('journey.allGood') + '</span><span class="store-tag">' + I18n.t('header.zhongxiao') + '</span></div><p class="diag-desc">' + I18n.t('journey.allGoodDesc') + '</p></div>';
      }
      MetricsComponent.updateDashboardMetrics(96.8, 99.5, 4.91, 98.0, 5);
    } else {
      if (nodeWait) { nodeWait.className = 'journey-node active'; }
      if (nodeService) { nodeService.className = 'journey-node active'; }
      if (scoreWait) { scoreWait.textContent = '95%'; }
      if (scoreService) { scoreService.textContent = '94%'; }
      if (detailsContainer) {
        detailsContainer.innerHTML = '<div class="diagnostic-card" style="background-color: rgba(255,255,255,0.02); border-color: var(--border-color); grid-column: span 2;"><div class="diag-header"><span class="diag-title">' + I18n.t('journey.genericAnalysis') + '</span><span class="store-tag">' + I18n.t('journey.genericTag') + '</span></div><p class="diag-desc">' + I18n.t('journey.genericDesc') + '</p></div>';
      }
      MetricsComponent.updateDashboardMetrics(94.2, 98.7, 4.85, 96.0, 8);
    }
  }

  function updateJourneyNodes(storeData) {
    if (!storeData) { return; }
    var nodes = storeData;
    if (storeData.nodes) { nodes = storeData.nodes; }

    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      var scoreEl = document.getElementById('node-score-' + node.id);
      var nodeEl = document.getElementById('node-' + node.id);
      if (scoreEl) { scoreEl.textContent = node.score + '%'; }
      if (nodeEl) {
        var cls = node.score >= 95 ? 'active' : node.score >= 85 ? 'warning' : 'error';
        nodeEl.className = 'journey-node ' + cls;
      }
    }
  }

  function renderDiagnosticCards(cards) {
    return cards.map(function (card) {
      return '<div class="diagnostic-card ' + card.type + '">' +
        '<div class="diag-header">' +
          '<span class="diag-title">' + card.title + '</span>' +
          '<span class="store-tag">' + card.store + '</span>' +
        '</div>' +
        '<p class="diag-desc">' + card.desc + '</p>' +
      '</div>';
    }).join('');
  }

  function loadApiData() {
    ApiService.cx.getJourneys().then(function (data) {
      if (data && data.nodes) {
        DashboardStore.setJourneyData(data);
        updateJourneyNodes(data);
      }
    }).catch(function () {});
  }

  return {
    initJourneyMap: initJourneyMap,
    handleStoreChange: handleStoreChange,
    updateJourneyNodes: updateJourneyNodes,
    renderDiagnosticCards: renderDiagnosticCards,
    loadApiData: loadApiData
  };
})();
