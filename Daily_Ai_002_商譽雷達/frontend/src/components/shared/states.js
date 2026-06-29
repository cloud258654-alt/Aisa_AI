var StateRenderer = (function () {
  function getContainer(containerId) {
    if (typeof containerId === 'string') {
      return document.getElementById(containerId);
    }
    return containerId;
  }

  function showLoading(containerId, message) {
    var container = getContainer(containerId);
    if (!container) { return; }
    var msg = message || I18n.t('common.loading');
    container.innerHTML =
      '<div class="state-loading">' +
      '<div class="state-spinner"></div>' +
      '<span>' + msg + '</span>' +
      '</div>';
  }

  function showEmpty(containerId, message) {
    var container = getContainer(containerId);
    if (!container) { return; }
    var msg = message || I18n.t('common.noData');
    container.innerHTML =
      '<div class="state-empty">' +
      '<svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.3"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>' +
      '<span>' + msg + '</span>' +
      '</div>';
  }

  function showError(containerId, message, retryFn) {
    var container = getContainer(containerId);
    if (!container) { return; }
    var msg = message || I18n.t('common.loadFailed');

    container.innerHTML =
      '<div class="state-error">' +
      '<svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" style="color:var(--accent-rose);"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>' +
      '<span>' + msg + '</span>' +
      (retryFn ? '<button class="retry-btn">' + I18n.t('common.retry') + '</button>' : '') +
      '</div>';

    if (retryFn) {
      var btn = container.querySelector('.retry-btn');
      if (btn) {
        btn.addEventListener('click', function () {
          retryFn();
        });
      }
    }
  }

  function clearState(containerId) {
    var container = getContainer(containerId);
    if (!container) { return; }
    var stateEl = container.querySelector('.state-loading, .state-empty, .state-error');
    if (stateEl) {
      stateEl.remove();
    }
  }

  return {
    showLoading: showLoading,
    showEmpty: showEmpty,
    showError: showError,
    clearState: clearState
  };
})();
