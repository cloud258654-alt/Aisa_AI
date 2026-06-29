# Sentinel ECXIP — Release Notes v1.0.0

## Enterprise MVP Release Candidate

**Version:** 1.0.0  
**Release Date:** 2026-06-29  
**Status:** Enterprise MVP — Ready for Demo & Portfolio

---

## What's Included

### Core Platform
- FastAPI backend with 60+ REST endpoints and WebSocket
- PostgreSQL 16 with 31 tables across 7 domains
- Redis 7 for caching, queues, and WebSocket pub/sub
- Celery with 12 scheduled tasks across 4 queues
- Docker Compose with 7 services
- JWT authentication with role-based access control

### AI Capabilities
- 14 specialized AI agents with rule-based intelligence
- Agent Orchestrator with 15 predefined pipelines
- AI Router with 5-tier model selection
- NLP Sandbox with sentiment, emotion, topic, and risk analysis
- PR response generation in Chinese and English

### Business Intelligence
- Brand Health Engine with weighted composite scoring
- Root Cause Engine with Pareto analysis
- Store Intelligence with daily health calculation and ranking
- Operational Intelligence with metric-to-event correlation
- Predictive Intelligence with 7-day multi-factor forecasting
- Learning Memory with historical case matching

### Frontend
- Apple Frosted Glass design language
- 12 modular components
- 8-page SPA navigation
- Real-time voice streaming with WebSocket
- i18n: Traditional Chinese + English (260+ keys)
- Language switcher with localStorage persistence

---

## Known Limitations

1. **Mock Mode Only:** No real LLM integration (OpenAI/Gemini keys not configured)
2. **No Real Crawlers:** Social media data is simulated (API keys required)
3. **No ML Models:** Predictions use moving average, not real ML
4. **Single Tenant Demo:** Multi-tenant is architected but not activated
5. **No Email/Notification:** Notification service exists but not connected
6. **No CI/CD:** GitHub Actions not yet configured
7. **No Production Monitoring:** Prometheus/Grafana not integrated

---

## Next Roadmap

### v1.1 — Production Hardening
- Real LLM integration (OpenAI + Gemini)
- Social media crawler integration
- CI/CD with GitHub Actions
- Unit test coverage > 80%
- Production monitoring stack

### v2.0 — Enterprise SaaS
- Multi-tenant activation with Stripe billing
- Custom KPI builder
- White-label support
- Advanced analytics (cohort, churn, A/B testing)

---

## How to Demo

See `docs/DEMO_SCRIPT.md` for a complete 5-minute walkthrough.

## Quick Start

```bash
cd docker && docker compose up -d
# Frontend: http://localhost:26117
# API Docs: http://localhost:8000/docs
```
