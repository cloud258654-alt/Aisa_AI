var AiTerminal = (function () {
  var terminal = null;
  var decisionOutputs = null;
  var activeScenarioKey = null;

  function initAITerminal() {
    terminal = document.getElementById('terminal-body');
    decisionOutputs = document.getElementById('decision-outputs');

    bindPresetTriggers();
    bindTabSwitching();
    bindPublishCopyActions();
  }

  function printTerminalLog(tag, msg, className) {
    if (!terminal) { terminal = document.getElementById('terminal-body'); }
    if (!terminal) { return; }
    if (!className) { className = 'system-msg'; }

    var ts = _utils.formatTimestamp();
    var row = document.createElement('div');
    row.className = 'terminal-row ' + className;
    row.innerHTML = '<span class="timestamp">' + ts + '</span> ' + tag + ' ' + msg;
    terminal.appendChild(row);
    terminal.scrollTop = terminal.scrollHeight;
  }

  function executeCrisisScenario(key) {
    var data = MockData.presetCrises[key];
    if (!data) { return; }

    activeScenarioKey = key;

    var buttons = document.querySelectorAll('.btn-primary-preset');
    for (var i = 0; i < buttons.length; i++) { buttons[i].classList.remove('active'); }
    var activeBtn = document.getElementById('trigger-crisis-' + key);
    if (activeBtn) { activeBtn.classList.add('active'); }

    if (terminal) {
      terminal.innerHTML = '';
    }
    printTerminalLog('[USER]', data.command, 'user-cmd');

    var delay = 0;
    data.logs.forEach(function (log, index) {
      delay += 600;
      setTimeout(function () {
        printTerminalLog(log.tag, log.msg, log.cls);

        if (index === data.logs.length - 1) {
          populateOutputs(data.outputs);
          showOutputs();
          switchTab('tab-root-cause');
          MetricsComponent.updateDashboardMetrics(
            data.metrics[0], data.metrics[1], data.metrics[2], data.metrics[3], data.metrics[4]
          );
          bindDynamicActions();
        }
      }, delay);
    });
  }

  function populateOutputs(outputs) {
    var rootCause = document.getElementById('tab-root-cause');
    var sop = document.getElementById('tab-sop');
    var pr = document.getElementById('tab-pr');
    var legal = document.getElementById('tab-legal');

    if (rootCause) { rootCause.innerHTML = outputs.rootCause; }
    if (sop) { sop.innerHTML = outputs.sop; }
    if (pr) { pr.innerHTML = outputs.pr; }
    if (legal) { legal.innerHTML = outputs.legal; }
  }

  function showOutputs() {
    if (decisionOutputs) { decisionOutputs.style.display = 'block'; }
  }

  function hideOutputs() {
    if (decisionOutputs) { decisionOutputs.style.display = 'none'; }
  }

  function switchTab(tabId) {
    var tabBtns = document.querySelectorAll('.tab-btn');
    for (var i = 0; i < tabBtns.length; i++) {
      tabBtns[i].classList.remove('active');
      if (tabBtns[i].getAttribute('data-tab') === tabId) {
        tabBtns[i].classList.add('active');
      }
    }

    var tabContents = document.querySelectorAll('.tab-content');
    for (var j = 0; j < tabContents.length; j++) {
      tabContents[j].classList.remove('active');
      if (tabContents[j].id === tabId) {
        tabContents[j].classList.add('active');
      }
    }
  }

  function bindPresetTriggers() {
    function bind(id, key) {
      var el = document.getElementById(id);
      if (el) {
        el.addEventListener('click', function () { executeCrisisScenario(key); });
      }
    }
    bind('trigger-crisis-threads', 'threads');
    bind('trigger-crisis-google', 'google');
    bind('trigger-crisis-ptt', 'ptt');
  }

  function bindTabSwitching() {
    var tabBtns = document.querySelectorAll('.tab-btn');
    for (var i = 0; i < tabBtns.length; i++) {
      tabBtns[i].addEventListener('click', function (e) {
        var tabId = e.target.getAttribute('data-tab');
        if (tabId) { switchTab(tabId); }
      });
    }
  }

  function bindPublishCopyActions() {
    document.addEventListener('click', function (e) {
      if (e.target.classList.contains('btn-copy-pr')) {
        handleCopyPR(e.target);
        return;
      }
      if (e.target.classList.contains('btn-publish-pr')) {
        handlePublishPR(e.target);
        return;
      }
      if (e.target.type === 'checkbox' && e.target.closest('.sop-checklist')) {
        handleSopCheckbox();
        return;
      }
    });
  }

  function bindDynamicActions() {
    setTimeout(function () {
      bindPublishCopyActions();
    }, 100);
  }

  function handleCopyPR(btn) {
    var targetId = btn.getAttribute('data-target');
    var textEl = document.getElementById(targetId);
    if (textEl) {
      var text = textEl.textContent.trim();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          btn.textContent = '已複製！';
          setTimeout(function () { btn.textContent = '複製聲明'; }, 2000);
        }).catch(function () {
          fallbackCopy(text, btn);
        });
      } else {
        fallbackCopy(text, btn);
      }
      printTerminalLog('[SYSTEM]', '公關聲明內容已成功複製至剪貼簿。', 'success-msg');
    }
  }

  function fallbackCopy(text, btn) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(textarea);
    btn.textContent = '已複製！';
    setTimeout(function () { btn.textContent = '複製聲明'; }, 2000);
  }

  function handlePublishPR(btn) {
    var channelType = btn.getAttribute('data-type');
    btn.disabled = true;
    btn.textContent = '張貼中...';

    setTimeout(function () {
      btn.textContent = '發布成功 ✓';
      printTerminalLog('[AI AGENT]', '公關應變聲明已成功串接發布至 ' + channelType + '。事件追蹤中。', 'success-msg');

      var s = DashboardStore.getState();
      var newRes = Math.min(100, s.resolutionRate + 4.0);
      var newRisk = Math.max(10, s.riskScore - 15);
      MetricsComponent.updateDashboardMetrics(s.brandScore, s.storeHealth, s.csat, newRes, newRisk);
    }, 1200);
  }

  function handleSopCheckbox() {
    var checkboxes = document.querySelectorAll('.sop-checklist input[type="checkbox"]');
    var total = checkboxes.length;
    var checked = document.querySelectorAll('.sop-checklist input[type="checkbox"]:checked').length;

    printTerminalLog('[SYSTEM]', 'SOP 執行進度更新：' + checked + '/' + total + '。', 'system-msg');

    if (checked === total) {
      printTerminalLog('[AI AGENT]', '所有建議改善 SOP 已全數被執行與確認。品牌健康度開始回升。', 'success-msg');
      var s = DashboardStore.getState();
      var newBrand = Math.min(100, s.brandScore + 3.0);
      var newRisk = Math.max(5, s.riskScore - 20);
      MetricsComponent.updateDashboardMetrics(newBrand, s.storeHealth, s.csat, 100.0, newRisk);
    }
  }

  function updateRiskBar(risk) {
    var riskBar = document.getElementById('risk-bar');
    if (riskBar) { riskBar.style.width = risk + '%'; }
  }

  return {
    initAITerminal: initAITerminal,
    executeCrisisScenario: executeCrisisScenario,
    printTerminalLog: printTerminalLog,
    switchTab: switchTab,
    showOutputs: showOutputs,
    hideOutputs: hideOutputs,
    updateRiskBar: updateRiskBar
  };
})();
