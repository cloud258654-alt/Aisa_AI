var LearningPanelComponent = (function () {
  var learningData = null;

  function initLearningPanel() {
    var container = document.getElementById('learning-section');
    if (!container) { return; }

    loadLearningData();
    bindNewCaseButton();
  }

  function loadLearningData() {
    setTimeout(function () {
      learningData = {
        similarCases: [
          {
            id: 'case_042',
            title: 'Return Policy Social Media Backlash',
            similarity: 94,
            date: '2026-03-15',
            resolution: 'Multi-channel clarification campaign deployed within 6 hours. CEO video statement posted. Sentiment recovered to baseline in 48 hours.',
            success: true,
            outcome: 'Negative sentiment dropped 62% in 48 hours. Brand trust score recovered to 89 within 1 week.',
          },
          {
            id: 'case_038',
            title: 'Store Manager Vacancy Performance Decline',
            similarity: 87,
            date: '2026-02-20',
            resolution: 'Regional director deployed as interim manager. Performance improvement plan implemented with daily check-ins. New manager hired in 21 days.',
            success: true,
            outcome: 'Store health score climbed from 48 to 72 in 45 days. NPS recovered from 8 to 28.',
          },
          {
            id: 'case_029',
            title: 'Checkout Wait Time Complaints Spike',
            similarity: 82,
            date: '2026-01-10',
            resolution: 'Queue management system deployed at top 3 affected stores. Peak-hour staff reallocation. Customer wait time commitment signs installed.',
            success: true,
            outcome: 'Wait time complaints reduced by 55% in 30 days. CSAT improved by 0.7 points across affected stores.',
          },
          {
            id: 'case_015',
            title: 'Food Quality Consistency Issue',
            similarity: 71,
            date: '2025-11-05',
            resolution: 'Conducted kitchen audit across all stores. Standardized recipe execution with photo guides. Implemented pre-service quality checks.',
            success: true,
            outcome: 'Food-related complaints dropped 60%. Quality satisfaction score improved from 72 to 88.',
          },
        ],
        whatWorked: [
          { strategy: 'Fast Response + CEO Video', successRate: 94, cases: 12, avgRecovery: '48 hours' },
          { strategy: 'Interim Manager + Daily Check-ins', successRate: 88, cases: 8, avgRecovery: '30-45 days' },
          { strategy: 'Queue System + Staff Reallocation', successRate: 91, cases: 15, avgRecovery: '14-30 days' },
        ],
        patternInsights: [
          'Cases resolved within first 4 hours show 3x better sentiment recovery rates',
          'Stores with interim management plans recover 40% faster than those without',
          'Multi-channel crisis response reduces brand damage by 55% vs. single channel',
          'Staff training completion above 90% correlates with 65% fewer repeat incidents',
        ],
      };
      renderLearning(learningData);
      DashboardStore.setState({ learningCases: learningData });
    }, 300);
  }

  function renderLearning(data) {
    if (!data) { return; }

    var similarCasesEl = document.getElementById('learning-similar-cases');
    var whatWorkedEl = document.getElementById('learning-what-worked');
    var patternInsightsEl = document.getElementById('learning-patterns');

    if (similarCasesEl && data.similarCases) {
      similarCasesEl.innerHTML = data.similarCases.map(function (c) {
        return '<div class="similar-case-card">' +
          '<div class="sc-card-header">' +
          '  <span class="sc-title">' + c.title + '</span>' +
          '  <span class="sc-similarity ' + (c.similarity >= 90 ? 'high' : c.similarity >= 75 ? 'medium' : 'low') + '">' + c.similarity + '% match</span>' +
          '</div>' +
          '<div class="sc-card-meta">' +
          '  <span class="sc-date">' + c.date + '</span>' +
          '  <span class="sc-outcome ' + (c.success ? 'success' : 'failed') + '">' + (c.success ? 'Resolved Successfully' : 'Unresolved') + '</span>' +
          '</div>' +
          '<div class="sc-card-body">' +
          '  <p><strong>Approach:</strong> ' + c.resolution + '</p>' +
          '  <p><strong>Outcome:</strong> ' + c.outcome + '</p>' +
          '</div>' +
        '</div>';
      }).join('');
    }

    if (whatWorkedEl && data.whatWorked) {
      whatWorkedEl.innerHTML = '<h4 class="lp-subtitle">What Worked Before</h4>' +
        data.whatWorked.map(function (w) {
          return '<div class="ww-item">' +
            '<div class="ww-header">' +
            '  <span class="ww-strategy">' + w.strategy + '</span>' +
            '  <span class="ww-rate">' + w.successRate + '% success</span>' +
            '</div>' +
            '<div class="ww-bar-wrap"><div class="ww-bar" style="width:' + w.successRate + '%"></div></div>' +
            '<span class="ww-meta">' + w.cases + ' past cases | Average recovery: ' + w.avgRecovery + '</span>' +
          '</div>';
        }).join('');
    }

    if (patternInsightsEl && data.patternInsights) {
      patternInsightsEl.innerHTML = '<h4 class="lp-subtitle">AI-Discovered Patterns</h4>' +
        data.patternInsights.map(function (p) {
          return '<div class="lp-insight-item">' +
            '<span class="lp-insight-bullet">\u2022</span>' +
            '<span>' + p + '</span>' +
          '</div>';
        }).join('');
    }
  }

  function bindNewCaseButton() {
    var btn = document.getElementById('btn-new-learning-case');
    var form = document.getElementById('new-case-form');
    if (!btn || !form) { return; }

    btn.addEventListener('click', function () {
      form.style.display = form.style.display === 'none' ? 'block' : 'none';
    });

    var submitBtn = document.getElementById('btn-submit-case');
    if (submitBtn) {
      submitBtn.addEventListener('click', function () {
        var titleInput = document.getElementById('new-case-title');
        var descInput = document.getElementById('new-case-description');
        var storeInput = document.getElementById('new-case-store');

        if (!titleInput || !descInput) { return; }
        var title = titleInput.value.trim();
        var desc = descInput.value.trim();
        var store = storeInput ? storeInput.value.trim() : '';

        if (!title || !desc) {
          alert('Please fill in the case title and description.');
          return;
        }

        var similarEl = form.querySelector('.new-case-status');
        if (!similarEl) {
          similarEl = document.createElement('div');
          similarEl.className = 'new-case-status';
          form.appendChild(similarEl);
        }
        similarEl.innerHTML = '<div class="sim-card" style="margin-top:12px;">' +
          '  <div class="sim-card-header"><span class="sim-scenario">Case Stored: "' + title + '"</span></div>' +
          '  <div class="sim-narrative">AI is analyzing the case pattern... Found 2 similar historical cases. Pattern matching confidence: 88%. The AI Learning Engine will incorporate this case into the next pattern update cycle.</div>' +
          '</div>';

        titleInput.value = '';
        descInput.value = '';
        if (storeInput) { storeInput.value = ''; }
      });
    }

    var cancelBtn = document.getElementById('btn-cancel-case');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', function () {
        form.style.display = 'none';
      });
    }
  }

  return {
    initLearningPanel: initLearningPanel,
    loadLearningData: loadLearningData
  };
})();
