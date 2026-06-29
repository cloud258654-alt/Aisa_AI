var DemoBannerComponent = (function () {
  var bannerEl = null;

  function init() {
    bannerEl = document.getElementById('demo-banner');
    if (!bannerEl) { return; }

    var state = DashboardStore.getState();
    if (state.demoMode) {
      showBanner();
    }
  }

  function showBanner() {
    if (!bannerEl) { bannerEl = document.getElementById('demo-banner'); }
    if (!bannerEl) { return; }
    bannerEl.style.display = 'block';
    bannerEl.innerHTML =
      '<span>' + String.fromCodePoint(0x1F7E6) + ' DEMO MODE — \u793A\u7BC4\u6A21\u5F0F\uFF0C\u8CC7\u6599\u70BA\u6A21\u64EC\u5C55\u793A\u7528\u9014</span>';
  }

  function hideBanner() {
    if (!bannerEl) { bannerEl = document.getElementById('demo-banner'); }
    if (bannerEl) { bannerEl.style.display = 'none'; }
  }

  return {
    init: init,
    showBanner: showBanner,
    hideBanner: hideBanner
  };
})();
