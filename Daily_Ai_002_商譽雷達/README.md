# Sentinel AI — Enterprise Customer Experience Intelligence Platform (ECXIP)

**AI-Powered Platform for Voice of Customer, Customer Experience, Brand Intelligence & Reputation Management**

---

## Project Overview

Sentinel AI ECXIP is an enterprise-grade platform that transforms how organizations understand, measure, and improve their customer experience. By integrating AI agent technology with multi-channel voice analytics, the platform provides continuous monitoring, deep analysis, and actionable recommendations.

The platform answers questions traditional monitoring tools cannot:
- Why did this happen?
- Which locations need immediate attention?
- What processes are causing customer churn?
- What should we do next?
- Has the issue been resolved?
- Will a brand crisis occur in the near future?

---

## Phase 2 Architecture Highlights

- **9 AI Specialized Agents** coordinated by an AgentOrchestrator for crisis response, daily briefs, and weekly reports
- **AI Router** with 5-tier model selection optimizing for cost, latency, and quality
- **24 Database Tables** across 7 bounded domains (Organization, VOC, CX, Brand, Workflow, Knowledge, Competitor)
- **50+ API Endpoints** across 11 route modules with full Pydantic validation
- **Real-time WebSocket** voice streaming and alert notifications
- **Celery Task System** with 4 dedicated queues and 7 scheduled beat tasks
- **Docker Multi-Service** deployment with health checks and persistent volumes

## Phase 3: Enterprise Intelligence Platform (New!)

### 5 New Intelligence Engines

- **Operational Intelligence Engine** — Real-time operational data correlation, 30-min refresh cycle identifying hidden relationships between wait times, staffing levels, and NPS/CX metrics
- **Predictive Intelligence Engine** — 7-day multi-factor forecasting for brand health, risk scores, and negative sentiment volumes using historical pattern analysis and confidence-weighted projections
- **Store Intelligence Engine** — Per-store daily intelligence calculation with 14-day trend analysis, voice volume correlation, and automated health scoring with color-coded risk categorization
- **Learning Memory Engine** — AI pattern discovery across historical cases with similarity matching (80-94%), success rate tracking for past solutions, and "what worked before" knowledge graph
- **Executive Intelligence Center** — Enhanced morning brief with AI COO analysis, operational correlations, 7-day predictions, strategic recommendations with confidence scoring, and real-time metrics snapshot across all 7 domains

### Enhanced Executive Dashboard

- **Executive Briefing Center** — Greeting header, key metrics row, "Today's Biggest Problem" highlight card, affected stores list, AI COO recommendations with confidence bars, store ranking mini-table (top 5), and 7-day risk forecast sparklines
- **Store Ranking Table** — Full store ranking with health score color bars, risk level tags, trend arrows, critical issues count, filterable tabs (All/Critical/Improving/Declining), and click-to-expand store detail panel
- **7-Day Prediction Center** — Four forecast panels (Brand Health, Risk Score, Negative Volume, Confidence) with ASCII/div bar charts, "What would happen if..." simulation input with AI-generated impact projections
- **AI Learning Memory Panel** — Historical similar cases with similarity matching, success rate tracking for past strategies, AI-discovered pattern insights, and "Store New Case" form for continuous learning

### 6 New Celery Scheduled Tasks

| Task | Schedule | Queue | Description |
|------|----------|-------|-------------|
| daily_store_intelligence_calculation | Daily 3 AM | analysis | Calculate StoreDailyIntelligence for all stores |
| daily_executive_brief_generation | Daily 6 AM | analysis | Generate morning brief for all organizations |
| hourly_risk_forecast | Hourly at :00 | analysis | Update risk predictions every hour |
| daily_learning_pattern_update | Daily 4 AM | analysis | Discover new learning patterns |
| operational_data_correlation_job | Every 30 min | analysis | Update operational correlations |
| weekly_prediction_model_training | Mon 2 AM | analysis | Train/retrain prediction models |

### 5 New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/executive/morning-brief` | GET | Enhanced morning brief with AI COO analysis, operational correlations, 7-day predictions |
| `/api/v1/executive/key-risks` | GET | Key business risks with severity, impact, financial exposure, and mitigation |
| `/api/v1/executive/opportunities` | GET | Business improvement opportunities with ROI estimates |
| `/api/v1/executive/ai-coo-summary` | GET | AI COO strategic recommendations with domain summaries |
| `/api/v1/executive/metrics-snapshot` | GET | Real-time snapshot of all metrics across 7 domains |

### 4 New Frontend Components

| Component | File | Description |
|-----------|------|-------------|
| MorningBrief (Enhanced) | `executive/morningBrief.js` | Executive briefing center with all new features |
| StoreRanking | `executive/storeRanking.js` | Full store ranking table with tabs and detail panel |
| PredictionPanel | `executive/predictionPanel.js` | 7-day forecast panels and simulation engine |
| LearningPanel | `executive/learningPanel.js` | Historical cases, success patterns, and learning form |

---

## Quick Start

### Docker (Recommended)
```powershell
# Clone and navigate
Set-Location "D:\Ai study\Aisa_AI\Daily_Ai_002_商譽雷達"

# Configure environment
Copy-Item backend\.env.example backend\.env
# Edit backend\.env and set SECRET_KEY, API keys

# Start all services
docker compose -f docker\docker-compose.yml up -d
```

Access at **http://localhost** — Dashboard, Docs, and API.

### Local Development
```powershell
# Start infrastructure
docker compose -f docker\docker-compose.yml up -d postgres redis

# Setup Python
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start dev server
uvicorn main:app --reload --port 8000
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla JS, CSS3 (Apple Frosted Glass UI) |
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Async Tasks | Celery 5.4 |
| AI | OpenAI / Google Gemini |
| Proxy | Nginx 1.27 |
| Deployment | Docker + Docker Compose |
| Migrations | Alembic |
| Auth | JWT + OAuth2 (python-jose, passlib) |

---

## Project Structure

```
├── index.html                  # SPA dashboard (Frosted Glass UI)
├── index.css                   # Global styles
├── app.js                      # Core frontend logic
│
├── backend/                    # FastAPI application
│   ├── main.py                 # Entry point, WebSocket manager
│   ├── core/                   # Config, database, Redis, security
│   ├── models/                 # 24 SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── api/v1/                 # 11 API route modules
│   ├── services/               # Business logic + 9 AI agents
│   ├── tasks/                  # Celery async task definitions
│   └── alembic/                # Database migrations
│
├── docker/                     # Docker Compose + Dockerfiles
├── docs/                       # Full documentation
│   ├── architecture.md
│   ├── api/api-reference.md
│   ├── database_schema.md
│   ├── ai-agents.md
│   ├── deployment.md
│   └── diagrams/
│
├── CHANGELOG.md
├── ROADMAP.md
└── README.md
```

---

## API Documentation

Interactive API docs available at runtime:

- **Swagger UI:** http://localhost/docs
- **ReDoc:** http://localhost/redoc

Static reference: [docs/api/api-reference.md](docs/api/api-reference.md)

**Base URL:** `/api/v1` | **Auth:** Bearer JWT

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | 7 | Login, refresh, user CRUD, role management |
| VOC | 6 | Voice ingest, list, stats, trends, delete |
| CX | 6 | Journeys, touchpoints, diagnostics, insights |
| Brand Health | 6 | Current, history, stores, alerts CRUD |
| Root Cause | 5 | Analysis CRUD, summary, store comparison |
| Executive | 4 | Morning brief, today summary, rankings, risk |
| Sandbox | 1 | NLP analysis pipeline |
| Workflow | 6 | Cases CRUD, comments, attachments, stats |
| Knowledge | 6 | Articles CRUD, semantic search |
| Trends | 4 | Overview, topics, emotions, predictions |
| Competitors | 5 | CRUD, metrics, benchmark, SWOT |

---

## Development Guide

### Prerequisites
- Python 3.12+
- Docker 24.0+
- PostgreSQL 16
- Redis 7

### First-Time Setup
```powershell
# Install dependencies
Set-Location backend
pip install -r requirements.txt

# Create database
createdb sentinel_ecxip

# Run migrations
alembic upgrade head

# Start Celery worker (separate terminal)
celery -A tasks.celery_app worker --loglevel=info
```

### Code Quality
- All API endpoints use Pydantic v2 schemas for validation
- Services follow Clean Architecture with dependency injection
- AI agents extend `BaseAgent` with consistent interface
- Celery tasks are idempotent with soft time limits

### Adding Features
1. Define model in `backend/models/`
2. Create schema in `backend/schemas/`
3. Implement service in `backend/services/`
4. Add router in `backend/api/v1/`
5. Register route in `backend/api/v1/router.py`
6. Generate migration: `alembic revision --autogenerate -m "description"`

### Running Tests
```powershell
# API health check
Invoke-WebRequest http://localhost:8000/api/v1/health
```

---

## License

Proprietary — All rights reserved.
