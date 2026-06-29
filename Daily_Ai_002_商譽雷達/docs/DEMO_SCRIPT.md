# Sentinel ECXIP — Demo Script (5-Minute Walkthrough)

> **Version:** 1.0.0 | **Date:** 2026-06-29 | **Duration:** ~5 minutes

---

## Demo Preparation Checklist

- [ ] Docker services running (`docker compose up -d`)
- [ ] Demo data seeded (`python backend/scripts/seed_demo_data.py`)
- [ ] Browser open at http://localhost:26117
- [ ] Logged in as admin@sentinel.ai / demo123
- [ ] Screen resolution set to 1920x1080 for full effect
- [ ] Both language switching tested beforehand

---

## Walkthrough

---

### 0:00 – 0:30 | Landing & First Impression

**What to show:**
- Open http://localhost:26117 in browser
- The Apple Frosted Glass UI loads — translucent panels, blurred backgrounds, subtle shadows
- Login page (if not already logged in): clean, minimalist, frosted glass card
- After login: Executive Dashboard loads

**What to say:**
> "This is Sentinel ECXIP — an enterprise AI platform for customer experience intelligence. Notice the Apple Frosted Glass design language: translucent cards, gaussian blur backdrops, consistent typography. This UI was built with vanilla CSS — no frameworks — using modern glassmorphism techniques. Every component follows the same design system."

**Key features to highlight:**
- Glassmorphism aesthetic (backdrop-blur, rgba backgrounds, border-radius)
- Clean, uncluttered layout
- Professional color palette (cool blues/greys)

---

### 0:30 – 1:00 | Executive Morning Brief — AI COO Summary

**What to show:**
- The Executive Briefing Center panel at the top of the dashboard
- Greeting header: "Good morning, COO" (or "早安, 營運長" in Chinese)
- 4-5 key metric cards: Brand Health, NPS, CSAT, Risk Score, Resolution Rate
- "Today's Biggest Problem" card highlighted in red/orange
- AI COO Recommendations section with 3-5 recommendations, each with a confidence bar
- Mini store ranking table (top 5 stores)

**What to say:**
> "Every morning at 6 AM, the platform generates an Executive Brief. This is the AI COO's daily digest — what matters *today*. You can see at-a-glance the top-level metrics, the single biggest problem requiring attention, and AI-generated strategic recommendations ranked by confidence. The affected stores are highlighted so you know exactly where to focus."

**Key features to highlight:**
- AI-generated summary (not just raw data)
- Confidence scoring on recommendations
- "Biggest Problem" callout (triage in one glance)
- Metric cards with trend arrows (up/down for direction)

---

### 1:00 – 1:30 | Store Ranking — Identify the Worst Store

**What to show:**
- Click "Store Ranking" in the left navigation (or scroll down)
- Full store ranking table with all stores
- Health score color bars (green > yellow > orange > red)
- Risk level tags (Critical, High, Medium, Low)
- Trend arrows showing 14-day direction
- Filter tabs: All / Critical / Improving / Declining
- Click a "Critical" store to expand its detail panel

**What to say:**
> "The Store Ranking view gives you a complete picture of every location. Each store gets a daily health score, color-coded from green to red. You can filter to see only critical stores, or stores that are improving vs. declining. Click any store to drill down — you'll see its VOC data, journey friction points, and historical trend. This is how operations managers prioritize field visits."

**Key features to highlight:**
- Color-coded health bars (instant visual scanning)
- Filterable tabs (data triage)
- Expandable detail panel (drill-down)
- Critical issues count per store

---

### 1:30 – 2:00 | VOC Stream & Journey Diagnostics (Drill Down)

**What to show:**
- In the expanded store detail: switch to "VOC" tab or navigate to Voice of Customer page
- Real-time voice stream across 6 channels (Google, Threads, Facebook, Instagram, Dcard, PTT)
- Sentiment badges: green (positive), yellow (neutral), red (negative)
- Click a specific voice item to see full AI analysis
- Switch to Customer Journey page: 6-stage funnel with color-coded health
- Touchpoints with friction markers

**What to say:**
> "Now let's drill into *why* a store is performing poorly. The Voice of Customer stream captures feedback from 6 channels — Google Reviews, social media, forums. Each item is analyzed for sentiment, emotion, topic, and risk. Meanwhile, the Customer Journey map shows exactly which touchpoints are causing friction. Notice the red nodes — these are the pain points driving negative sentiment."

**Key features to highlight:**
- Multi-channel aggregation (single pane of glass)
- AI-powered sentiment/emotion analysis
- Friction detection on journey map
- Channel filtering (isolate specific platforms)

---

### 2:00 – 2:30 | AI Brand Manager — Crisis Simulation

**What to show:**
- Navigate to "AI Brand Manager" in the left nav
- Terminal-style interface with scenario selector
- Select "食品衛生危機" (Food Safety Crisis) scenario
- Click "觸發危機分析" (Trigger Crisis Analysis)
- Terminal streams AI analysis line by line
- The AI identifies root cause, affected stores, severity level, and initial recommendations

**What to say:**
> "This is the AI Brand Manager — the command center for crisis response. Let's simulate a food safety crisis. The terminal streams real-time AI analysis: what happened, which stores are affected, the severity, and recommended first actions. This isn't just a dashboard — it's an active decision-support tool that helps brand managers respond in minutes, not hours."

**Key features to highlight:**
- Terminal-style streaming response (feels like an AI co-pilot)
- 3 pre-built crisis scenarios
- Real-time AI analysis (not just static text)
- Chinese + English response capability

---

### 2:30 – 3:00 | Root Cause → SOP → PR → Legal Pipeline

**What to show:**
- Tab navigation within AI Brand Manager:
  1. Root Cause tab: 5-Why analysis, Pareto chart, contributing factors
  2. SOP tab: Step-by-step checklist for resolution
  3. PR tab: Drafted public statement (Chinese version)
  4. Legal tab: Risk categories, compliance concerns, recommended actions
- Click "Copy" button on PR statement

**What to say:**
> "Now watch what happens after the AI identifies the crisis. It walks through four tabs: Root Cause analysis with 5-Why methodology and Pareto insights, a generated SOP checklist with specific action items, a drafted PR statement ready for review, and a legal risk assessment. This pipeline turns hours of manual work into seconds. You can copy the PR statement directly and send it to your comms team."

**Key features to highlight:**
- 5-Why root cause methodology
- Auto-generated SOP with actionable steps
- PR response in Chinese and English
- Legal risk categorization
- One-click copy for PR statements

---

### 3:00 – 3:30 | Predictive Intelligence — 7-Day Forecast

**What to show:**
- Navigate to "Predictive Intelligence"
- Four forecast panels: Brand Health, Risk Score, Negative Volume, Confidence
- 7-day bar/div charts with date labels
- Confidence percentages shown for each forecast
- Scroll to "What would happen if..." simulation input
- Type a scenario: "New store opening in Taipei" and click Simulate
- AI generates impact projection

**What to say:**
> "The platform doesn't just tell you what happened — it predicts what's coming. Four 7-day forecasts: Brand Health trajectory, Risk Score projection, Negative Sentiment Volume, and Confidence bands. Green means improving, red means watch out. And here's the what-if simulator: type in any scenario and the AI projects the impact on your forecast. This turns reactive management into proactive strategy."

**Key features to highlight:**
- Multi-factor forecasting (not just trend extrapolation)
- Confidence-weighted projections
- What-if simulation (interactive scenario planning)
- 7-day horizon (operational planning window)

---

### 3:30 – 4:00 | Learning Memory — Historical Case Matching

**What to show:**
- Navigate to "Learning Memory"
- Grid of historical cases with similarity percentages
- Cases sorted by relevance (80-94% match)
- Success/fail badges on each case
- "AI Pattern Insights" section showing discovered patterns
- "Store New Case" form at the bottom

**What to say:**
> "Here's where the platform gets smarter over time. The Learning Memory engine matches current situations against historical cases — showing you what happened before, what worked, and what didn't. With 80-94% similarity matching, you can see proven solutions. And the AI Pattern Discovery finds correlations humans might miss — like 'food complaints spike 3 days after supplier changes.' Every resolved case makes the platform smarter."

**Key features to highlight:**
- Similarity matching with percentages
- Success rate tracking (evidence-based decisions)
- AI pattern discovery (machine-found correlations)
- Continuous learning loop (store new cases)

---

### 4:00 – 4:30 | Language Switching — i18n Demo

**What to show:**
- Point to the language switcher in the top-right header: "繁中" (currently active)
- Click "EN" — entire interface instantly switches to English
- Navigate through 2-3 pages in English to show full coverage
- Show that navigation labels, metrics, buttons, tooltips all switch
- Click "繁中" to switch back
- Mention localStorage persistence

**What to say:**
> "One more thing — the platform is fully bilingual. With one click, the entire interface switches between Traditional Chinese and English — 260+ translation keys. Navigation, metrics, tooltips, chart labels, even AI-generated content titles — everything translates instantly, no page refresh. And the language preference is saved so teams across regions get their preferred language every time."

**Key features to highlight:**
- Instant switching (no page reload)
- 260+ translation keys (comprehensive coverage)
- localStorage persistence (survives sessions)
- Both static (data-i18n) and dynamic (I18n.t()) text

---

### 4:30 – 5:00 | Architecture Summary & Closing

**What to show:**
- Optional: switch to http://localhost:8000/docs to show Swagger API docs
- Optional: show `docker compose ps` in terminal to show running services
- If time: open http://localhost:8000/redoc for ReDoc
- Return to dashboard for closing

**What to say:**
> "Under the hood, Sentinel ECXIP runs on a modern microservices architecture. FastAPI backend with 60+ REST endpoints, PostgreSQL for persistence, Redis for caching and real-time WebSocket, Celery for async task processing with 12 scheduled jobs, all orchestrated with Docker Compose. 14 specialized AI agents work together through an orchestrator. And everything you've seen today runs in Demo Mode — simulated data, no external API dependencies required. 

> This is v1.0.0 — the Enterprise MVP release candidate. Production-ready architecture with enterprise features: multi-tenant data isolation, JWT authentication, role-based access, rate limiting, i18n, and a polished UI. Ready for demo, portfolio, and the next phase of development.

> Questions?"

**Key features to highlight:**
- Swagger/ReDoc (API documentation quality)
- Docker Compose (one-command deployment)
- 14 AI agents (scale of intelligence)
- Demo Mode (self-contained, no external dependencies)

---

## Quick Reference: Feature Map

| Time | Feature | Page |
|------|---------|------|
| 0:00 | UI Design | Dashboard |
| 0:30 | Executive Brief | Dashboard |
| 1:00 | Store Ranking | Store Ranking |
| 1:30 | VOC & Journey | VOC / Journey |
| 2:00 | Crisis Simulation | AI Brand Manager |
| 2:30 | Root Cause / SOP / PR | AI Brand Manager |
| 3:00 | 7-Day Forecast | Predictions |
| 3:30 | Learning Memory | Learning |
| 4:00 | i18n Switching | All Pages |
| 4:30 | Architecture | Swagger / Terminal |

---

## Troubleshooting During Demo

| Issue | Quick Fix |
|-------|-----------|
| Dashboard empty | Re-run `seed_demo_data.py`, refresh page |
| WebSocket not connecting | Check Redis is running: `docker compose ps redis` |
| AI Terminal not responding | Restart backend: `docker compose restart backend` |
| Language not switching | Check browser console for JS errors, clear localStorage |
| Docker containers failing | `docker compose down -v && docker compose up -d` |
| API returns 500 | Check `docker compose logs backend` for errors |

---

**Demo Script Version:** 1.0.0  
**Last Updated:** 2026-06-29
