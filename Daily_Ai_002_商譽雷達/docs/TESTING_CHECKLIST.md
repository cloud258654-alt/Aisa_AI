# Sentinel ECXIP — Testing Checklist

> **Version:** 1.0.0 | **Date:** 2026-06-29 | **Status:** Manual QA for MVP

---

## 1. Frontend Manual Testing

### 1.1 Page: Dashboard / Executive Briefing Center
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 1 | Navigate to Dashboard | Morning brief loads with greeting, date, metrics row | [ ] |
| 2 | Verify greeting header | Greeting shows localized "Good morning/afternoon, COO" based on time | [ ] |
| 3 | Key metrics row | 4-5 metric cards render with values and trend arrows | [ ] |
| 4 | "Today's Biggest Problem" card | Highlight card shows the top risk with description | [ ] |
| 5 | AI COO Recommendations | 3-5 recommendations render with confidence bars | [ ] |
| 6 | Store Ranking mini-table (top 5) | Top 5 stores show with health scores and risk tags | [ ] |
| 7 | 7-day risk forecast sparklines | Mini chart renders for brand health prediction | [ ] |
| 8 | Refresh / reload page | All data re-fetches and renders correctly | [ ] |
| 9 | Resize browser window | Layout adjusts responsively (1400, 1200, 768 px breakpoints) | [ ] |

### 1.2 Page: Store Ranking
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 10 | Navigate to Store Ranking | Full store ranking table loads | [ ] |
| 11 | Health score color bars | Each row shows color bar proportional to score | [ ] |
| 12 | Risk level tags | Critical/High/Medium/Low tags colored appropriately | [ ] |
| 13 | Trend arrows | Up/down/neutral arrows reflect 14-day trend | [ ] |
| 14 | Filter: All | All stores displayed | [ ] |
| 15 | Filter: Critical | Only critical-risk stores shown | [ ] |
| 16 | Filter: Improving | Only improving stores shown | [ ] |
| 17 | Filter: Declining | Only declining stores shown | [ ] |
| 18 | Click store to expand | Detail panel opens with store health breakdown | [ ] |
| 19 | Close detail panel | Panel closes, returns to full table | [ ] |
| 20 | Critical issues count | Each row shows accurate issue count badge | [ ] |

### 1.3 Page: Predictive Intelligence
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 21 | Navigate to Predictions | Four forecast panels render | [ ] |
| 22 | Brand Health forecast | 7-day bar chart with trend line visible | [ ] |
| 23 | Risk Score forecast | 7-day projection with confidence bands | [ ] |
| 24 | Negative Volume forecast | Volume bars with daily labels | [ ] |
| 25 | Confidence indicator | Each forecast shows confidence percentage | [ ] |
| 26 | Simulation input | Enter a value and click simulate | [ ] |
| 27 | Simulation result | AI impact projection renders below input | [ ] |
| 28 | Empty simulation | No crash with empty input | [ ] |

### 1.4 Page: Learning Memory
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 29 | Navigate to Learning | Historical cases list renders | [ ] |
| 30 | Similarity matching | Each case shows match % (80-94%) | [ ] |
| 31 | Success rate tracking | Success/fail badges visible on past cases | [ ] |
| 32 | AI pattern insights | Pattern cards show discovered patterns | [ ] |
| 33 | "Store New Case" form | Form opens with all required fields | [ ] |
| 34 | Submit new case | Success message, case appears in list | [ ] |
| 35 | Empty form validation | Required fields show error messages | [ ] |

### 1.5 Page: Voice of Customer
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 36 | Navigate to VOC | Multi-channel voice stream renders | [ ] |
| 37 | Channel tabs | Switch between Google, Threads, Facebook, Instagram, Dcard, PTT | [ ] |
| 38 | Sentiment badges | Positive/Neutral/Negative badges with correct colors | [ ] |
| 39 | Stream auto-update | New voice items appear (demo mode: periodic) | [ ] |
| 40 | Voice item expand | Click shows full content and analysis | [ ] |
| 41 | Timestamps | Relative timestamps display correctly | [ ] |
| 42 | Empty channel | Channel with no data shows empty state message | [ ] |

### 1.6 Page: Customer Journey Map
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 43 | Navigate to Journey | 6-stage customer journey map renders | [ ] |
| 44 | Touchpoint nodes | All touchpoints visible with stage labels | [ ] |
| 45 | Friction indicators | Red/yellow markers on problematic touchpoints | [ ] |
| 46 | Store filter | Select different store, journey updates | [ ] |
| 47 | Hover on touchpoint | Tooltip with details appears | [ ] |
| 48 | Health score overlay | Score labels visible on each stage | [ ] |

### 1.7 Page: AI Brand Manager
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 49 | Navigate to AI Terminal | Terminal UI with scenario selector renders | [ ] |
| 50 | Select crisis scenario | Scenario context loads in terminal | [ ] |
| 51 | Trigger crisis analysis | Terminal shows streaming AI response | [ ] |
| 52 | Root Cause tab | Root cause analysis with 5-Why renders | [ ] |
| 53 | SOP tab | SOP generation with steps and checklist renders | [ ] |
| 54 | PR tab | PR response drafted in appropriate language | [ ] |
| 55 | Legal tab | Legal risk assessment with recommendations | [ ] |
| 56 | Copy to clipboard | Copy buttons work for PR and SOP text | [ ] |

### 1.8 Page: NLP Sandbox
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 57 | Navigate to Sandbox | Text input area and analysis panel render | [ ] |
| 58 | Type text and analyze | Result cards populate (sentiment, emotion, touchpoint, risk) | [ ] |
| 59 | Chinese text input | Analysis works with Chinese characters | [ ] |
| 60 | English text input | Analysis works with English text | [ ] |
| 61 | Empty input warning | "Please enter text" message shown | [ ] |
| 62 | Loading state | Spinner shown during analysis | [ ] |
| 63 | Error state | Error handling if analysis fails | [ ] |

---

## 2. i18n Testing

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 64 | Default language | UI loads in zh-TW by default | [ ] |
| 65 | Switch to English | Click "EN" button, all text switches to English | [ ] |
| 66 | Switch back to Chinese | Click "繁中" button, all text returns to Chinese | [ ] |
| 67 | Persistence across reload | Language preference restored after page refresh | [ ] |
| 68 | Persistence across sessions | Language preference persists in localStorage | [ ] |
| 69 | All 8 pages tested | Switch language on every page, no untranslated text | [ ] |
| 70 | Component dynamic text | Dashboard metrics, store tags, prediction labels all switch | [ ] |
| 71 | data-i18n attributes | All 124 static text elements updated | [ ] |
| 72 | data-i18n-placeholder | Input placeholders switch language | [ ] |
| 73 | data-i18n-title | Tooltips switch language | [ ] |
| 74 | Parameter interpolation | `{{param}}` correctly substitutes values | [ ] |
| 75 | Missing key fallback | Missing translations show key name or HTML fallback | [ ] |

---

## 3. API Endpoint Testing

### 3.1 Health Check
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 76 | `GET /api/v1/health` | Returns `{status: "healthy", version: "1.0.0"}` | [ ] |
| 77 | Health includes DB status | Database connection status reported | [ ] |
| 78 | Health includes Redis status | Redis connection status reported | [ ] |

### 3.2 Auth Endpoints
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 79 | `POST /api/v1/auth/login` valid | Returns access_token + refresh_token | [ ] |
| 80 | `POST /api/v1/auth/login` invalid | Returns 401 with error message | [ ] |
| 81 | `POST /api/v1/auth/refresh` valid | Returns new access_token | [ ] |
| 82 | `POST /api/v1/auth/refresh` expired | Returns 401 | [ ] |
| 83 | `GET /api/v1/auth/me` | Returns current user profile | [ ] |
| 84 | Protected endpoint no token | Returns 401 | [ ] |
| 85 | Protected endpoint invalid token | Returns 401 | [ ] |
| 86 | Protected endpoint expired token | Returns 401 | [ ] |

### 3.3 Executive Endpoints
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 87 | `GET /api/v1/executive/morning-brief` | Returns brief with all sections | [ ] |
| 88 | `GET /api/v1/executive/key-risks` | Returns risk array with severity scores | [ ] |
| 89 | `GET /api/v1/executive/opportunities` | Returns opportunity array with ROI | [ ] |
| 90 | `GET /api/v1/executive/ai-coo-summary` | Returns AI COO recommendations | [ ] |
| 91 | `GET /api/v1/executive/metrics-snapshot` | Returns cross-domain metrics | [ ] |
| 92 | `GET /api/v1/executive/store-ranking` | Returns sorted store list | [ ] |

### 3.4 VOC Endpoints
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 93 | `GET /api/v1/voc/voices` | Returns paginated voice list | [ ] |
| 94 | `GET /api/v1/voc/voices?channel=google` | Filtered by channel | [ ] |
| 95 | `GET /api/v1/voc/voices?limit=10&offset=0` | Pagination works | [ ] |
| 96 | `GET /api/v1/voc/stats` | Returns channel distribution stats | [ ] |
| 97 | `GET /api/v1/voc/trends` | Returns sentiment trend data | [ ] |

### 3.5 CX Endpoints
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 98 | `GET /api/v1/cx/journeys` | Returns journey list | [ ] |
| 99 | `GET /api/v1/cx/touchpoints` | Returns touchpoint data | [ ] |
| 100 | `GET /api/v1/cx/diagnostics` | Returns diagnostic analysis | [ ] |

### 3.6 Brand Health Endpoints
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 101 | `GET /api/v1/brand/health` | Returns current brand health score | [ ] |
| 102 | `GET /api/v1/brand/health/history` | Returns historical health data | [ ] |
| 103 | `GET /api/v1/brand/stores` | Returns per-store health scores | [ ] |
| 104 | `GET /api/v1/brand/alerts` | Returns active alerts | [ ] |

### 3.7 Workflow & Knowledge
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 105 | `GET /api/v1/workflow/cases` | Returns paginated cases | [ ] |
| 106 | `POST /api/v1/workflow/cases` | Creates new case, returns 201 | [ ] |
| 107 | `GET /api/v1/knowledge/articles` | Returns knowledge articles | [ ] |
| 108 | `GET /api/v1/knowledge/search?q=term` | Returns semantic search results | [ ] |

### 3.8 Sandbox, Trends, Competitors, Operational
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 109 | `POST /api/v1/sandbox/analyze` | Returns NLP analysis result | [ ] |
| 110 | `GET /api/v1/trends/overview` | Returns trend overview | [ ] |
| 111 | `GET /api/v1/competitors` | Returns competitor list | [ ] |
| 112 | `GET /api/v1/competitors/{id}/swot` | Returns SWOT analysis | [ ] |
| 113 | `GET /api/v1/operational/correlations` | Returns data correlations | [ ] |
| 114 | `GET /api/v1/operational/metrics` | Returns operational metrics | [ ] |

### 3.9 Predictions & Learning
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 115 | `GET /api/v1/predictions/forecast` | Returns 7-day forecast | [ ] |
| 116 | `POST /api/v1/predictions/simulate` | Returns simulation projection | [ ] |
| 117 | `GET /api/v1/learning/cases` | Returns historical cases with similarity | [ ] |
| 118 | `GET /api/v1/learning/patterns` | Returns discovered patterns | [ ] |
| 119 | `POST /api/v1/learning/cases` | Stores new learning case | [ ] |

### 3.10 Store Intelligence
| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 120 | `GET /api/v1/stores/{id}/intelligence` | Returns daily intelligence | [ ] |
| 121 | `GET /api/v1/stores/{id}/trends` | Returns 14-day trend | [ ] |
| 122 | `GET /api/v1/stores/{id}/voices` | Returns store voice data | [ ] |

---

## 4. Docker Deployment Testing

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 123 | `docker compose up -d` | All 7 services start without error | [ ] |
| 124 | `docker compose ps` | All services show "healthy" or "running" | [ ] |
| 125 | Backend health check | `curl http://localhost:8000/api/v1/health` returns 200 | [ ] |
| 126 | Frontend accessible | Browser loads http://localhost:26117 | [ ] |
| 127 | Nginx proxy | http://localhost routes to frontend | [ ] |
| 128 | Service logs | `docker compose logs -f` shows no error loops | [ ] |
| 129 | PostgreSQL connection | Backend successfully connects to DB | [ ] |
| 130 | Redis connection | Celery worker connects to Redis broker | [ ] |
| 131 | `docker compose down` | All services stop and remove cleanly | [ ] |
| 132 | Volume persistence | Data survives `docker compose down && up -d` cycle | [ ] |
| 133 | Container restart | `docker compose restart backend` recovers cleanly | [ ] |

---

## 5. WebSocket Testing

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 134 | Connect to voice stream | WebSocket connects at `/ws/voice-stream/all` | [ ] |
| 135 | Receive voice messages | Demo messages arrive at intervals | [ ] |
| 136 | Connect to specific channel | `/ws/voice-stream/google` filters correctly | [ ] |
| 137 | Connect to alert stream | `/ws/alerts/{user_id}` connects | [ ] |
| 138 | Alert notification | Alert message triggers UI notification | [ ] |
| 139 | Disconnect handling | UI shows "disconnected" indicator | [ ] |
| 140 | Auto-reconnect | Client reconnects after network interruption | [ ] |
| 141 | Concurrent connections | Multiple browser tabs share connection properly | [ ] |
| 142 | Close connection | Clean disconnect, no server errors | [ ] |

---

## 6. Demo Data Testing

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 143 | `seed_demo_data.py` runs | Script completes without errors | [ ] |
| 144 | Orgs created | 3 demo organizations in database | [ ] |
| 145 | Users created | Admin user created with correct password | [ ] |
| 146 | Stores created | 10+ demo stores with location data | [ ] |
| 147 | VOC data seeded | Voice records spread across 6 channels | [ ] |
| 148 | CX journeys seeded | Journey records for multiple stores | [ ] |
| 149 | Brand health data | Health history with 30 days of data | [ ] |
| 150 | Workflow cases | 5-10 demo cases with timelines | [ ] |
| 151 | Knowledge articles | 10+ articles in knowledge base | [ ] |
| 152 | Competitor data | 3-5 competitors with metrics | [ ] |
| 153 | Store intelligence | Daily intelligence records per store | [ ] |
| 154 | Learning cases | Historical case records with patterns | [ ] |
| 155 | Operational data | POS/traffic/staffing records | [ ] |
| 156 | Demo login works | Login with demo credentials succeeds | [ ] |
| 157 | Dashboard shows data | All dashboard panels populated with demo data | [ ] |

---

## 7. Error State Testing

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 158 | 404 page | Navigating to unknown route shows friendly 404 | [ ] |
| 159 | 500 error | Server error shows generic error UI (not stack trace) | [ ] |
| 160 | Network down | API call failure shows "Connection error" message | [ ] |
| 161 | Timeout handling | Long requests timeout gracefully | [ ] |
| 162 | API returns null | Null data doesn't crash the UI | [ ] |
| 163 | API returns empty array | Empty arrays render "no data" states | [ ] |
| 164 | API returns malformed JSON | Parser error handled, error message shown | [ ] |
| 165 | Form validation errors | Inline error messages on invalid fields | [ ] |
| 166 | Auth token expired mid-session | Auto-redirect to login | [ ] |

---

## 8. Empty State Testing

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 167 | Empty VOC stream | "No voice data for selected channel" message | [ ] |
| 168 | Empty store ranking | "No stores configured" message | [ ] |
| 169 | Empty learning cases | "No historical cases found" message | [ ] |
| 170 | Empty search results | "No results matching your query" message | [ ] |
| 171 | Empty competitor list | "No competitors tracked" message | [ ] |
| 172 | Empty knowledge articles | "No articles available" message | [ ] |
| 173 | Empty workflow cases | "No active cases" message | [ ] |
| 174 | Empty executive brief | "Brief not yet generated" message | [ ] |

---

## 9. Loading State Testing

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 175 | Dashboard initial load | Skeleton/spinner shown while data fetches | [ ] |
| 176 | Store ranking load | Loading indicator in table before data | [ ] |
| 177 | Prediction chart load | Loading state with skeleton chart | [ ] |
| 178 | NLP analysis in progress | Spinner with "Analyzing..." text | [ ] |
| 179 | WebSocket connecting | "Connecting..." indicator shown | [ ] |
| 180 | Page transition | Smooth transition, no flash of unstyled content | [ ] |

---

## 10. Browser Compatibility

| # | Browser | Version | Status |
|---|---------|---------|--------|
| 181 | Chrome | Latest | [ ] |
| 182 | Firefox | Latest | [ ] |
| 183 | Edge | Latest | [ ] |
| 184 | Safari | Latest (if macOS available) | [ ] |

---

## 11. Mobile Responsiveness

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 185 | 1400px width | Full 3-column layout visible | [ ] |
| 186 | 1200px width | Two-column layout, side panels stack | [ ] |
| 187 | 768px width | Single column, all content vertical | [ ] |
| 188 | 480px width (mobile) | Single column, navigation collapses | [ ] |
| 189 | Touch targets | Buttons and links are tap-friendly (>48px) | [ ] |
| 190 | Horizontal scroll | No unwanted horizontal scroll at any width | [ ] |

---

## Test Results Summary

- **Total Test Cases:** 190
- **Passed:** ___ / 190
- **Failed:** ___ / 190
- **Blocked:** ___ / 190
- **Test Date:** _________
- **Tested By:** _________

---

**Last Updated:** 2026-06-29
