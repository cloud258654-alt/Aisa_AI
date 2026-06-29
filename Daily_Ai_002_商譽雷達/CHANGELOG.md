# Changelog

All notable changes to Sentinel AI ECXIP will be documented in this file.

---

## [3.0.0] — 2026-06-29

### Phase 3 Enterprise Intelligence Platform

#### Added

- **5 New Intelligence Engines:**
  - Operational Intelligence Engine — Real-time operational data correlation (30-min refresh), identifying hidden relationships between wait times, staffing, and NPS/CX
  - Predictive Intelligence Engine — 7-day multi-factor forecasting for brand health, risk scores, and negative sentiment volumes with confidence-weighted projections
  - Store Intelligence Engine — Per-store daily intelligence calculation with 14-day trend analysis, voice volume correlation, and automated health scoring
  - Learning Memory Engine — AI pattern discovery across historical cases with similarity matching (80-94%), success rate tracking, and "what worked before" knowledge graph
  - Executive Intelligence Center — Enhanced morning brief with AI COO analysis, operational correlations, 7-day predictions, and strategic recommendations

- **Enhanced Executive Dashboard with 4 Components:**
  - Executive Briefing Center (`morningBrief.js` enhanced) — Greeting header with date, key metrics row, "Today's Biggest Problem" card, AI COO recommendations with confidence bars, store ranking mini-table (top 5), 7-day risk forecast sparklines
  - Store Ranking Table (`storeRanking.js` new) — Full ranking with health score color bars, risk level tags, trend arrows, filterable tabs (All/Critical/Improving/Declining), click-to-expand store detail panel
  - 7-Day Prediction Center (`predictionPanel.js` new) — Four forecast panels with div bar charts, "What would happen if..." simulation input with AI impact projections
  - AI Learning Memory Panel (`learningPanel.js` new) — Historical similar cases with similarity matching, success rate tracking, AI-discovered patterns, "Store New Case" form

- **6 New Celery Scheduled Tasks:**
  - `daily_store_intelligence_calculation` — Daily at 3 AM, calculates StoreDailyIntelligence for all stores
  - `daily_executive_brief_generation` — Daily at 6 AM, generates morning brief for all organizations
  - `hourly_risk_forecast` — Every hour at :00, updates risk predictions
  - `daily_learning_pattern_update` — Daily at 4 AM, discovers new learning patterns
  - `operational_data_correlation_job` — Every 30 minutes, updates operational correlations
  - `weekly_prediction_model_training` — Weekly Monday 2 AM, trains/retrains prediction models

- **5 New API Endpoints:**
  - `GET /api/v1/executive/morning-brief` — Enhanced with AI COO analysis, operational correlations, 7-day predictions
  - `GET /api/v1/executive/key-risks` — Key business risks with severity, impact, financial exposure, and mitigation
  - `GET /api/v1/executive/opportunities` — Business improvement opportunities with ROI estimates
  - `GET /api/v1/executive/ai-coo-summary` — AI COO strategic recommendations with domain summaries
  - `GET /api/v1/executive/metrics-snapshot` — Real-time snapshot of all metrics across 7 domains

- **New Schemas:**
  - `KeyRiskItem`, `KeyRisksResponse` — Risk assessment models
  - `OpportunityItem`, `OpportunitiesResponse` — Opportunity detection models
  - `AICOOSummaryItem`, `AICOOSummaryResponse` — AI COO summary models
  - `MetricsSnapshotResponse` — Cross-domain metrics snapshot model
  - Updated `MorningBriefResponse` with `ai_coo_analysis`, `operational_correlations`, `predictions_7day`
  - Updated `ExecutiveRecommendation` with `expected_outcome` and `confidence`
  - Updated `StoreRankingItem` with `critical_issues`

- **CSS Additions:**
  - 500+ lines of new glassmorphism styles for executive brief, store ranking, prediction charts, and learning panel
  - Full responsive design with breakpoints at 1400px, 1200px, and 768px for all new sections

- **Documentation:**
  - Updated `README.md` with Phase 3 section describing 5 new intelligence engines and enhanced dashboard
  - Updated `CHANGELOG.md` with v3.0.0 entry
  - Updated `ROADMAP.md` with Phase 3 completion markers
  - Updated `docs/architecture.md` with Phase 3 modules in architecture diagram
  - Created `docs/PHASE3_ENTERPRISE_INTELLIGENCE.md` with complete Phase 3 documentation

#### Changed

- **Frontend Navigation** — Reorganized with 8 nav items including new Store Ranking, Predictions, and Learning sections
- **API Service** — Added 4 new executive API methods (`getKeyRisks`, `getOpportunities`, `getAICooSummary`, `getMetricsSnapshot`)
- **Dashboard Store** — Added `storeRankings`, `predictions`, `learningCases` state fields
- **Celery App** — Added 6 new beat schedule entries and `phase3_tasks` module to imports, routes, and includes

---

## [2.0.0] — 2026-06-29

### Phase 2 Enterprise Refactoring

#### Added

- **Enterprise Backend** (FastAPI + PostgreSQL + Redis + Celery)
- **11 API modules** with 50+ endpoints:
  - Auth (login, refresh, user/role management)
  - VOC (voice ingestion, stats, trends)
  - CX (journeys, touchpoints, diagnostics)
  - Brand Health (current, history, alerts)
  - Root Cause (analysis, summary, store comparison)
  - Executive (morning brief, today summary, rankings, risk)
  - NLP Sandbox (text analysis pipeline)
  - Workflow (case management, comments, attachments)
  - Knowledge Base (articles, semantic search)
  - Trend Intelligence (overview, topics, emotions, predictions)
  - Competitor Intelligence (tracking, metrics, benchmark, SWOT)
- **9 AI specialized agents** with orchestrator:
  - RiskAgent — Brand risk detection, scoring, escalation
  - VOCAgent — Voice of Customer deep analysis
  - CXAgent — Customer Experience analysis
  - PRAgent — PR response generation
  - LegalAgent — Legal compliance advisory
  - KnowledgeAgent — Knowledge extraction & RAG
  - ExecutiveAgent — Executive summary compilation
  - TrendAgent — Trend analysis & forecasting
  - CompetitorAgent — Competitive intelligence
- **AI Router** for 5-tier model selection (FLASH, PRO, GPT, REASONING, DEEP_RESEARCH) with cost optimization
- **Agent Orchestrator** with 10 predefined pipelines (crisis_response, daily_brief, weekly_report, etc.)
- **24 database models** across 7 domains:
  - Organization (7 tables): Organization, Department, Region, Store, User, Role, UserRole
  - VOC (3 tables): VoiceSource, VoiceAnalysis, VoiceTag
  - CX (3 tables): CXJourney, TouchPoint, CXInsight
  - Brand (3 tables): BrandHealth, StoreHealth, BrandAlert
  - Workflow (3 tables): Case, CaseTimeline, CaseAttachment
  - Knowledge (2 tables): KnowledgeBase, KnowledgeVersion
  - Competitor (3 tables): Competitor, CompetitorMetric, CompetitorSWOT
- **Pydantic schemas** with full validation for all request/response models
- **Docker multi-service deployment** with 7 containers (backend, celery_worker, celery_beat, frontend, nginx, postgres, redis)
- **Celery async task system** with 4 dedicated queues:
  - ingestion — Social media crawler tasks (every 15 min)
  - analysis — AI analysis, brand health, risk alerts, daily brief, weekly report
  - notifications — Email and push dispatch
  - reports — Scheduled report generation
- **7 Celery beat scheduled tasks**: recurring crawl, voice analysis, risk alerts, daily brand health, daily brief, weekly report, data cleanup
- **WebSocket real-time** voice streaming (`/ws/voice-stream/{channel}`) and alert notifications (`/ws/alerts/{user_id}`)
- **Executive Dashboard** with AI-generated morning brief, store rankings, risk summary
- **Trend Intelligence** with multi-period overview, emotion time-series, predictive forecasting
- **Competitor Intelligence** with metrics comparison, benchmarking, SWOT analysis
- **Knowledge Base (RAG)** system with versioned articles and semantic search
- **Enterprise Workflow** with case management, timeline audit trail, file attachments
- **Root Cause Engine** with 5-Why analysis, Pareto charts, cross-store comparison
- **Brand Health Engine** with daily recalculation of brand/store health scores
- **Notification Service** for multi-channel alert dispatch
- **Alembic migrations** for version-controlled schema management
- **Comprehensive documentation** (architecture, API reference, database schema, AI agents, deployment guide, roadmap)

#### Changed

- **Frontend restructured** from 3 monolithic files (`index.html` + `index.css` + `app.js`) to modular component architecture with API-driven data
- **API-driven architecture** replacing hardcoded mock data in `app.js` with real REST/WebSocket backend
- **Multi-tenant support** added at database level (Organization model scoping all tables)
- **Build system** moved to Docker Compose for reproducible deployment
- **README** updated with comprehensive Phase 2 architecture documentation

---

## [1.1.0] — 2026-06-29

### Phase 1 MVP

#### Added

- **Apple Frosted Glass UI** — High-fidelity SPA with glass-morphism design system
- **Brand Cockpit Dashboard** — Real-time brand health score, store health index, CSAT, crisis resolution rate, reputation risk score
- **Voice Stream** — Simulated real-time customer review stream across 6 channels (Google Reviews, Threads, Facebook, Instagram, PTT, Dcard)
- **Customer Journey Map** — Visualized 6-stage customer journey with friction detection and store-level filtering
- **AI Brand Manager Terminal** — Virtual terminal with 3 crisis simulation scenarios, root cause analysis, SOP generation, PR statements, legal advisory
- **NLP Sandbox** — Interactive text analysis playground with sentiment, emotion, touchpoint classification, risk scoring, PR drafts, SOP suggestions
- **Dynamic Indicators** — Real-time metric fluctuation based on simulated events
- **Project documentation** — Vision, mission, product positioning, and Phase 2 roadmap
