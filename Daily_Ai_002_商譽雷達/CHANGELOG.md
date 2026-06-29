# Changelog

All notable changes to Sentinel AI ECXIP will be documented in this file.

**Status: Enterprise MVP v1.0.0 — Feature Freeze**

---

## [1.0.0] — 2026-06-29 (Enterprise MVP Release Candidate)

### Final Polish

- **System Health Check Center** — Health endpoint with DB/Redis status, version reporting, and Docker health checks
- **Demo Mode / Production Mode** — Configurable via `DEMO_MODE` env var; simulated data in demo, real services in production
- **Sample Data Seeder** — `scripts/seed_demo_data.py` populates all 7 domains with realistic demo data
- **Portfolio-Ready README** — Complete project overview with architecture diagram, feature table, quick start, and documentation index
- **Release Notes** — `RELEASE_NOTES_v1.0.0.md` with what's included, known limitations, and next roadmap
- **Security Checklist** — `docs/SECURITY_CHECKLIST.md` covering JWT, bcrypt, CORS, rate limiting, SQL injection, XSS, CSRF, secrets management, WebSocket security, multi-tenant isolation, and audit logging
- **Testing Checklist** — `docs/TESTING_CHECKLIST.md` with 190 manual test cases across frontend, API, Docker, i18n, WebSocket, error states, empty states, loading states, browser compatibility, and mobile responsiveness
- **Demo Script** — `docs/DEMO_SCRIPT.md` with 5-minute walkthrough, timed segments, talking points, and troubleshooting guide
- **Version Freeze** — `PROJECT_VERSION = "1.0.0"` set in `backend/core/config.py`; feature freeze marker in CHANGELOG

---

## [3.1.0] — 2026-06-29 (Phase 3.1 i18n)

### Added

- **i18n Internationalization Framework** (`frontend/i18n/`)
  - `i18n/index.js` — I18n engine with `t()` function, dot-notation key lookup, `{{param}}` interpolation, localStorage persistence, and locale change events
  - `i18n/zh-TW.js` — 260+ Traditional Chinese translation keys
  - `i18n/en-US.js` — 260+ English translation keys
  - `i18n/I18N_GUIDE.md` — Complete internationalization guide with best practices

- **Language Switcher** — Toggle button in header (繁中 / EN), instant UI update, localStorage persistence

- **data-i18n Attribute System**
  - 124 `data-i18n` attributes in index.html for static text
  - 6 `data-i18n-placeholder` attributes for input placeholders
  - 4 `data-i18n-title` attributes for tooltip text
  - Automatic fallback: HTML content serves as default text if i18n fails

- **Component i18n Integration** — All components updated to use `I18n.t()` for dynamic text across all 8 pages

- **Documentation**
  - `docs/I18N_GUIDE.md` — How to add languages, add keys, switch languages, fallback rules
  - `docs/FRONTEND_ARCHITECTURE.md` — Frontend architecture with i18n integration

---

## [3.0.0] — 2026-06-29 (Phase 3 Enterprise Intelligence)

### Added

- **5 New Intelligence Engines:**
  - Operational Intelligence Engine — Real-time operational data correlation (30-min refresh)
  - Predictive Intelligence Engine — 7-day multi-factor forecasting with confidence-weighted projections
  - Store Intelligence Engine — Per-store daily intelligence calculation with 14-day trend analysis
  - Learning Memory Engine — AI pattern discovery with similarity matching (80-94%)
  - Executive Intelligence Center — Enhanced morning brief with AI COO analysis

- **4 Enhanced/New Frontend Components:**
  - Executive Briefing Center (enhanced) — Greeting, key metrics, biggest problem card, AI COO recommendations, store ranking mini-table, risk forecast sparklines
  - Store Ranking Table (new) — Full ranking with health color bars, risk tags, filterable tabs, expandable detail panel
  - 7-Day Prediction Center (new) — Four forecast panels with div bar charts, what-if simulation engine
  - AI Learning Memory Panel (new) — Historical cases, similarity matching, success tracking, pattern discovery

- **6 New Celery Scheduled Tasks:**
  - `daily_store_intelligence_calculation` — Daily 3 AM
  - `daily_executive_brief_generation` — Daily 6 AM
  - `hourly_risk_forecast` — Hourly at :00
  - `daily_learning_pattern_update` — Daily 4 AM
  - `operational_data_correlation_job` — Every 30 minutes
  - `weekly_prediction_model_training` — Weekly Monday 2 AM

- **5 New API Endpoints:** Key risks, opportunities, AI COO summary, metrics snapshot, enhanced morning brief

- **New Schemas:** KeyRiskItem, OpportunityItem, AICOOSummaryItem, MetricsSnapshotResponse, updated MorningBriefResponse, ExecutiveRecommendation, StoreRankingItem

- **CSS Additions:** 500+ lines of glassmorphism styles for all new sections with responsive breakpoints at 1400px, 1200px, 768px

### Changed

- Frontend navigation reorganized to 8 items
- API service added 4 new executive methods
- Dashboard store added storeRankings, predictions, learningCases state
- Celery app added 6 new beat schedule entries

---

## [2.0.0] — 2026-06-29 (Phase 2 Enterprise SaaS)

### Added

- **Enterprise Backend** — FastAPI + PostgreSQL 16 + Redis 7 + Celery
- **11 API route modules** with 50+ endpoints across Auth, VOC, CX, Brand Health, Root Cause, Executive, Sandbox, Workflow, Knowledge, Trends, Competitors
- **9 AI Specialized Agents** with orchestrator: RiskAgent, VOCAgent, CXAgent, PRAgent, LegalAgent, KnowledgeAgent, ExecutiveAgent, TrendAgent, CompetitorAgent
- **AI Router** — 5-tier model selection (FLASH, PRO, GPT, REASONING, DEEP_RESEARCH) with cost optimization
- **Agent Orchestrator** — 10 predefined pipelines (crisis_response, daily_brief, weekly_report, etc.)
- **24 Database models** across 7 domains: Organization (7), VOC (3), CX (3), Brand (3), Workflow (3), Knowledge (2), Competitor (3)
- **Pydantic v2 schemas** with full validation for all request/response models
- **Docker Compose** — 7 services (backend, celery_worker, celery_beat, frontend, nginx, postgres, redis)
- **Celery Task System** — 4 queues (ingestion, analysis, notifications, reports) with 7 beat scheduled tasks
- **WebSocket** — Real-time voice streaming and alert notifications
- **Brand Health Engine** — Daily recalculation of brand/store health scores
- **Root Cause Engine** — 5-Why analysis, Pareto charts, cross-store comparison
- **Executive Dashboard** — AI-generated morning brief, store rankings, risk summary
- **Trend Intelligence** — Multi-period overview, emotion time-series, predictive forecasting
- **Competitor Intelligence** — Metrics comparison, benchmarking, SWOT analysis
- **Knowledge Base (RAG)** — Versioned articles and semantic search
- **Enterprise Workflow** — Case management, timeline audit trail, file attachments
- **Notification Service** — Multi-channel alert dispatch
- **Alembic migrations** — Version-controlled schema management

### Changed

- Frontend restructured from monolithic to modular component architecture with API-driven data
- API-driven architecture replacing hardcoded mock data
- Multi-tenant support added at database level (Organization model scoping)
- Build system moved to Docker Compose for reproducible deployment

---

## [1.1.0] — 2026-06-29 (Phase 1 MVP)

### Added

- **Apple Frosted Glass UI** — High-fidelity SPA with glassmorphism design system
- **Brand Cockpit Dashboard** — Real-time brand health score, store health index, CSAT, crisis resolution rate, reputation risk score
- **Voice Stream** — Simulated real-time customer review stream across 6 channels (Google Reviews, Threads, Facebook, Instagram, PTT, Dcard)
- **Customer Journey Map** — Visualized 6-stage customer journey with friction detection and store-level filtering
- **AI Brand Manager Terminal** — Virtual terminal with 3 crisis simulation scenarios, root cause analysis, SOP generation, PR statements, legal advisory
- **NLP Sandbox** — Interactive text analysis playground with sentiment, emotion, touchpoint classification, risk scoring, PR drafts, SOP suggestions
- **Dynamic Indicators** — Real-time metric fluctuation based on simulated events
- **Project documentation** — Vision, mission, product positioning, and Phase 2 roadmap
