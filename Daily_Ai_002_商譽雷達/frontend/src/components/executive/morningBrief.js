var MorningBriefComponent = (function () {
  var briefData = null;

  function initExecutiveDashboard() {
    var section = document.getElementById('executive-dashboard');
    if (!section) { return; }

    loadMorningBrief();
    bindRefreshButton();
  }

  function loadMorningBrief() {
    DashboardStore.setLoading(true);

    var summaryEl = document.getElementById('brief-summary');
    if (summaryEl && typeof StateRenderer !== 'undefined') {
      StateRenderer.showLoading('brief-summary', I18n.t('executive.loading'));
    }

    if (typeof ApiService !== 'undefined') {
      ApiService.executive.getMorningBrief().then(function (data) {
        briefData = data;
        renderBrief(data);
        DashboardStore.setLoading(false);
      }).catch(function () {
        loadMockBrief();
      });
    } else {
      loadMockBrief();
    }
  }

  function loadMockBrief() {
    setTimeout(function () {
      briefData = {
        date: new Date().toISOString().split('T')[0],
        summary: '今日全品牌輿情穩定，信義旗艦店排隊摩擦指標持續需關注。AI COO 已識別 2 項營運風險關聯，並預測 7 日品牌健康指數將達 93.1。昨日共 287 則新增評論，正面佔比 72%，負面佔比 18%。',
        riskLevel: 'low',
        key_metrics: {
          brand_health_score: 92.4,
          store_health_index: 98.1,
          risk_score: 12,
          total_voices_today: 342
        },
        topStores: [
          { name: '忠孝 SOGO 店', score: 96.8, status: 'healthy', trend: 'up', issues: 0 },
          { name: '台中公益店', score: 95.2, status: 'healthy', trend: 'stable', issues: 0 },
          { name: '板橋大遠百店', score: 93.5, status: 'healthy', trend: 'down', issues: 1 },
          { name: '信義旗艦店', score: 91.0, status: 'warning', trend: 'down', issues: 3 },
          { name: '機場快取店', score: 85.0, status: 'stable', trend: 'up', issues: 0 }
        ],
        biggestProblem: {
          title: 'Eastside Plaza 系統性衰退',
          severity: 'high',
          description: '4 項併發警示：候位時間、服務品質、餐點溫度、人員回應率。自 6/15 店經理職缺以來持續下滑。',
          affectedStores: ['Eastside Plaza'],
          recommendation: '立即指派代理店經理，派遣區域營運總監進行為期 2 週的現場評估。'
        },
        aiCooRecs: [
          { action: '發布社交媒體退貨政策聲明', impact: '48h 內降低負面聲量 40%', confidence: 0.92 },
          { action: '尖峰時段調配 5 名員工至受影響門市', impact: '平均等候時間減少 3 分鐘', confidence: 0.88 },
          { action: '為 Eastside Plaza 加速招募 3 名兼職人員', impact: '30 天內逆轉 NPS 下滑趨勢', confidence: 0.78 }
        ],
        predictions: [
          { day: 'Day 1', health: 93.1, risk: 14.2, negative: 28 },
          { day: 'Day 2', health: 93.5, risk: 13.8, negative: 25 },
          { day: 'Day 3', health: 94.0, risk: 12.5, negative: 22 },
          { day: 'Day 4', health: 93.8, risk: 13.0, negative: 24 },
          { day: 'Day 5', health: 94.2, risk: 11.8, negative: 20 },
          { day: 'Day 6', health: 94.5, risk: 10.5, negative: 18 },
          { day: 'Day 7', health: 94.8, risk: 9.8, negative: 15 }
        ],
        alerts: [
          { type: 'warning', message: 'Eastside Plaza 48h 內負評集中於排隊與服務體驗', count: 18 },
          { type: 'critical', message: '社交媒體退貨政策負面聲量持續上升', count: 34 },
          { type: 'info', message: '其餘 7 間分店無重大客訴', count: 0 }
        ],
        actionItems: ['發布社交媒體退貨政策說明', '檢討 Eastside Plaza 尖峰排隊動線', '追蹤 Eastside Plaza 服務 SOP 改善進度', '確認各分店週末備戰人力']
      };
      renderBrief(briefData);
      DashboardStore.setLoading(false);
    }, 400);
  }

  function renderBrief(data) {
    if (!data) { return; }

    var dateEl = document.getElementById('brief-date');
    var summaryEl = document.getElementById('brief-summary');
    var riskBadgeEl = document.getElementById('brief-risk-badge');
    var rankingTable = document.getElementById('brief-ranking-table');
    var alertsContainer = document.getElementById('brief-alerts');
    var actionsContainer = document.getElementById('brief-actions');
    var greetingEl = document.getElementById('brief-greeting');
    var metricsRowEl = document.getElementById('brief-metrics-row');
    var problemCardEl = document.getElementById('brief-problem-card');
    var cooRecsEl = document.getElementById('brief-coo-recs');
    var sparklineEl = document.getElementById('brief-sparkline');

    var now = new Date();
    var hour = now.getHours();
    var greetingKey = hour < 12 ? 'executive.greetingMorning' : hour < 18 ? 'executive.greetingAfternoon' : 'executive.greetingEvening';
    var greeting = I18n.t(greetingKey);

    if (greetingEl) {
      greetingEl.textContent = greeting + I18n.t('executive.greetingSuffix');
    }

    if (dateEl) { dateEl.textContent = data.date; }
    if (summaryEl) { summaryEl.textContent = data.summary; }
    if (typeof StateRenderer !== 'undefined') { StateRenderer.clearState('brief-summary'); }

    if (riskBadgeEl) {
      var riskLabels = {
        low: I18n.t('executive.riskLow'),
        medium: I18n.t('executive.riskMedium'),
        high: I18n.t('executive.riskHigh'),
        critical: I18n.t('executive.riskCritical')
      };
      var riskLabel = riskLabels[data.riskLevel] || data.riskLevel;
      riskBadgeEl.textContent = riskLabel;
      riskBadgeEl.className = 'brief-risk-badge ' + (data.riskLevel || 'low');
    }

    if (metricsRowEl && data.key_metrics) {
      var m = data.key_metrics;
      metricsRowEl.innerHTML =
        '<div class="eb-metric-item"><span class="eb-metric-label">' + I18n.t('dashboard.brandHealthLabel') + '</span><span class="eb-metric-val positive">' + (m.brand_health_score || '--') + '</span></div>' +
        '<div class="eb-metric-item"><span class="eb-metric-label">' + I18n.t('dashboard.storeHealthLabel') + '</span><span class="eb-metric-val positive">' + (m.store_health_index || '--') + '%</span></div>' +
        '<div class="eb-metric-item"><span class="eb-metric-label">' + I18n.t('dashboard.riskScore') + '</span><span class="eb-metric-val ' + ((m.risk_score || 0) > 50 ? 'danger' : 'positive') + '">' + (m.risk_score || '--') + '</span></div>' +
        '<div class="eb-metric-item"><span class="eb-metric-label">VOC Volume</span><span class="eb-metric-val">' + (m.total_voices_today || '--') + '</span></div>';
    }

    if (problemCardEl && data.biggestProblem) {
      var p = data.biggestProblem;
      problemCardEl.innerHTML =
        '<div class="eb-problem-header">' +
        '  <span class="eb-problem-icon">' + (p.severity === 'critical' ? '\u26A0\uFE0F' : '\u2757') + '</span>' +
        '  <span class="eb-problem-title">' + I18n.t('executive.biggestProblemTitle') + ': ' + p.title + '</span>' +
        '  <span class="eb-severity-tag ' + p.severity + '">' + p.severity.toUpperCase() + '</span>' +
        '</div>' +
        '<p class="eb-problem-desc">' + p.description + '</p>' +
        '<div class="eb-problem-stores">' +
        '  <span class="eb-problem-label">' + I18n.t('executive.affectedStores') + ':</span>' +
        '  ' + p.affectedStores.map(function (s) { return '<span class="eb-store-tag">' + s + '</span>'; }).join('') +
        '</div>' +
        '<div class="eb-problem-rec">' +
        '  <span class="eb-problem-label">' + I18n.t('executive.aiRecommendation') + ':</span> ' + p.recommendation +
        '</div>';
    }

    if (cooRecsEl && data.aiCooRecs) {
      cooRecsEl.innerHTML = '<h4 class="eb-section-title">' + I18n.t('executive.aiCooRecs') + '</h4>' +
        data.aiCooRecs.map(function (r, i) {
        var confPct = Math.round((r.confidence || 0) * 100);
        return '<div class="eb-coo-item">' +
          '<span class="eb-coo-num">' + (i + 1) + '</span>' +
          '<div class="eb-coo-content">' +
          '  <span class="eb-coo-action">' + r.action + '</span>' +
          '  <span class="eb-coo-impact">' + r.impact + '</span>' +
          '  <div class="eb-coo-confidence"><div class="eb-conf-bar" style="width:' + confPct + '%"></div><span>' + confPct + '%</span></div>' +
          '</div>' +
        '</div>';
      }).join('');
    }

    if (rankingTable && data.topStores) {
      rankingTable.innerHTML = data.topStores.map(function (store, i) {
        var trendIcon = store.trend === 'up' ? '\u2191' : store.trend === 'down' ? '\u2193' : '\u2192';
        var trendClass = store.trend === 'up' ? 'trend-up' : store.trend === 'down' ? 'trend-down' : 'trend-stable';
        var barWidth = Math.round(store.score);
        return '<tr>' +
          '<td class="rank-cell">' + (i + 1) + '</td>' +
          '<td>' + store.name + '</td>' +
          '<td><div class="eb-score-bar-wrap"><div class="eb-score-bar" style="width:' + barWidth + '%"></div><span class="eb-score-val">' + store.score.toFixed(1) + '</span></div></td>' +
          '<td><span class="status-dot ' + store.status + '"></span></td>' +
          '<td><span class="' + trendClass + '">' + trendIcon + '</span></td>' +
        '</tr>';
      }).join('');
    }

    if (sparklineEl && data.predictions) {
      var maxHealth = 100;
      var sparkHtml = '<div class="eb-sparkline-container">' +
        '<span class="eb-sparkline-label">' + I18n.t('executive.brandHealthForecast') + '</span>' +
        '<div class="eb-sparkline-bars">';
      data.predictions.forEach(function (p) {
        var h = Math.round((p.health / maxHealth) * 60);
        sparkHtml += '<div class="eb-spark-bar-wrap"><div class="eb-spark-bar" style="height:' + h + 'px"></div><span class="eb-spark-val">' + p.health.toFixed(1) + '</span><span class="eb-spark-day">' + p.day + '</span></div>';
      });
      sparkHtml += '</div></div>';
      sparklineEl.innerHTML = sparkHtml;
    }

    if (alertsContainer && data.alerts) {
      alertsContainer.innerHTML = data.alerts.map(function (a) {
        return '<div class="brief-alert-item ' + a.type + '">' +
          '<span class="alert-type-tag ' + a.type + '">' + (a.type === 'critical' ? '\u26A0\uFE0F' : a.type === 'warning' ? '\u26A0\uFE0F' : '\u2139\uFE0F') + '</span>' +
          '<span>' + a.message + '</span>' +
          (a.count > 0 ? '<span class="alert-count">' + a.count + '</span>' : '') +
        '</div>';
      }).join('');
    }

    if (actionsContainer && data.actionItems) {
      actionsContainer.innerHTML = data.actionItems.map(function (item) {
        return '<li class="action-item">' + item + '</li>';
      }).join('');
    }
  }

  function bindRefreshButton() {
    var btn = document.getElementById('btn-refresh-brief');
    if (btn) {
      btn.addEventListener('click', function () {
        loadMorningBrief();
      });
    }
  }

  return {
    initExecutiveDashboard: initExecutiveDashboard,
    loadMorningBrief: loadMorningBrief,
    renderBrief: renderBrief
  };
})();
