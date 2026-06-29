var NlpSandbox = (function () {
  var sandboxExamples = [
    '信義店昨天服務極爛！我們等了一個多小時，點的招牌牛肉送上來居然還是冰的，反應了店員還擺臭臉，叫主管來才不情不願道歉，這種店吃一次就夠了！',
    '忠孝SOGO店的服務生Apple態度超好，很有耐心解說菜單，做完的美甲花色很美，非常細緻。一定會再回訪的，大推！',
    '路過台中店覺得裝潢很好看就進去了，等候時間還好大概十分鐘，只是餐點味道很普通，以這個價位來說算貴的，沒有評論上寫得那麼神。'
  ];

  function initSandbox() {
    var btnExample = document.getElementById('btn-sandbox-example');
    var btnAnalyze = document.getElementById('btn-sandbox-analyze');
    var sandboxInput = document.getElementById('sandbox-input');

    if (btnExample) {
      btnExample.addEventListener('click', function () {
        var index = Math.floor(Math.random() * sandboxExamples.length);
        if (sandboxInput) { sandboxInput.value = sandboxExamples[index]; }
      });
    }

    if (btnAnalyze) {
      btnAnalyze.addEventListener('click', function () {
        var text = sandboxInput ? sandboxInput.value.trim() : '';
        if (!text) {
          alert('請輸入一些評論文字再執行分析！');
          return;
        }
        analyzeText(text);
      });
    }
  }

  function analyzeText(text) {
    var sandboxLoading = document.getElementById('sandbox-loading');
    var sandboxResults = document.getElementById('sandbox-results');

    if (sandboxResults) { sandboxResults.style.display = 'none'; }
    if (sandboxLoading) { sandboxLoading.style.display = 'flex'; }

    if (typeof ApiService !== 'undefined') {
      ApiService.sandbox.analyze(text).then(function (data) {
        finishAnalysis(text, data);
      }).catch(function () {
        finishAnalysis(text, null);
      });
    } else {
      setTimeout(function () { finishAnalysis(text, null); }, 1500);
    }
  }

  function finishAnalysis(text, apiResult) {
    var sandboxLoading = document.getElementById('sandbox-loading');
    var sandboxResults = document.getElementById('sandbox-results');

    if (sandboxLoading) { sandboxLoading.style.display = 'none'; }

    var sentiment = 'Positive (92%)';
    var sentimentClass = 'positive';
    var emotion = 'Joy 😊 / Satisfaction 👍';
    var touchpoint = 'Service (服務體驗) & Product (餐點品質)';
    var risk = 'Low Risk (5)';
    var riskClass = 'low';
    var pr = '您好，感謝您對我們服務與品質的肯定！我們會持續維持高品質水準，期待下次再度為您提供愉快的體驗。';
    var ops = [
      '維持當前服務規範，將該店同仁的優秀事蹟記錄入本月考核指標。',
      '持續維持食材供應鏈的穩定品質。'
    ];

    if (apiResult && apiResult.sentiment) {
      sentiment = apiResult.sentiment === 'negative' ? 'Negative (' + apiResult.sentimentScore + '%)' : 'Positive (' + apiResult.sentimentScore + '%)';
      sentimentClass = apiResult.sentiment;
      emotion = apiResult.emotion || emotion;
      touchpoint = apiResult.touchpoint || touchpoint;
      risk = apiResult.riskLevel === 'high' ? 'CRITICAL Risk (' + apiResult.riskScore + ')' : 'Low Risk (' + apiResult.riskScore + ')';
      riskClass = apiResult.riskLevel || 'low';
      pr = apiResult.prDraft || pr;
      ops = apiResult.opsSuggestions || ops;
    } else {
      var lowerText = text.toLowerCase();

      if (lowerText.indexOf('爛') > -1 || lowerText.indexOf('冰') > -1 || lowerText.indexOf('臭臉') > -1 || lowerText.indexOf('生氣') > -1 || lowerText.indexOf('等很久') > -1 || lowerText.indexOf('拉肚子') > -1 || lowerText.indexOf('肚子痛') > -1 || lowerText.indexOf('差') > -1) {
        sentiment = 'Negative (96%)';
        sentimentClass = 'negative';
        emotion = 'Anger 😠 / Frustration 😩';

        if (lowerText.indexOf('等') > -1 || lowerText.indexOf('候') > -1) {
          touchpoint = 'Wait (等候到店) & Service (服務體驗)';
        } else if (lowerText.indexOf('冰') > -1 || lowerText.indexOf('不新鮮') > -1 || lowerText.indexOf('拉肚子') > -1) {
          touchpoint = 'Service (服務體驗) & Product (食品品質)';
        } else {
          touchpoint = 'Service (服務體驗) / Touchpoint friction';
        }

        if (lowerText.indexOf('拉肚子') > -1 || lowerText.indexOf('毒') > -1 || lowerText.indexOf('集體') > -1) {
          risk = 'CRITICAL Risk (85)';
          riskClass = 'high';
          pr = '您好，非常抱歉讓您遭遇此用餐情況。本公司高度重視此食安疑慮，已立刻責成相關分店主管清查冷鏈儲存與廚房作業。我們非常關切您的身體狀況，請您方便撥冗聯絡我們，以便安排就醫複查與全額補償。';
          ops = ['分店立即對冷鏈及食材新鮮度進行自主封存與送驗。', '對當日收發貨及庫存食材清單進行回溯排查。'];
        } else {
          risk = 'High Risk (72)';
          riskClass = 'high';
          pr = '您好，十分抱歉讓您在此次用餐中感到不愉快。針對您提及的餐點溫度及員工態度問題，我們已立即轉達分店店長進行整頓與加強教育訓練，並將嚴格監督出餐覆核。希望您給予我們改進的機會。';
          ops = ['要求分店落實出餐雙重核對，並於現場進行人員應對培訓督導。', '店經理親自向顧客致電說明改善計畫並致歉。'];
        }
      } else if (lowerText.indexOf('普通') > -1 || lowerText.indexOf('還好') > -1 || lowerText.indexOf('一般') > -1 || lowerText.indexOf('貴') > -1) {
        sentiment = 'Neutral (60%)';
        sentimentClass = 'neutral';
        emotion = 'Neutral 😐 / Evaluation 🤔';
        touchpoint = 'Product (餐點品質) & Price (價格認知)';
        risk = 'Low Risk (15)';
        riskClass = 'low';
        pr = '您好，感謝您的回饋。我們會持續聽取各方顧客意見，對產品的性價比與口味進行優化。期待未來能為您提供更為驚艷的服務。';
        ops = ['記錄顧客對於價格與餐點美味度的性價比回饋，彙整給研發總部。', '定期觀察對手品牌同價位產品的競爭力。'];
      }
    }

    renderResults(sentiment, sentimentClass, emotion, touchpoint, risk, riskClass, pr, ops);

    if (riskClass === 'high') {
      var s = DashboardStore.getState();
      var newBrand = Math.max(80, s.brandScore - 1.0);
      var newRisk = Math.min(100, s.riskScore + 8);
      MetricsComponent.updateDashboardMetrics(newBrand, s.storeHealth, s.csat, s.resolutionRate, newRisk);
    }

    DashboardStore.setSandboxResults({ sentiment: sentiment, sentimentClass: sentimentClass, emotion: emotion, touchpoint: touchpoint, risk: risk, riskClass: riskClass, pr: pr, ops: ops });
  }

  function renderResults(sentiment, sentimentClass, emotion, touchpoint, risk, riskClass, pr, ops) {
    var sandboxResults = document.getElementById('sandbox-results');
    var sentEl = document.getElementById('sandbox-sentiment');
    var emotionEl = document.getElementById('sandbox-emotion');
    var touchpointEl = document.getElementById('sandbox-touchpoint');
    var riskEl = document.getElementById('sandbox-risk');
    var prRecEl = document.getElementById('sandbox-pr-rec');
    var opsRecEl = document.getElementById('sandbox-ops-rec');

    if (sentEl) {
      sentEl.textContent = sentiment;
      sentEl.className = 'result-val sentiment-badge ' + sentimentClass;
    }
    if (emotionEl) { emotionEl.textContent = emotion; }
    if (touchpointEl) { touchpointEl.textContent = touchpoint; }
    if (riskEl) {
      riskEl.textContent = risk;
      riskEl.className = 'result-val risk-text ' + riskClass;
    }
    if (prRecEl) { prRecEl.textContent = pr; }
    if (opsRecEl) { opsRecEl.innerHTML = ops.map(function (item) { return '<li>' + item + '</li>'; }).join(''); }

    if (sandboxResults) { sandboxResults.style.display = 'block'; }
  }

  return {
    initSandbox: initSandbox,
    analyzeText: analyzeText,
    renderResults: renderResults
  };
})();
