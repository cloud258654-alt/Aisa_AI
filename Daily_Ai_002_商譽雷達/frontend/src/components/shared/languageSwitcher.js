var LanguageSwitcher = (function() {
  function init() {
    var headerActions = document.querySelector('.header-actions');
    if (!headerActions) { return; }

    var switcher = document.createElement('div');
    switcher.className = 'lang-switcher';
    switcher.innerHTML =
      '<span class="lang-option" data-locale="zh-TW">繁中</span>' +
      '<span class="lang-option" data-locale="en-US">EN</span>';
    headerActions.insertBefore(switcher, headerActions.firstChild);

    switcher.addEventListener('click', function(e) {
      var option = e.target.closest('.lang-option');
      if (!option) { return; }
      var locale = option.getAttribute('data-locale');
      if (locale) {
        I18n.setLocale(locale);
      }
    });

    I18nEvents.on('localeChanged', function() {
      render();
    });

    render();
  }

  function render() {
    var options = document.querySelectorAll('.lang-option');
    var current = I18n.getLocale();
    for (var i = 0; i < options.length; i++) {
      if (options[i].getAttribute('data-locale') === current) {
        options[i].classList.add('active');
      } else {
        options[i].classList.remove('active');
      }
    }
  }

  return { init: init, render: render };
})();
