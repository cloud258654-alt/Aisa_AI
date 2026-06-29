var _utils = (function () {
  function formatTime(date) {
    if (!date) { date = new Date(); }
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    var hours = String(date.getHours()).padStart(2, '0');
    var minutes = String(date.getMinutes()).padStart(2, '0');
    var seconds = String(date.getSeconds()).padStart(2, '0');
    return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
  }

  function formatTimestamp(date) {
    if (!date) { date = new Date(); }
    var hours = String(date.getHours()).padStart(2, '0');
    var minutes = String(date.getMinutes()).padStart(2, '0');
    var seconds = String(date.getSeconds()).padStart(2, '0');
    return '[' + hours + ':' + minutes + ':' + seconds + ']';
  }

  function formatNumber(num, decimals) {
    if (decimals === undefined) { decimals = 2; }
    return Number(num).toFixed(decimals);
  }

  function classNames() {
    var result = [];
    for (var i = 0; i < arguments.length; i++) {
      if (arguments[i]) { result.push(arguments[i]); }
    }
    return result.join(' ');
  }

  function debounce(fn, delay) {
    if (delay === undefined) { delay = 300; }
    var timer = null;
    return function () {
      var context = this;
      var args = arguments;
      if (timer) { clearTimeout(timer); }
      timer = setTimeout(function () { fn.apply(context, args); }, delay);
    };
  }

  function $(selector, parent) {
    if (!parent) { parent = document; }
    return parent.querySelector(selector);
  }

  function $$(selector, parent) {
    if (!parent) { parent = document; }
    return parent.querySelectorAll(selector);
  }

  function html(strings) {
    var values = [];
    for (var i = 1; i < arguments.length; i++) { values.push(arguments[i]); }
    var result = '';
    for (var j = 0; j < strings.length; j++) {
      result += strings[j];
      if (j < values.length) { result += values[j]; }
    }
    return result;
  }

  function randomItem(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  function clamp(val, min, max) {
    return Math.min(max, Math.max(min, val));
  }

  return {
    formatTime: formatTime,
    formatTimestamp: formatTimestamp,
    formatNumber: formatNumber,
    classNames: classNames,
    debounce: debounce,
    $: $,
    $$: $$,
    html: html,
    randomItem: randomItem,
    clamp: clamp
  };
})();
