var PredictionPanelComponent = (function () {
  var predictionData = null;

  function initPredictionPanel() {
    var container = document.getElementById('prediction-section');
    if (!container) { return; }

    loadPredictions();
    bindSimulation();
  }

  function loadPredictions() {
    if (typeof ApiService !== 'undefined') {
      ApiService.executive.getMorningBrief().then(function (data) {
        predictionData = data.predictions_7day || data.predictions || [];
        renderPredictions(predictionData);
        DashboardStore.setState({ predictions: predictionData });
      }).catch(function () {
        loadMockPredictions();
      });
    } else {
      loadMockPredictions();
    }
  }

  function loadMockPredictions() {
    setTimeout(function () {
      predictionData = [
        { date: 'Day 1', brand_health: 93.1, risk_score: 14.2, negative_volume: 28, confidence: 0.91 },
        { date: 'Day 2', brand_health: 93.5, risk_score: 13.8, negative_volume: 25, confidence: 0.87 },
        { date: 'Day 3', brand_health: 94.0, risk_score: 12.5, negative_volume: 22, confidence: 0.82 },
        { date: 'Day 4', brand_health: 93.8, risk_score: 13.0, negative_volume: 24, confidence: 0.77 },
        { date: 'Day 5', brand_health: 94.2, risk_score: 11.8, negative_volume: 20, confidence: 0.72 },
        { date: 'Day 6', brand_health: 94.5, risk_score: 10.5, negative_volume: 18, confidence: 0.67 },
        { date: 'Day 7', brand_health: 94.8, risk_score: 9.8, negative_volume: 15, confidence: 0.62 }
      ];
      renderPredictions(predictionData);
      DashboardStore.setState({ predictions: predictionData });
    }, 300);
  }

  function renderPredictions(data) {
    if (!data || data.length === 0) { return; }

    var chartEl = document.getElementById('prediction-chart');
    var riskEl = document.getElementById('prediction-risk-chart');
    var negVolEl = document.getElementById('prediction-negvol-chart');
    var confEl = document.getElementById('prediction-confidence');

    if (chartEl) { renderHealthChart(chartEl, data); }
    if (riskEl) { renderRiskChart(riskEl, data); }
    if (negVolEl) { renderNegVolChart(negVolEl, data); }
    if (confEl) { renderConfidence(confEl, data); }
  }

  function renderHealthChart(container, data) {
    var max = 100;
    var min = 85;
    var range = max - min;
    var html = '<div class="fc-chart-header"><span>Brand Health Trend</span><span class="fc-trend-tag positive">Projected +1.7</span></div><div class="fc-bar-chart">';

    data.forEach(function (p, i) {
      var h = Math.round(((p.brand_health - min) / range) * 100);
      var health = typeof p.brand_health === 'number' ? p.brand_health : p.health;
      var day = p.date || p.day || ('Day ' + (i + 1));
      var colorClass = health >= 90 ? 'fc-bar-green' : health >= 80 ? 'fc-bar-amber' : 'fc-bar-red';
      html += '<div class="fc-bar-item">' +
        '<div class="fc-bar ' + colorClass + '" style="height:' + h + '%"><span class="fc-bar-val">' + health.toFixed(1) + '</span></div>' +
        '<span class="fc-bar-label">' + day + '</span>' +
      '</div>';
    });

    html += '</div>';
    container.innerHTML = html;
  }

  function renderRiskChart(container, data) {
    var max = 20;
    var html = '<div class="fc-chart-header"><span>Risk Score Trend</span><span class="fc-trend-tag positive">Declining</span></div><div class="fc-bar-chart">';

    data.forEach(function (p, i) {
      var h = Math.round((p.risk_score / max) * 100);
      var day = p.date || p.day || ('Day ' + (i + 1));
      var colorClass = p.risk_score > 12 ? 'fc-bar-red' : p.risk_score > 8 ? 'fc-bar-amber' : 'fc-bar-green';
      html += '<div class="fc-bar-item">' +
        '<div class="fc-bar ' + colorClass + '" style="height:' + h + '%"><span class="fc-bar-val">' + p.risk_score.toFixed(1) + '</span></div>' +
        '<span class="fc-bar-label">' + day + '</span>' +
      '</div>';
    });

    html += '</div>';
    container.innerHTML = html;
  }

  function renderNegVolChart(container, data) {
    var max = 35;
    var html = '<div class="fc-chart-header"><span>Negative Sentiment Volume</span><span class="fc-trend-tag positive">Shrinking</span></div><div class="fc-bar-chart">';

    data.forEach(function (p, i) {
      var vol = p.negative_volume;
      var h = Math.round((vol / max) * 100);
      var day = p.date || p.day || ('Day ' + (i + 1));
      html += '<div class="fc-bar-item">' +
        '<div class="fc-bar fc-bar-red" style="height:' + h + '%"><span class="fc-bar-val">' + vol + '</span></div>' +
        '<span class="fc-bar-label">' + day + '</span>' +
      '</div>';
    });

    html += '</div>';
    container.innerHTML = html;
  }

  function renderConfidence(container, data) {
    var html = '<div class="fc-confidence-list">';
    var labels = ['Very High', 'High', 'Good', 'Moderate', 'Moderate', 'Fair', 'Fair'];

    data.forEach(function (p, i) {
      var confPct = Math.round((p.confidence || 0.5) * 100);
      var day = p.date || p.day || ('Day ' + (i + 1));
      html += '<div class="fc-conf-item">' +
        '<span class="fc-conf-day">' + day + '</span>' +
        '<div class="fc-conf-bar-wrap"><div class="fc-conf-bar" style="width:' + confPct + '%"></div></div>' +
        '<span class="fc-conf-val">' + confPct + '%</span>' +
        '<span class="fc-conf-label">' + (labels[i] || 'N/A') + '</span>' +
      '</div>';
    });

    html += '</div>';
    container.innerHTML = html;
  }

  function bindSimulation() {
    var btn = document.getElementById('btn-run-simulation');
    var input = document.getElementById('simulation-input');
    if (!btn || !input) { return; }

    btn.addEventListener('click', function () {
      var scenario = input.value.trim();
      if (!scenario) {
        scenario = '增加 10% 尖峰時段人力配置';
        input.value = scenario;
      }

      var simResult = document.getElementById('simulation-result');
      if (simResult) {
        simResult.innerHTML =
          '<div class="sim-card">' +
          '  <div class="sim-card-header">' +
          '    <span class="sim-scenario">Simulation: "' + scenario + '"</span>' +
          '    <span class="badge premium-badge">AI PREDICTION</span>' +
          '  </div>' +
          '  <div class="sim-results-grid">' +
          '    <div class="sim-result-box"><span class="sim-label">Brand Health Impact</span><span class="sim-val positive">+3.2 points</span></div>' +
          '    <div class="sim-result-box"><span class="sim-label">Risk Score Change</span><span class="sim-val positive">-5.8 points</span></div>' +
          '    <div class="sim-result-box"><span class="sim-label">NPS Projection</span><span class="sim-val positive">+6.5</span></div>' +
          '    <div class="sim-result-box"><span class="sim-label">Wait Time Reduction</span><span class="sim-val positive">-3.5 min avg</span></div>' +
          '  </div>' +
          '  <div class="sim-narrative">Based on historical correlation patterns, reallocating peak staff would reduce wait time friction at Eastside Plaza and Westside Mall by an estimated 35%, improving their respective NPS by 5-8 points within 14 days. The net effect on overall brand health is projected at +3.2 points over 30 days with 78% confidence.</div>' +
          '</div>';
      }
    });
  }

  return {
    initPredictionPanel: initPredictionPanel,
    loadPredictions: loadPredictions,
    renderPredictions: renderPredictions
  };
})();
