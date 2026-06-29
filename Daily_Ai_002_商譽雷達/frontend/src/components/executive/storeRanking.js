var StoreRankingComponent = (function () {
  var currentTab = 'all';
  var allStores = [];

  function initStoreRanking() {
    var container = document.getElementById('store-ranking-section');
    if (!container) { return; }

    loadStoreRankings();
    bindTabs();
    bindStoreClicks();
  }

  function loadStoreRankings() {
    var tbody = document.getElementById('store-ranking-tbody');
    if (tbody) { tbody.innerHTML = ''; }
    if (typeof StateRenderer !== 'undefined') {
      StateRenderer.showLoading('store-ranking-section', I18n.t('storeRanking.loading'));
    }

    if (typeof ApiService !== 'undefined') {
      ApiService.executive.getStoreRanking().then(function (data) {
        if (typeof StateRenderer !== 'undefined') { StateRenderer.clearState('store-ranking-section'); }
        allStores = data.rankings || [];
        renderTable(currentTab);
        DashboardStore.setState({ storeRankings: allStores });
      }).catch(function () {
        if (typeof StateRenderer !== 'undefined') {
          StateRenderer.showError('store-ranking-section', I18n.t('storeRanking.loadFailed'), function () {
            loadStoreRankings();
          });
        }
        loadMockRankings();
      });
    } else {
      loadMockRankings();
    }
  }

  function loadMockRankings() {
    setTimeout(function () {
      allStores = [
        { rank: 1, store_name: 'Downtown Flagship', score: 92.5, status: 'healthy', trend: 'up', critical_issues: 0, alert_count: 0 },
        { rank: 2, store_name: 'Westside Mall', score: 85.0, status: 'healthy', trend: 'stable', critical_issues: 0, alert_count: 1 },
        { rank: 3, store_name: 'Airport Kiosk', score: 78.0, status: 'stable', trend: 'stable', critical_issues: 1, alert_count: 2 },
        { rank: 4, store_name: 'Northgate Center', score: 62.0, status: 'warning', trend: 'stable', critical_issues: 1, alert_count: 1 },
        { rank: 5, store_name: 'Eastside Plaza', score: 55.0, status: 'critical', trend: 'down', critical_issues: 3, alert_count: 4 },
        { rank: 6, store_name: 'Southgate Village', score: 71.0, status: 'stable', trend: 'up', critical_issues: 0, alert_count: 1 },
        { rank: 7, store_name: 'Harbor View', score: 68.0, status: 'warning', trend: 'down', critical_issues: 2, alert_count: 2 },
        { rank: 8, store_name: 'University Corner', score: 65.0, status: 'stable', trend: 'stable', critical_issues: 0, alert_count: 0 },
        { rank: 9, store_name: 'Metro Station', score: 59.0, status: 'warning', trend: 'down', critical_issues: 2, alert_count: 3 },
        { rank: 10, store_name: 'Riverside Outlet', score: 52.0, status: 'critical', trend: 'down', critical_issues: 4, alert_count: 5 }
      ];
      renderTable(currentTab);
      DashboardStore.setState({ storeRankings: allStores });
    }, 300);
  }

  function getFilteredStores() {
    if (currentTab === 'all') return allStores;
    if (currentTab === 'critical') return allStores.filter(function (s) { return s.status === 'critical' || (s.critical_issues || 0) >= 3; });
    if (currentTab === 'improving') return allStores.filter(function (s) { return s.trend === 'up'; });
    if (currentTab === 'declining') return allStores.filter(function (s) { return s.trend === 'down'; });
    return allStores;
  }

  function renderTable(tab) {
    currentTab = tab;
    var tbody = document.getElementById('store-ranking-tbody');
    if (!tbody) { return; }

    var stores = getFilteredStores();

    if (stores.length === 0) {
      if (typeof StateRenderer !== 'undefined') {
        StateRenderer.showEmpty('store-ranking-tbody', I18n.t('storeRanking.noMatch'));
      } else {
        tbody.innerHTML = '<tr><td colspan="6" class="loading-row">' + I18n.t('storeRanking.noMatch') + '</td></tr>';
      }
      return;
    }
    if (typeof StateRenderer !== 'undefined') { StateRenderer.clearState('store-ranking-tbody'); }

    tbody.innerHTML = stores.map(function (store, i) {
      var rankNum = currentTab === 'all' ? store.rank : (i + 1);
      var trendIcon = store.trend === 'up' ? '\u2191' : store.trend === 'down' ? '\u2193' : '\u2192';
      var trendClass = store.trend === 'up' ? 'trend-up' : store.trend === 'down' ? 'trend-down' : 'trend-stable';
      var scoreColor = store.score >= 80 ? 'sr-bar-green' : store.score >= 60 ? 'sr-bar-amber' : 'sr-bar-red';
      var barWidth = Math.round(store.score);
      var issuesCount = store.critical_issues || 0;

      return '<tr class="sr-row" data-store="' + store.store_name + '">' +
        '<td class="rank-cell">' + rankNum + '</td>' +
        '<td class="sr-store-name">' + store.store_name + '</td>' +
        '<td><div class="sr-score-wrap"><div class="sr-score-bar ' + scoreColor + '" style="width:' + barWidth + '%"></div><span class="sr-score-num">' + store.score.toFixed(1) + '</span></div></td>' +
        '<td><span class="sr-risk-tag ' + (store.status || 'stable') + '">' + (store.status || 'stable').toUpperCase() + '</span></td>' +
        '<td><span class="' + trendClass + '">' + trendIcon + '</span></td>' +
        '<td class="sr-issues-cell"><span class="sr-issues-count ' + (issuesCount > 0 ? 'has-issues' : 'no-issues') + '">' + issuesCount + '</span></td>' +
      '</tr>';
    }).join('');
  }

  function bindTabs() {
    var tabs = document.querySelectorAll('#store-ranking-section .sr-tab-btn');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].addEventListener('click', function () {
        var tabId = this.getAttribute('data-tab');
        setActiveTab(tabId);
        renderTable(tabId);
      });
    }
  }

  function setActiveTab(tabId) {
    var tabs = document.querySelectorAll('#store-ranking-section .sr-tab-btn');
    for (var i = 0; i < tabs.length; i++) {
      if (tabs[i].getAttribute('data-tab') === tabId) {
        tabs[i].classList.add('active');
      } else {
        tabs[i].classList.remove('active');
      }
    }
  }

  function bindStoreClicks() {
    var tbody = document.getElementById('store-ranking-tbody');
    if (!tbody) { return; }

    tbody.addEventListener('click', function (e) {
      var row = e.target.closest('.sr-row');
      if (!row) { return; }
      var storeName = row.getAttribute('data-store');
      if (storeName) {
        showStoreDetail(storeName);
      }
    });
  }

  function showStoreDetail(storeName) {
    var store = allStores.find(function (s) { return s.store_name === storeName; });
    if (!store) { return; }

    var detailEl = document.getElementById('sr-store-detail');
    if (!detailEl) { return; }

    var statusLabel = (store.status || 'stable').toUpperCase();
    detailEl.innerHTML =
      '<div class="sr-detail-header">' +
      '  <h3>' + store.store_name + '</h3>' +
      '  <span class="sr-risk-tag ' + (store.status || 'stable') + '">' + statusLabel + '</span>' +
      '  <button class="btn-icon sr-detail-close" id="sr-detail-close">\u00D7</button>' +
      '</div>' +
      '<div class="sr-detail-grid">' +
      '  <div class="sr-detail-item"><span class="sr-detail-label">' + I18n.t('storeRanking.detailHealthScore') + '</span><span class="sr-detail-val">' + store.score.toFixed(1) + '/100</span></div>' +
      '  <div class="sr-detail-item"><span class="sr-detail-label">' + I18n.t('storeRanking.detailTrend') + '</span><span class="sr-detail-val">' + (store.trend || 'stable') + '</span></div>' +
      '  <div class="sr-detail-item"><span class="sr-detail-label">' + I18n.t('storeRanking.detailCriticalIssues') + '</span><span class="sr-detail-val">' + (store.critical_issues || 0) + '</span></div>' +
      '  <div class="sr-detail-item"><span class="sr-detail-label">' + I18n.t('storeRanking.detailActiveAlerts') + '</span><span class="sr-detail-val">' + (store.alert_count || 0) + '</span></div>' +
      '</div>' +
      '<div class="sr-detail-actions">' +
      '  <button class="btn btn-sm-primary">' + I18n.t('storeRanking.viewFullReport') + '</button>' +
      '  <button class="btn btn-secondary btn-sm">' + I18n.t('storeRanking.assignManager') + '</button>' +
      '</div>';
    detailEl.style.display = 'block';

    var closeBtn = document.getElementById('sr-detail-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        detailEl.style.display = 'none';
      });
    }
  }

  return {
    initStoreRanking: initStoreRanking,
    loadStoreRankings: loadStoreRankings,
    renderTable: renderTable
  };
})();
