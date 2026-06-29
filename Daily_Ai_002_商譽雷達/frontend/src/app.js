// Sentinel AI Enterprise Customer Experience Intelligence Platform (ECXIP)
// MAIN APPLICATION ENTRY POINT
// Initializes all components and manages navigation

(function () {
  var systemTimeInterval = null;

  function updateSystemTime() {
    var timeEl = document.getElementById('system-time');
    if (!timeEl) { return; }
    timeEl.textContent = _utils.formatTime();
  }

  function initSystemTime() {
    updateSystemTime();
    systemTimeInterval = setInterval(updateSystemTime, 1000);
  }

  function initNavigation() {
    var navItems = document.querySelectorAll('.nav-item');
    var sections = {
      'nav-dashboard': null,
      'nav-exec-brief': document.getElementById('executive-brief-section'),
      'nav-store-ranking': document.getElementById('store-ranking-section'),
      'nav-predictions': document.getElementById('prediction-section'),
      'nav-learning': document.getElementById('learning-section'),
      'nav-journey': document.getElementById('journey'),
      'nav-voc': document.querySelector('.column-left'),
      'nav-sandbox': document.getElementById('sandbox')
    };

    for (var i = 0; i < navItems.length; i++) {
      navItems[i].addEventListener('click', function (e) {
        e.preventDefault();
        var targetId = this.id;
        setActiveNav(targetId);

        var target = sections[targetId];
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else if (targetId === 'nav-dashboard') {
          var workspace = document.querySelector('.workspace-scroll-container');
          if (workspace) { workspace.scrollTo({ top: 0, behavior: 'smooth' }); }
        }
      });
    }
  }

  function setActiveNav(activeId) {
    var navItems = document.querySelectorAll('.nav-item');
    for (var i = 0; i < navItems.length; i++) {
      if (navItems[i].id === activeId) {
        navItems[i].classList.add('active');
      } else {
        navItems[i].classList.remove('active');
      }
    }
  }

  function initConnectionStatus() {
    var statusDot = document.querySelector('.pulse-dot');
    var statusText = document.querySelector('.connection-status span:last-child');

    DashboardStore.subscribe(function (state) {
      if (statusDot) {
        statusDot.classList.remove('green', 'yellow', 'red');
        if (state.connectionStatus === 'connected') {
          statusDot.classList.add('green');
        } else if (state.connectionStatus === 'error') {
          statusDot.classList.add('red');
        } else {
          statusDot.classList.add('yellow');
        }
      }
      if (statusText) {
        if (state.connectionStatus === 'connected') {
          statusText.textContent = 'AI Engine Live';
        } else if (state.connectionStatus === 'disconnected') {
          statusText.textContent = 'Reconnecting...';
        } else {
          statusText.textContent = 'Connection Error';
        }
      }
    });
  }

  function setupStoreFilterBinding() {
    DashboardStore.subscribe(function (state, prevState) {
      if (state.selectedStore !== prevState.selectedStore) {
        JourneyMapComponent.handleStoreChange(state.selectedStore);
        var storeFilter = document.getElementById('store-filter');
        if (storeFilter && storeFilter.value !== state.selectedStore) {
          storeFilter.value = state.selectedStore;
        }
      }
    });
  }

  function tryApiConnection() {
    if (typeof ApiService !== 'undefined') {
      ApiService.brand.getCurrent().then(function (data) {
        if (data && data.brandScore) {
          DashboardStore.setConnectionStatus('connected');
          MetricsComponent.updateDashboardMetrics(
            data.brandScore, data.storeHealth, data.csat,
            data.resolutionRate, data.riskScore
          );
        }
      }).catch(function () {});
      ApiService.voc.getSummary().catch(function () {});
      ApiService.executive.getMorningBrief().catch(function () {});
    }
  }

  function initWebSocket() {
    if (typeof WebSocketService !== 'undefined') {
      WebSocketService.connect('dashboard');
      WebSocketService.on('message', function (data) {
        if (data.type === 'voice_update') {
          DashboardStore.addStreamItem(data.payload);
        }
      });
      WebSocketService.on('connected', function () {
        DashboardStore.setConnectionStatus('connected');
      });
      WebSocketService.on('disconnected', function () {
        DashboardStore.setConnectionStatus('disconnected');
      });
      WebSocketService.on('error', function () {
        DashboardStore.setConnectionStatus('error');
      });
    }
  }

  function initAll() {
    initSystemTime();
    initNavigation();
    initConnectionStatus();
    setupStoreFilterBinding();

    MetricsComponent.initMetrics();
    VoiceStreamComponent.initStream();
    VoiceStreamComponent.bindModalEvents();
    JourneyMapComponent.initJourneyMap();
    AiTerminal.initAITerminal();
    NlpSandbox.initSandbox();

    if (typeof MorningBriefComponent !== 'undefined') {
      MorningBriefComponent.initExecutiveDashboard();
    }
    if (typeof StoreRankingComponent !== 'undefined') {
      StoreRankingComponent.initStoreRanking();
    }
    if (typeof PredictionPanelComponent !== 'undefined') {
      PredictionPanelComponent.initPredictionPanel();
    }
    if (typeof LearningPanelComponent !== 'undefined') {
      LearningPanelComponent.initLearningPanel();
    }

    tryApiConnection();
    initWebSocket();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();
