var MetricsComponent = (function () {
  function initMetrics() {
    updateDashboardMetrics(92.4, 98.1, 4.82, 94.5, 12);
  }

  function updateDashboardMetrics(brand, store, csat, res, risk) {
    var state = DashboardStore.getState();
    DashboardStore.updateMetrics(brand, store, csat, res, risk);

    var brandEl = document.getElementById('val-brand-score');
    var storeEl = document.getElementById('val-store-health');
    var csatEl = document.getElementById('val-csat');
    var resEl = document.getElementById('val-resolution');
    var riskEl = document.getElementById('val-risk');
    var riskBar = document.getElementById('risk-bar');

    if (brandEl) { brandEl.textContent = brand.toFixed(1); }
    if (storeEl) { storeEl.textContent = store.toFixed(1) + '%'; }
    if (csatEl) { csatEl.innerHTML = csat.toFixed(2) + ' <span class="max-val">/ 5</span>'; }
    if (resEl) { resEl.textContent = res.toFixed(1) + '%'; }

    if (riskBar) { riskBar.style.width = risk + '%'; }

    if (riskEl) {
      if (risk < 30) {
        riskEl.textContent = 'Low (' + risk + ')';
        riskEl.className = 'metric-value text-green';
      } else if (risk < 70) {
        riskEl.textContent = 'Medium (' + risk + ')';
        riskEl.className = 'metric-value text-amber';
      } else {
        riskEl.textContent = 'CRITICAL (' + risk + ')';
        riskEl.className = 'metric-value text-rose';
      }
    }

    var circleBrand = document.getElementById('circle-brand-score');
    var circleStore = document.getElementById('circle-store-health');
    var circleCsat = document.getElementById('circle-csat');
    var circleRes = document.getElementById('circle-resolution');

    if (circleBrand) { circleBrand.setAttribute('stroke-dasharray', brand + ', 100'); }
    if (circleStore) { circleStore.setAttribute('stroke-dasharray', store + ', 100'); }
    if (circleCsat) { circleCsat.setAttribute('stroke-dasharray', ((csat / 5) * 100) + ', 100'); }
    if (circleRes) { circleRes.setAttribute('stroke-dasharray', res + ', 100'); }

    updateStarsRating(csat);

    if (typeof AiTerminal !== 'undefined' && AiTerminal.updateRiskBar) {
      AiTerminal.updateRiskBar(risk);
    }
  }

  function updateStarsRating(csat) {
    var starsEl = document.querySelector('#card-csat .metric-stars');
    if (!starsEl) { return; }
    var fullStars = Math.floor(csat);
    var stars = '';
    for (var i = 0; i < 5; i++) {
      stars += (i < fullStars) ? '★' : '☆';
    }
    starsEl.textContent = stars;
  }

  function getMetrics() {
    return DashboardStore.getState();
  }

  function renderMetricCard(id, label, value, delta, deltaText, colorClass) {
    return '';
  }

  return {
    initMetrics: initMetrics,
    updateDashboardMetrics: updateDashboardMetrics,
    getMetrics: getMetrics
  };
})();
