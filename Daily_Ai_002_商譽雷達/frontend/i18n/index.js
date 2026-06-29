var I18nEvents = (function() {
  var listeners = {};

  function on(event, fn) {
    if (!listeners[event]) { listeners[event] = []; }
    listeners[event].push(fn);
  }

  function off(event, fn) {
    if (!listeners[event]) { return; }
    var idx = listeners[event].indexOf(fn);
    if (idx > -1) { listeners[event].splice(idx, 1); }
  }

  function emit(event, data) {
    if (!listeners[event]) { return; }
    for (var i = 0; i < listeners[event].length; i++) {
      listeners[event][i](data);
    }
  }

  return { on: on, off: off, emit: emit };
})();

var I18n = (function() {
  var currentLocale = 'zh-TW';
  var translations = {};
  var _onLocaleChangedCallbacks = [];

  function init(options) {
    var saved = null;
    try { saved = localStorage.getItem('sentinel-locale'); } catch (e) {}
    currentLocale = saved || (options && options.defaultLocale) || 'zh-TW';
    if (options && options.zhTW) { register('zh-TW', options.zhTW); }
    if (options && options.enUS) { register('en-US', options.enUS); }
    document.documentElement.setAttribute('lang', currentLocale);
  }

  function register(locale, dict) {
    translations[locale] = dict;
  }

  function t(key, params) {
    var dict = translations[currentLocale] || {};
    var result = getValueByDotNotation(dict, key);
    if (result === undefined) {
      var enDict = translations['en-US'] || {};
      result = getValueByDotNotation(enDict, key);
    }
    if (result === undefined) {
      result = key;
    }
    if (typeof result !== 'string') { return key; }
    if (params) {
      result = interpolateParams(result, params);
    }
    return result;
  }

  function getValueByDotNotation(obj, path) {
    if (!obj || !path) { return undefined; }
    var keys = path.split('.');
    var result = obj;
    for (var i = 0; i < keys.length; i++) {
      if (result === undefined || result === null) { return undefined; }
      result = result[keys[i]];
    }
    return result;
  }

  function interpolateParams(str, params) {
    return str.replace(/\{\{(\w+)\}\}/g, function(match, paramName) {
      return params[paramName] !== undefined ? params[paramName] : match;
    });
  }

  function setLocale(locale) {
    if (locale === currentLocale) { return; }
    currentLocale = locale;
    try { localStorage.setItem('sentinel-locale', locale); } catch (e) {}
    document.documentElement.setAttribute('lang', locale);
    I18nEvents.emit('localeChanged', locale);
  }

  function getLocale() {
    return currentLocale;
  }

  return {
    init: init,
    t: t,
    setLocale: setLocale,
    getLocale: getLocale,
    register: register
  };
})();
