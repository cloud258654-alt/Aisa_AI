var ApiService = (function () {
  var BASE_URL = '/api/v1';
  var MOCK_DELAY = 300;

  function getToken() {
    return localStorage.getItem('sentinel_token');
  }

  function setToken(token) {
    localStorage.setItem('sentinel_token', token);
  }

  function getRefreshToken() {
    return localStorage.getItem('sentinel_refresh_token');
  }

  function setRefreshToken(rt) {
    localStorage.setItem('sentinel_refresh_token', rt);
  }

  function clearTokens() {
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_refresh_token');
  }

  function request(method, path, body, useMock) {
    if (useMock === undefined) { useMock = true; }
    var url = BASE_URL + path;
    var headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    var token = getToken();
    if (token) { headers['Authorization'] = 'Bearer ' + token; }

    return new Promise(function (resolve, reject) {
      var options = { method: method, headers: headers };
      if (body && method !== 'GET') { options.body = JSON.stringify(body); }

      fetch(url, options).then(function (response) {
        if (response.status === 401) {
          return refreshTokenRequest().then(function (refreshed) {
            if (refreshed) {
              headers['Authorization'] = 'Bearer ' + getToken();
              return fetch(url, Object.assign({}, options, { headers: headers }));
            }
            throw new Error('Session expired');
          }).then(function (retryResponse) {
            if (retryResponse.ok) { return retryResponse.json(); }
            throw new Error('Unauthorized');
          });
        }
        if (!response.ok) { throw new Error('API Error: ' + response.status); }
        return response.json();
      }).then(function (data) {
        resolve(data);
      }).catch(function (err) {
        if (useMock) {
          console.warn('API ' + method + ' ' + path + ' failed, using mock:', err.message);
          resolve(getMockResponse(path, method, body));
        } else {
          reject(err);
        }
      });
    });
  }

  function refreshTokenRequest() {
    var refreshToken = getRefreshToken();
    if (!refreshToken) { return Promise.resolve(false); }
    return fetch(BASE_URL + '/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken: refreshToken })
    }).then(function (r) {
      if (r.ok) { return r.json(); }
      return null;
    }).then(function (data) {
      if (data && data.token) {
        setToken(data.token);
        if (data.refreshToken) { setRefreshToken(data.refreshToken); }
        return true;
      }
      return false;
    }).catch(function () { return false; });
  }

  function getMockResponse(path, method, body) {
    return new Promise(function (resolve) {
      setTimeout(function () {
        resolve(mockData(path, method, body));
      }, MOCK_DELAY);
    });
  }

  function mockData(path, method, body) {
    if (path.indexOf('/auth/login') === 0) {
      return { token: 'eyJhbGciOiJIUzI1NiJ9.mock-token', refreshToken: 'rt_mock_001', user: { id: 'u1', name: 'Brand Manager', email: body ? body.email : 'admin@sentinel.ai', role: 'brand_manager', avatar: null } };
    }
    if (path.indexOf('/auth/refresh') === 0) {
      return { token: 'eyJhbGciOiJIUzI1NiJ9.mock-refreshed', refreshToken: 'rt_mock_new' };
    }
    if (path.indexOf('/auth/me') === 0) {
      return { id: 'u1', name: 'Brand Manager', email: 'admin@sentinel.ai', role: 'brand_manager', permissions: ['all'] };
    }
    if (path.indexOf('/voc/voices') === 0) {
      return { data: [], total: 0, page: 1, pageSize: 20 };
    }
    if (path.indexOf('/voc/summary') === 0) {
      return { totalMentions: 12847, positiveRatio: 0.72, negativeRatio: 0.18, neutralRatio: 0.10, topTopics: ['服務態度', '出餐速度', '食材品質'], channels: { google: 3421, threads: 2890, facebook: 2150, instagram: 1890, dcard: 1340, ptt: 1156 } };
    }
    if (path.indexOf('/voc/trends') === 0) {
      return { daily: Array.from({ length: 30 }, function (_, i) { return { date: '2026-06-' + String(i + 1).padStart(2, '0'), positive: 120 + Math.floor(Math.random() * 40), negative: 20 + Math.floor(Math.random() * 30), neutral: 30 + Math.floor(Math.random() * 20) }; }), overall: 'stable' };
    }
    if (path.indexOf('/cx/journeys') === 0) {
      return { nodes: [{ id: 'search', name: '搜尋探索', score: 98 }, { id: 'book', name: '線上預約', score: 96 }, { id: 'wait', name: '候位到店', score: 84 }, { id: 'service', name: '服務體驗', score: 79 }, { id: 'pay', name: '付款收銀', score: 95 }, { id: 'review', name: '評論回饋', score: 92 }] };
    }
    if (path.indexOf('/cx/diagnostics') === 0) {
      return [{ id: 'd1', type: 'warning', title: '候位到店摩擦 (等候時間過長)', store: '信義旗艦店', desc: '最近 48 小時有 18 則負評提及「排隊引導混亂、候位時間超過預期」。AI 偵測流程流失率上升 4.2%。' }, { id: 'd2', type: 'error', title: '服務體驗摩擦 (出餐速度及服務態度)', store: '信義旗艦店', desc: '輿情中提及「出餐送錯、主餐冷掉、員工態度冷淡」之關鍵字密度暴增 320%。品牌健康度主要扣分項。' }];
    }
    if (path.indexOf('/cx/touchpoints') === 0) {
      return ['搜尋探索', '線上預約', '候位到店', '服務體驗', '付款收銀', '評論回饋'];
    }
    if (path.indexOf('/brand/current') === 0) {
      return { brandScore: 92.4, storeHealth: 98.1, csat: 4.82, resolutionRate: 94.5, riskScore: 12, risk: 'low', updatedAt: new Date().toISOString() };
    }
    if (path.indexOf('/brand/history') === 0) {
      return Array.from({ length: 30 }, function (_, i) { return { date: '2026-06-' + String(i + 1).padStart(2, '0'), brandScore: 90 + Math.random() * 8, riskScore: 5 + Math.random() * 30 }; });
    }
    if (path.indexOf('/brand/alerts') === 0) {
      return [{ id: 'a1', level: 'warning', title: '信義店排隊動線需改善', createdAt: new Date().toISOString() }, { id: 'a2', level: 'info', title: '各分店整體健康度良好', createdAt: new Date().toISOString() }];
    }
    if (path.indexOf('/executive/morning-brief') === 0) {
      return {
        date: new Date().toISOString().split('T')[0],
        summary: '今日全品牌輿情穩定，信義旗艦店排隊摩擦指標持續需關注。AI COO 已識別 2 項營運風險關聯，並預測 7 日品牌健康指數將達 93.1。',
        riskLevel: 'low',
        key_metrics: { brand_health_score: 92.4, store_health_index: 98.1, risk_score: 12, total_voices_today: 342 },
        topStores: [
          { name: '忠孝 SOGO 店', score: 96.8, status: 'healthy', trend: 'up', issues: 0 },
          { name: '台中公益店', score: 95.2, status: 'healthy', trend: 'stable', issues: 0 },
          { name: '板橋大遠百店', score: 93.5, status: 'healthy', trend: 'down', issues: 1 },
          { name: '信義旗艦店', score: 91.0, status: 'warning', trend: 'down', issues: 3 },
          { name: '機場快取店', score: 85.0, status: 'stable', trend: 'up', issues: 0 }
        ],
        biggestProblem: {
          title: 'Eastside Plaza 系統性衰退',
          severity: 'high',
          description: '4 項併發警示。自 6/15 店經理職缺以來持續下滑。',
          affectedStores: ['Eastside Plaza'],
          recommendation: '立即指派代理店經理，派遣區域營運總監進行為期 2 週的現場評估。'
        },
        aiCooRecs: [
          { action: '發布社交媒體退貨政策聲明', impact: '48h 內降低負面聲量 40%', confidence: 0.92 },
          { action: '尖峰時段調配 5 名員工', impact: '等候時間減少 3 分鐘', confidence: 0.88 },
          { action: 'Eastside Plaza 加速招募 3 名兼職人員', impact: '30 天內逆轉 NPS 下滑', confidence: 0.78 }
        ],
        predictions: [
          { day: 'Day 1', health: 93.1, risk: 14.2, negative: 28 },
          { day: 'Day 2', health: 93.5, risk: 13.8, negative: 25 },
          { day: 'Day 3', health: 94.0, risk: 12.5, negative: 22 },
          { day: 'Day 4', health: 93.8, risk: 13.0, negative: 24 },
          { day: 'Day 5', health: 94.2, risk: 11.8, negative: 20 },
          { day: 'Day 6', health: 94.5, risk: 10.5, negative: 18 },
          { day: 'Day 7', health: 94.8, risk: 9.8, negative: 15 }
        ],
        alerts: [{ type: 'warning', message: 'Eastside Plaza 負評集中排隊體驗', count: 18 }, { type: 'critical', message: '社交媒體退貨政策負面聲量上升', count: 34 }, { type: 'info', message: '其餘 7 間分店無重大客訴', count: 0 }],
        actionItems: ['發布社交媒體退貨政策說明', '檢討 Eastside Plaza 尖峰排隊動線', '追蹤 Eastside Plaza 服務 SOP 改善進度', '確認各分店週末備戰人力']
      };
    }
    if (path.indexOf('/executive/today-summary') === 0) {
      return { date: new Date().toISOString().split('T')[0], totalReviews: 287, positive: 207, negative: 52, neutral: 28, avgCsat: 4.82, resolutionRate: 94.5 };
    }
    if (path.indexOf('/executive/store-ranking') === 0) {
      return { rankings: [
        { rank: 1, store_name: 'Downtown Flagship', score: 92.5, status: 'healthy', trend: 'up', critical_issues: 0, alert_count: 0 },
        { rank: 2, store_name: 'Westside Mall', score: 85.0, status: 'healthy', trend: 'stable', critical_issues: 0, alert_count: 1 },
        { rank: 3, store_name: 'Airport Kiosk', score: 78.0, status: 'stable', trend: 'stable', critical_issues: 1, alert_count: 2 },
        { rank: 4, store_name: 'Northgate Center', score: 62.0, status: 'warning', trend: 'stable', critical_issues: 1, alert_count: 1 },
        { rank: 5, store_name: 'Eastside Plaza', score: 55.0, status: 'critical', trend: 'down', critical_issues: 3, alert_count: 4 },
        { rank: 6, store_name: 'Southgate Village', score: 71.0, status: 'stable', trend: 'up', critical_issues: 0, alert_count: 1 },
        { rank: 7, store_name: 'Harbor View', score: 68.0, status: 'warning', trend: 'down', critical_issues: 2, alert_count: 2 },
        { rank: 8, store_name: 'University Corner', score: 65.0, status: 'stable', trend: 'stable', critical_issues: 0, alert_count: 0 },
        { rank: 9, store_name: 'Metro Station', score: 59.0, status: 'warning', trend: 'down', critical_issues: 2, alert_count: 3 },
        { rank: 10, store_name: 'Riverside Outlet', score: 52.0, status: 'critical', trend: 'down', critical_issues: 4, alert_count: 5 }
      ], total_stores: 10 };
    }
    if (path.indexOf('/executive/key-risks') === 0) {
      return {
        date: new Date().toISOString().split('T')[0],
        total_active_risks: 12,
        overall_risk_index: 62.5,
        critical_risks: [
          { risk_id: 'risk_001', title: 'Social Media Return Policy Backlash', description: 'Viral posts on Threads/Twitter criticizing new return policy. +12% sentiment velocity per hour.', severity: 'critical', impact_score: 91.0, affected_stores: 12, probability: 0.85, financial_exposure: '$120K-$250K', trend_direction: 'accelerating', recommended_mitigation: 'Issue immediate multi-channel statement.' },
          { risk_id: 'risk_002', title: 'Eastside Plaza Performance Decline', description: '4 concurrent alerts. Store manager vacancy since June 15.', severity: 'high', impact_score: 78.0, affected_stores: 1, probability: 0.90, financial_exposure: '$45K-$80K', trend_direction: 'worsening', recommended_mitigation: 'Appoint interim manager.' }
        ],
        emerging_risks: [
          { risk_id: 'emerging_001', title: 'Competitor Price Drop in Downtown', signal_strength: 'moderate' },
          { risk_id: 'emerging_002', title: 'Supply Chain Delay Westside', signal_strength: 'weak' }
        ],
        risk_heatmap: { high_probability_high_impact: 3, high_probability_low_impact: 2, low_probability_high_impact: 1, low_probability_low_impact: 6 }
      };
    }
    if (path.indexOf('/executive/opportunities') === 0) {
      return {
        date: new Date().toISOString().split('T')[0],
        total_opportunities: 14,
        high_priority: [
          { opportunity_id: 'opp_001', title: 'AI-Powered Dynamic Staffing', category: 'Operations', potential_impact: 'Reduce wait complaints 45%', effort_required: 'Medium', roi_estimate: '3.2x 6mo', confidence: 0.89, affected_areas: ['All stores'], suggested_actions: ['Deploy predictive staffing model', 'Integrate POS signals'] },
          { opportunity_id: 'opp_002', title: 'Social Media Proactive Response', category: 'Brand', potential_impact: 'Reduce negative spread 60%', effort_required: 'Low', roi_estimate: '8.5x 3mo', confidence: 0.94, affected_areas: ['Social channels'], suggested_actions: ['15-min response SLA', 'Templated responses'] }
        ],
        medium_priority: [],
        quick_wins: [
          { opportunity_id: 'opp_006', title: 'Standardize Follow-Up Emails', category: 'Retention', potential_impact: 'Review rate +35%', effort_required: 'Very Low', roi_estimate: '12x 1mo', confidence: 0.95, affected_areas: ['Email'], suggested_actions: ['Auto post-visit email', 'CSAT survey'] }
        ]
      };
    }
    if (path.indexOf('/executive/ai-coo-summary') === 0) {
      return {
        date: new Date().toISOString().split('T')[0],
        executive_statement: 'Overall operational posture: STRONG. Brand health 92.4/100. Primary concern: social media sentiment spike.',
        strategic_priorities: [
          { rank: 1, initiative: 'Social Media Sentiment Recovery', urgency: 'critical', timeframe: '48 hours' },
          { rank: 2, initiative: 'Eastside Plaza Rescue', urgency: 'high', timeframe: '30 days' }
        ],
        domain_summaries: [
          { domain: 'Brand Health', status: 'excellent', score: 92.4, recommendations: ['Maintain response cadence'] },
          { domain: 'Store Operations', status: 'good', score: 87.6, recommendations: ['Queue management pilot'] }
        ],
        top_actions_today: ['Issue social media statement', 'Dispatch director to Eastside', 'Reallocate peak staff'],
        critical_decisions_needed: [],
        kpi_summary: { brand_score_trend: 'up +1.2%', customer_satisfaction: '4.82/5.0', resolution_rate: '94.5%' }
      };
    }
    if (path.indexOf('/executive/metrics-snapshot') === 0) {
      return {
        timestamp: new Date().toISOString(),
        brand_health: { overall_score: 92.4, trend: 'improving', previous_day: 91.2 },
        store_health: { overall_index: 98.1, store_count: 12, stores_healthy: 9, stores_warning: 2, stores_critical: 1 },
        voc_metrics: { total_voices_today: 342, sentiment_distribution: { positive_pct: 44, neutral_pct: 27, negative_pct: 29 } },
        risk_metrics: { overall_risk_score: 62.5, risk_level: 'elevated', active_alerts: 12 },
        cx_metrics: { journey_completion_rate: 72.0, nps_score: 38.0, csat_overall: 4.82 },
        competitive_metrics: { market_position: 3, total_competitors_tracked: 8 },
        trend_metrics: { overall_trend_direction: 'improving', momentum_score: 72.0 }
      };
    }
    if (path.indexOf('/sandbox/analyze') === 0) {
      return { sentiment: 'negative', sentimentScore: 96, emotion: 'Anger / Frustration', touchpoint: 'Wait & Service', riskLevel: 'high', riskScore: 78, prDraft: '您好，非常抱歉讓您有不愉快的用餐體驗。關於候位時間過長以及餐點溫度不符預期的情況，我們已立刻通報該店經理進行流程檢討。', opsSuggestions: ['尖峰時段出餐雙重覆核機制', '更新外場排隊引導機制'] };
    }
    if (path.indexOf('/workflow/cases') === 0) {
      return { data: [], total: 0 };
    }
    if (path.indexOf('/knowledge/articles') === 0 || path.indexOf('/knowledge/search') === 0) {
      return { data: [], total: 0 };
    }
    if (path.indexOf('/trends/overview') === 0 || path.indexOf('/trends/predictions') === 0) {
      return { data: [], total: 0 };
    }
    if (path.indexOf('/competitors') === 0) {
      return { data: [], total: 0 };
    }
    if (method === 'POST' && path.indexOf('/workflow/cases') === 0) {
      return { id: 'case_' + Date.now(), status: 'created' };
    }
    if (path.indexOf('/system/health') === 0) {
      return { system: 'healthy', database: 'healthy', redis: 'healthy', ai_engine: 'healthy', queue: 'healthy', uptime: '14d 6h 32m', version: '3.0.0', timestamp: new Date().toISOString() };
    }
    if (path.indexOf('/system/status') === 0) {
      return { status: 'operational', cpu: 34.2, memory: 62.8, disk: 45.1, active_users: 12, requests_per_minute: 847, last_incident: null };
    }
    return { data: null };
  }

  return {
    auth: {
      login: function (email, password) { return request('POST', '/auth/login', { email: email, password: password }); },
      refresh: function (refreshToken) { return request('POST', '/auth/refresh', { refreshToken: refreshToken }, false); },
      getMe: function () { return request('GET', '/auth/me'); },
      logout: function () { clearTokens(); return Promise.resolve(true); }
    },
    voc: {
      getVoices: function (params) { return request('GET', '/voc/voices' + toQuery(params)); },
      getVoice: function (id) { return request('GET', '/voc/voices/' + id); },
      getSummary: function () { return request('GET', '/voc/summary'); },
      getTrends: function (params) { return request('GET', '/voc/trends' + toQuery(params)); }
    },
    cx: {
      getJourneys: function (params) { return request('GET', '/cx/journeys' + toQuery(params)); },
      getDiagnostics: function (storeId) { return request('GET', '/cx/diagnostics' + toQuery({ storeId: storeId })); },
      getTouchpoints: function () { return request('GET', '/cx/touchpoints'); }
    },
    brand: {
      getCurrent: function () { return request('GET', '/brand/current'); },
      getHistory: function (params) { return request('GET', '/brand/history' + toQuery(params)); },
      getAlerts: function () { return request('GET', '/brand/alerts'); }
    },
    executive: {
      getMorningBrief: function () { return request('GET', '/executive/morning-brief'); },
      getTodaySummary: function () { return request('GET', '/executive/today-summary'); },
      getStoreRanking: function () { return request('GET', '/executive/store-ranking'); },
      getKeyRisks: function () { return request('GET', '/executive/key-risks'); },
      getOpportunities: function () { return request('GET', '/executive/opportunities'); },
      getAICooSummary: function () { return request('GET', '/executive/ai-coo-summary'); },
      getMetricsSnapshot: function () { return request('GET', '/executive/metrics-snapshot'); }
    },
    sandbox: {
      analyze: function (text) { return request('POST', '/sandbox/analyze', { text: text }); }
    },
    workflow: {
      getCases: function (params) { return request('GET', '/workflow/cases' + toQuery(params)); },
      createCase: function (data) { return request('POST', '/workflow/cases', data); },
      updateCase: function (id, data) { return request('PATCH', '/workflow/cases/' + id, data); }
    },
    knowledge: {
      getArticles: function (params) { return request('GET', '/knowledge/articles' + toQuery(params)); },
      search: function (query) { return request('GET', '/knowledge/search' + toQuery({ q: query })); }
    },
    trends: {
      getOverview: function (params) { return request('GET', '/trends/overview' + toQuery(params)); },
      getPredictions: function () { return request('GET', '/trends/predictions'); }
    },
    competitors: {
      list: function () { return request('GET', '/competitors'); },
      getBenchmark: function () { return request('GET', '/competitors/benchmark'); }
    },
    system: {
      getHealth: function () { return request('GET', '/system/health'); },
      getStatus: function () { return request('GET', '/system/status'); }
    }
  };

  function toQuery(params) {
    if (!params) { return ''; }
    var keys = Object.keys(params);
    if (keys.length === 0) { return ''; }
    return '?' + keys.map(function (k) { return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]); }).join('&');
  }
})();
