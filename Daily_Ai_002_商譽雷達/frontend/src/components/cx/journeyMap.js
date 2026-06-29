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
          { type: 'warning', title: '候位到店摩擦 (等候時間過長)', store: '信義旗艦店', desc: '最近 48 小時有 18 則負評提及「排隊引導混亂、候位時間超過預期」。AI 偵測流程流失率上升 4.2%。' },
          { type: 'error', title: '服務體驗摩擦 (出餐速度及服務態度)', store: '信義旗艦店', desc: '輿情中提及「出餐送錯、主餐冷掉、員工態度冷淡」之關鍵字密度暴增 320%。品牌健康度主要扣分項。' }
        ]);
      }
      MetricsComponent.updateDashboardMetrics(92.4, 98.1, 4.82, 94.5, 12);
    } else if (val === 'zhongxiao') {
      if (nodeWait) { nodeWait.className = 'journey-node active'; }
      if (nodeService) { nodeService.className = 'journey-node active'; }
      if (scoreWait) { scoreWait.textContent = '97%'; }
      if (scoreService) { scoreService.textContent = '96%'; }
      if (detailsContainer) {
        detailsContainer.innerHTML = '<div class="diagnostic-card" style="background-color: rgba(16, 185, 129, 0.03); border-color: rgba(16, 185, 129, 0.15); grid-column: span 2;"><div class="diag-header"><span class="diag-title" style="color: var(--accent-emerald)">忠孝 SOGO 店營運狀態良好</span><span class="store-tag">忠孝 SOGO 店</span></div><p class="diag-desc">所有顧客旅程節點 (Search ➔ Review) 指標均高於 95% 門檻。本週滿意度維持高點，無顯著客訴事件。</p></div>';
      }
      MetricsComponent.updateDashboardMetrics(96.8, 99.5, 4.91, 98.0, 5);
    } else {
      if (nodeWait) { nodeWait.className = 'journey-node active'; }
      if (nodeService) { nodeService.className = 'journey-node active'; }
      if (scoreWait) { scoreWait.textContent = '95%'; }
      if (scoreService) { scoreService.textContent = '94%'; }
      if (detailsContainer) {
        detailsContainer.innerHTML = '<div class="diagnostic-card" style="background-color: rgba(255,255,255,0.02); border-color: var(--border-color); grid-column: span 2;"><div class="diag-header"><span class="diag-title">門市健康度分析</span><span class="store-tag">分店診斷</span></div><p class="diag-desc">該門市目前數據平穩。點選其他門市或返回「全品牌門市」以查看整體輿情走勢。</p></div>';
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
