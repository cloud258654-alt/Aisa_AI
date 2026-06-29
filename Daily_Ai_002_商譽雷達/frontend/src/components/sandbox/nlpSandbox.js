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
          alert(I18n.t('sandbox.alertEmpty'));
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

    var sentiment = I18n.t('sandbox.defaultSentimentPositive') + ' (92%)';
    var sentimentClass = 'positive';
    var emotion = 'Joy \uD83D\uDE0A / Satisfaction \uD83D\uDC4D';
    var touchpoint = 'Service (\u670D\u52D9\u9AD4\u9A57) & Product (\u9910\u9EDE\u54C1\u8CEA)';
    var risk = I18n.t('sandbox.defaultRiskLow') + ' (5)';
    var riskClass = 'low';
    var pr = '\u60A8\u597D\uFF0C\u611F\u8B1D\u60A8\u5C0D\u6211\u5011\u670D\u52D9\u8207\u54C1\u8CEA\u7684\u80AF\u5B9A\uFF01\u6211\u5011\u6703\u6301\u7E8C\u7DAD\u6301\u9AD8\u54C1\u8CEA\u6C34\u6E96\uFF0C\u671F\u5F85\u4E0B\u6B21\u518D\u5EA6\u70BA\u60A8\u63D0\u4F9B\u6109\u5FEB\u7684\u9AD4\u9A57\u3002';
    var ops = [
      '\u7DAD\u6301\u7576\u524D\u670D\u52D9\u898F\u7BC4\uFF0C\u5C07\u8A72\u5E97\u540C\u4EC1\u7684\u512A\u79C0\u4E8B\u8E5F\u8A18\u9304\u5165\u672C\u6708\u8003\u6838\u6307\u6A19\u3002',
      '\u6301\u7E8C\u7DAD\u6301\u98DF\u6750\u4F9B\u61C9\u93C8\u7684\u7A69\u5B9A\u54C1\u8CEA\u3002'
    ];

    if (apiResult && apiResult.sentiment) {
      sentiment = (apiResult.sentiment === 'negative' ? I18n.t('sandbox.defaultSentimentNegative') : I18n.t('sandbox.defaultSentimentPositive')) + ' (' + apiResult.sentimentScore + '%)';
      sentimentClass = apiResult.sentiment;
      emotion = apiResult.emotion || emotion;
      touchpoint = apiResult.touchpoint || touchpoint;
      risk = (apiResult.riskLevel === 'high' ? I18n.t('sandbox.defaultRiskCritical') + ' (' : I18n.t('sandbox.defaultRiskLow') + ' (') + apiResult.riskScore + ')';
      riskClass = apiResult.riskLevel || 'low';
      pr = apiResult.prDraft || pr;
      ops = apiResult.opsSuggestions || ops;
    } else {
      var lowerText = text.toLowerCase();

      if (lowerText.indexOf('\u721B') > -1 || lowerText.indexOf('\u51B0') > -1 || lowerText.indexOf('\u81ED\u81C9') > -1 || lowerText.indexOf('\u751F\u6C23') > -1 || lowerText.indexOf('\u7B49\u5F88\u4E45') > -1 || lowerText.indexOf('\u62C9\u809A\u5B50') > -1 || lowerText.indexOf('\u809A\u5B50\u75DB') > -1 || lowerText.indexOf('\u5DEE') > -1) {
        sentiment = I18n.t('sandbox.defaultSentimentNegative') + ' (96%)';
        sentimentClass = 'negative';
        emotion = 'Anger \uD83D\uDE20 / Frustration \uD83D\uDE29';

        if (lowerText.indexOf('\u7B49') > -1 || lowerText.indexOf('\u5019') > -1) {
          touchpoint = 'Wait (\u7B49\u5019\u5230\u5E97) & Service (\u670D\u52D9\u9AD4\u9A57)';
        } else if (lowerText.indexOf('\u51B0') > -1 || lowerText.indexOf('\u4E0D\u65B0\u9BAE') > -1 || lowerText.indexOf('\u62C9\u809A\u5B50') > -1) {
          touchpoint = 'Service (\u670D\u52D9\u9AD4\u9A57) & Product (\u98DF\u54C1\u54C1\u8CEA)';
        } else {
          touchpoint = 'Service (\u670D\u52D9\u9AD4\u9A57) / Touchpoint friction';
        }

        if (lowerText.indexOf('\u62C9\u809A\u5B50') > -1 || lowerText.indexOf('\u6BD2') > -1 || lowerText.indexOf('\u96C6\u9AD4') > -1) {
          risk = I18n.t('sandbox.defaultRiskCritical') + ' (85)';
          riskClass = 'high';
          pr = '\u60A8\u597D\uFF0C\u975E\u5E38\u62B1\u6B49\u8B93\u60A8\u906D\u9047\u6B64\u7528\u9910\u60C5\u6CC1\u3002\u672C\u516C\u53F8\u9AD8\u5EA6\u91CD\u8996\u6B64\u98DF\u5B89\u7591\u616E\uFF0C\u5DF2\u7ACB\u523B\u8CAC\u6210\u76F8\u95DC\u5206\u5E97\u4E3B\u7BA1\u6E05\u67E5\u51B7\u93C8\u5132\u5B58\u8207\u5EDA\u623F\u4F5C\u696D\u3002\u6211\u5011\u975E\u5E38\u95DC\u5207\u60A8\u7684\u8EAB\u9AD4\u72C0\u6CC1\uFF0C\u8ACB\u60A8\u65B9\u4FBF\u64A5\u5197\u806F\u7D61\u6211\u5011\uFF0C\u4EE5\u4FBF\u5B89\u6392\u5C31\u91AB\u8907\u67E5\u8207\u5168\u984D\u88DC\u511F\u3002';
          ops = ['\u5206\u5E97\u7ACB\u5373\u5C0D\u51B7\u93C8\u53CA\u98DF\u6750\u65B0\u9BAE\u5EA6\u9032\u884C\u81EA\u4E3B\u5C01\u5B58\u8207\u9001\u9A57\u3002', '\u5C0D\u7576\u65E5\u6536\u767C\u8CA8\u53CA\u5EAB\u5B58\u98DF\u6750\u6E05\u55AE\u9032\u884C\u56DE\u6EAF\u6392\u67E5\u3002'];
        } else {
          risk = I18n.t('sandbox.defaultRiskHigh') + ' (72)';
          riskClass = 'high';
          pr = '\u60A8\u597D\uFF0C\u5341\u5206\u62B1\u6B49\u8B93\u60A8\u5728\u6B64\u6B21\u7528\u9910\u4E2D\u611F\u5230\u4E0D\u6109\u5FEB\u3002\u91DD\u5C0D\u60A8\u63D0\u53CA\u7684\u9910\u9EDE\u6EAB\u5EA6\u53CA\u54E1\u5DE5\u614B\u5EA6\u554F\u984C\uFF0C\u6211\u5011\u5DF2\u7ACB\u5373\u8F49\u9054\u5206\u5E97\u5E97\u9577\u9032\u884C\u6574\u9813\u8207\u52A0\u5F37\u6559\u80B2\u8A13\u7DF4\uFF0C\u4E26\u5C07\u56B4\u683C\u76E3\u7763\u51FA\u9910\u8986\u6838\u3002\u5E0C\u671B\u60A8\u7D66\u4E88\u6211\u5011\u6539\u9032\u7684\u6A5F\u6703\u3002';
          ops = ['\u8981\u6C42\u5206\u5E97\u843D\u5BE6\u51FA\u9910\u96D9\u91CD\u6838\u5C0D\uFF0C\u4E26\u65BC\u73FE\u5834\u9032\u884C\u4EBA\u54E1\u61C9\u5C0D\u57F9\u8A13\u7763\u5C0E\u3002', '\u5E97\u7D93\u7406\u89AA\u81EA\u5411\u9867\u5BA2\u81F4\u96FB\u8AAA\u660E\u6539\u5584\u8A08\u756B\u4E26\u81F4\u6B49\u3002'];
        }
      } else if (lowerText.indexOf('\u666E\u901A') > -1 || lowerText.indexOf('\u9084\u597D') > -1 || lowerText.indexOf('\u4E00\u822C') > -1 || lowerText.indexOf('\u8CB4') > -1) {
        sentiment = I18n.t('sandbox.defaultSentimentNeutral') + ' (60%)';
        sentimentClass = 'neutral';
        emotion = 'Neutral \uD83D\uDE10 / Evaluation \uD83E\uDD14';
        touchpoint = 'Product (\u9910\u9EDE\u54C1\u8CEA) & Price (\u50F9\u683C\u8A8D\u77E5)';
        risk = I18n.t('sandbox.defaultRiskLow') + ' (15)';
        riskClass = 'low';
        pr = '\u60A8\u597D\uFF0C\u611F\u8B1D\u60A8\u7684\u56DE\u994B\u3002\u6211\u5011\u6703\u6301\u7E8C\u807D\u53D6\u5404\u65B9\u9867\u5BA2\u610F\u898B\uFF0C\u5C0D\u7522\u54C1\u7684\u6027\u50F9\u6BD4\u8207\u53E3\u5473\u9032\u884C\u512A\u5316\u3002\u671F\u5F85\u672A\u4F86\u80FD\u70BA\u60A8\u63D0\u4F9B\u66F4\u70BA\u9A5A\u8277\u7684\u670D\u52D9\u3002';
        ops = ['\u8A18\u9304\u9867\u5BA2\u5C0D\u65BC\u50F9\u683C\u8207\u9910\u9EDE\u7F8E\u5473\u5EA6\u7684\u6027\u50F9\u6BD4\u56DE\u994B\uFF0C\u5F59\u6574\u7D66\u7814\u767C\u7E3D\u90E8\u3002', '\u5B9A\u671F\u89C0\u5BDF\u5C0D\u624B\u54C1\u724C\u540C\u50F9\u4F4D\u7522\u54C1\u7684\u7AF6\u722D\u529B\u3002'];
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
