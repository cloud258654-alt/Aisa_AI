# Sentinel AI — Enterprise Customer Experience Intelligence Platform (ECXIP)

> **一句話介紹：** Sentinel ECXIP 是一套整合 VOC、CX、Brand Intelligence、AI Agent、Operational Intelligence 與 Executive Decision Support 的企業級 AI 平台。

> **In a Sentence:** Sentinel ECXIP is an enterprise AI platform that unifies Voice of Customer, Customer Experience, Brand Intelligence, 14 AI agents, Operational Intelligence, and Executive Decision Support into a single command center.

---

## 🎯 Portfolio Summary

Sentinel ECXIP is an enterprise-grade AI platform that transforms how organizations understand, measure, and improve their customer experience. By integrating 14 AI agents with multi-channel voice analytics across 6 bounded domains, the platform provides continuous monitoring, deep root cause analysis, predictive intelligence, and actionable executive recommendations.

Built with an Enterprise SaaS architecture from day one, the platform features multi-tenant support, Docker-based deployment, comprehensive i18n (zh-TW + en-US), and a polished Apple Frosted Glass UI.

---

## ✨ Key Features

| Module | Description |
|--------|-------------|
| 🏠 Executive Briefing | AI COO morning brief with daily summary, risks, store ranking, and predictions |
| 📊 Brand Cockpit | Real-time brand health, store health, CSAT, crisis resolution, and reputation risk |
| 🎤 Voice of Customer | Multi-channel voice stream (Google, Threads, Facebook, Instagram, Dcard, PTT) |
| 🗺️ Customer Journey | Touchpoint diagnostic map with friction detection and AI root cause analysis |
| 🧠 AI Brand Manager | Crisis simulation, SOP generation, PR statement drafting, legal advisory |
| 🔬 NLP Sandbox | Real-time text analysis with sentiment, emotion, touchpoint, and risk scoring |
| 📈 Predictive Intelligence | 7-day brand health, risk, and sentiment forecasting with what-if simulation |
| 🏪 Store Intelligence | Per-store daily health scoring, ranking, and trend analysis |
| 📚 Learning Memory | Historical case matching, pattern discovery, and resolution recommendation |
| ⚙️ Operational Intelligence | POS, traffic, and staffing data correlation with VOC events |
| 🌐 i18n | Full Traditional Chinese (zh-TW) and English (en-US) support, instant switching |
| 🔒 Enterprise Ready | JWT auth, role-based access, rate limiting, multi-tenant architecture |

---

## 🏗️ Architecture

```
Frontend (Vanilla JS SPA)
    ↓
Nginx Reverse Proxy
    ↓
FastAPI Backend (REST + WebSocket)
    ↓
┌──────────┬──────────┬──────────┬──────────┐
│ VOC      │ CX       │ Brand    │ Workflow │
│ Service  │ Service  │ Health   │ Service  │
├──────────┼──────────┼──────────┼──────────┤
│ 14 AI Agents + Orchestrator + AI Router    │
├──────────┼──────────┼──────────┼──────────┤
│ PostgreSQL │  Redis  │ Celery   │ WebSocket│
└──────────┴──────────┴──────────┴──────────┘
```

**Tech Stack:** FastAPI · PostgreSQL 16 · Redis 7 · Celery · Docker · Vanilla JS · CSS3 Glassmorphism

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Python 3.12+ (for local dev)

### Docker (Recommended)
```bash
cd docker
docker compose up -d
```

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py
# → http://localhost:8000

# Frontend
cd frontend
python -m http.server 26117
# → http://localhost:26117

# Generate Demo Data (optional)
cd backend
python scripts/seed_demo_data.py
```

### Demo Credentials
- **Email:** admin@sentinel.ai
- **Password:** demo123

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Demo Mode
The platform runs in **Demo Mode** by default — all data is simulated. Set `DEMO_MODE=false` in `.env` to connect real services.

---

## 📁 Project Structure

```
Daily_Ai_002_商譽雷達/
├── frontend/          # Vanilla JS SPA (Apple Frosted Glass UI)
│   ├── i18n/          # zh-TW + en-US translations (260+ keys)
│   └── src/           # Components, services, stores, styles
├── backend/           # FastAPI application
│   ├── api/v1/        # 15 route modules (60+ endpoints)
│   ├── models/        # 31 SQLAlchemy ORM models (7 domains)
│   ├── schemas/       # Pydantic v2 validation schemas
│   ├── services/      # 17 business services
│   │   └── agents/    # 14 AI agents + orchestrator
│   ├── tasks/         # Celery async tasks (12 scheduled)
│   └── scripts/       # Demo data seeder
├── docker/            # Docker Compose (7 services)
└── docs/              # Architecture, API, DB schema, guides
```

---

## 🤖 AI Agent Architecture

14 specialized AI agents coordinated by an AgentOrchestrator:

| Agent | Role |
|-------|------|
| RiskAgent | Early warning detection, crisis escalation |
| VOCAgent | Voice sentiment, emotion, topic analysis |
| CXAgent | Customer journey friction detection |
| PRAgent | PR response generation (Chinese/English) |
| LegalAgent | Legal risk assessment, compliance |
| KnowledgeAgent | SOP/case knowledge retrieval |
| ExecutiveAgent | Executive summary generation |
| TrendAgent | Trend analysis and anomaly detection |
| CompetitorAgent | Competitive intelligence, SWOT |
| OperationalAgent | Operational data correlation |
| PredictionAgent | 7-day multi-factor forecasting |
| StoreIntelligenceAgent | Per-store health analysis |
| LearningAgent | Historical pattern matching |
| AICOOAgent | COO-level strategic recommendations |

---

## 📚 Documentation

| Document | Path |
|----------|------|
| Architecture | `docs/architecture.md` |
| API Reference | `docs/api/api-reference.md` |
| Database Schema | `docs/database_schema.md` |
| AI Agents | `docs/ai-agents.md` |
| I18n Guide | `docs/I18N_GUIDE.md` |
| Frontend Architecture | `docs/FRONTEND_ARCHITECTURE.md` |
| Deployment | `docs/deployment.md` |
| Security Checklist | `docs/SECURITY_CHECKLIST.md` |
| Testing Checklist | `docs/TESTING_CHECKLIST.md` |
| Demo Script | `docs/DEMO_SCRIPT.md` |
| Release Notes | `RELEASE_NOTES_v1.0.0.md` |
| Changelog | `CHANGELOG.md` |
| Roadmap | `ROADMAP.md` |

---

## 🗺️ Roadmap

- ✅ **Phase 1:** MVP — Brand monitoring & AI analysis
- ✅ **Phase 2:** Enterprise SaaS — Microservices, AI agents, Docker
- ✅ **Phase 3:** Intelligence Platform — 5 new engines, 5 new agents
- ✅ **Phase 3.1:** i18n — Chinese/English UI, language switcher
- ✅ **v1.0.0:** Enterprise MVP Release Candidate

---

## 📄 License

Proprietary. All rights reserved.

---

**Version:** 1.0.0  
**Status:** Enterprise MVP Release Candidate  
**Last Updated:** 2026-06-29
