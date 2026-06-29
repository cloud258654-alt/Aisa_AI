var VoiceStreamComponent = (function () {
  var streamInterval = null;
  var isStreamRunning = true;
  var streamContainer = null;

  function initStream() {
    streamContainer = document.getElementById('stream-feed-container');
    if (!streamContainer) { return; }

    for (var i = 0; i < 5; i++) {
      var mockItem = _utils.randomItem(MockData.reviewBank);
      createVoiceCard(mockItem, false);
    }

    startStreamInterval();
    bindControls();
  }

  function createVoiceCard(data, isPrepend) {
    if (!streamContainer) { streamContainer = document.getElementById('stream-feed-container'); }
    if (!streamContainer) { return null; }

    var card = document.createElement('div');
    card.className = 'voice-item';

    var riskBadge = data.risk === 'high' ? '<span class="v-badge risk-high">' + I18n.t('voc.highRiskAlert') + '</span>' : '';
    var sentimentClass = data.sentiment;

    var sentimentLabels = {
      negative: I18n.t('voc.sentimentNegative'),
      positive: I18n.t('voc.sentimentPositive'),
      neutral: I18n.t('voc.sentimentNeutral')
    };

    card.innerHTML =
      '<div class="voice-meta">' +
        '<div class="channel-tag ' + data.channel + '">' +
          '<span class="channel-dot ' + data.channel + '"></span>' +
          '<span>' + data.channelName + ' (@' + data.author + ')</span>' +
        '</div>' +
        '<span class="voice-time">' + I18n.t('voc.justNow') + '</span>' +
      '</div>' +
      '<p class="voice-body">' + data.text + '</p>' +
      '<div class="voice-tags">' +
        '<span class="v-badge ' + sentimentClass + '">' + (sentimentLabels[data.sentiment] || data.sentiment.toUpperCase()) + '</span>' +
        '<span class="v-badge topic">' + data.topic + '</span>' +
        '<span class="v-badge store">' + data.store + '</span>' +
        riskBadge +
      '</div>' +
      '<div class="voice-actions">' +
        '<button class="btn-sm btn-sm-primary btn-process-review">' + I18n.t('voc.processReview') + '</button>' +
      '</div>';

    if (isPrepend) {
      streamContainer.prepend(card);
    } else {
      streamContainer.appendChild(card);
    }

    var processBtn = card.querySelector('.btn-process-review');
    if (processBtn) {
      processBtn.addEventListener('click', function () {
        openModal(data.text);
      });
    }

    if (streamContainer.children.length > 20) {
      streamContainer.removeChild(streamContainer.lastChild);
    }

    return card;
  }

  function startStreamInterval() {
    if (streamInterval) { clearInterval(streamInterval); }

    streamInterval = setInterval(function () {
      if (!isStreamRunning) { return; }

      var randomReview = Object.assign({}, _utils.randomItem(MockData.reviewBank));
      randomReview.author = _utils.randomItem(MockData.authorPool);
      createVoiceCard(randomReview, true);

      if (randomReview.sentiment === 'negative') {
        var s = DashboardStore.getState();
        var newBrand = _utils.clamp(s.brandScore - 0.2, 80, 100);
        var newCsat = _utils.clamp(s.csat - 0.01, 4.0, 5.0);
        var newRisk = _utils.clamp(s.riskScore + 2, 0, 100);
        MetricsComponent.updateDashboardMetrics(newBrand, s.storeHealth, newCsat, s.resolutionRate, newRisk);
      } else if (randomReview.sentiment === 'positive') {
        var s2 = DashboardStore.getState();
        var nb = _utils.clamp(s2.brandScore + 0.1, 0, 100);
        var nc = _utils.clamp(s2.csat + 0.005, 0, 5.0);
        var nr = _utils.clamp(s2.riskScore - 1, 0, 100);
        MetricsComponent.updateDashboardMetrics(nb, s2.storeHealth, nc, s2.resolutionRate, nr);
      }
    }, 6000);
  }

  function pauseStream() {
    isStreamRunning = !isStreamRunning;
    DashboardStore.setStreamRunning(isStreamRunning);
    var btnPause = document.getElementById('btn-pause-stream');
    if (!btnPause) { return; }

    if (isStreamRunning) {
      btnPause.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="pause-icon"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>';
      btnPause.classList.remove('paused');
    } else {
      btnPause.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>';
      btnPause.classList.add('paused');
    }
  }

  function clearStream() {
    if (streamContainer) { streamContainer.innerHTML = ''; }
    DashboardStore.clearStream();
    if (typeof StateRenderer !== 'undefined') {
      StateRenderer.showEmpty('stream-feed-container', I18n.t('voc.streamCleared'));
    }
  }

  function bindControls() {
    var btnPause = document.getElementById('btn-pause-stream');
    var btnClear = document.getElementById('btn-clear-stream');

    if (btnPause) {
      btnPause.addEventListener('click', pauseStream);
    }
    if (btnClear) {
      btnClear.addEventListener('click', clearStream);
    }
  }

  function openModal(text) {
    var modal = document.getElementById('action-modal');
    var modalReviewText = document.getElementById('modal-review-text');
    if (!modal || !modalReviewText) { return; }
    modalReviewText.textContent = text;
    modal.style.display = 'flex';
  }

  function closeModal() {
    var modal = document.getElementById('action-modal');
    if (modal) { modal.style.display = 'none'; }
  }

  function bindModalEvents() {
    var modalClose = document.getElementById('modal-close');
    var modal = document.getElementById('action-modal');

    if (modalClose) {
      modalClose.addEventListener('click', closeModal);
    }
    window.addEventListener('click', function (e) {
      if (e.target === modal) { closeModal(); }
    });

    var actions = ['modal-action-sop', 'modal-action-reply', 'modal-action-pr'];
    actions.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.addEventListener('click', function () {
          closeModal();
          var s = DashboardStore.getState();
          var newRes = Math.min(100, s.resolutionRate + 0.5);
          var newRisk = Math.max(5, s.riskScore - 3);
          MetricsComponent.updateDashboardMetrics(s.brandScore, s.storeHealth, s.csat, newRes, newRisk);

          if (typeof AiTerminal !== 'undefined' && AiTerminal.printTerminalLog) {
            AiTerminal.printTerminalLog('[SYSTEM]', I18n.t('ai.dispatchLog') + el.textContent + I18n.t('ai.recalibrated'), 'success-msg');
          }
        });
      }
    });
  }

  return {
    initStream: initStream,
    createVoiceCard: createVoiceCard,
    startStreamInterval: startStreamInterval,
    pauseStream: pauseStream,
    clearStream: clearStream,
    bindModalEvents: bindModalEvents
  };
})();
