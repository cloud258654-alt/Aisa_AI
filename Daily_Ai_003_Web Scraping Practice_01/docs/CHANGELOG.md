# CHANGELOG

## [0.9.0] — 2026-07-03

### Added
- Sprint 6 Frontend PWA completed.

## [1.0.0-rc1] — 2026-07-03

### Added
- Sprint 8 Release Candidate v1.0.0-rc1
- `README.md` — updated with full project info, setup, demo steps, API list
- `docs/RELEASE_NOTES_v1.0.0.md` — release notes with features, limitations, recommendation
- `docs/DEMO_CHECKLIST.md` — demo acceptance checklist (backend, crawler, frontend, PWA)
- `docs/KNOWN_RISKS.md` — 7 documented risks with severity, impact, mitigation
- `scripts/start_backend.ps1` — backend startup script
- `scripts/start_frontend.ps1` — frontend startup script
- `scripts/run_crawler.ps1` — crawler runner script (with --pages param, max 3)

## [0.10.0] — 2026-07-03

### Added
- Sprint 7 Integration Review completed
- Backend / Frontend / Crawler integration verified
- `docs/REVIEW_REPORT.md` created with 11-section formal review
- Recommendation: enter Sprint 8 Release Candidate
- React + Vite frontend created under `frontend/`.
- Meme image grid, article list, search, sort, popular view, image preview modal, and statistics panel created.
- API integration completed for health/statistics/articles/article detail/images/search/popular endpoints.
- PWA manifest, service worker, offline fallback, and app icon added.
- RWD layout completed for mobile, tablet, and desktop.

## [0.1.0] — 2026-07-03

### Added
- Project skeleton with directory structure
  - `docs/`, `ai_collaboration/`, `backend/`, `frontend/`, `database/`, `tests/`, `scripts/`
- Documentation files
  - `docs/01_Project_Overview.md`
  - `docs/02_Requirements.md`
  - `docs/03_Software_Design.md`
  - `docs/CHANGELOG.md`
- AI collaboration files
  - `ai_collaboration/AGENT_BOUNDARY.md`
  - `ai_collaboration/CURRENT_TASK.md`
  - `ai_collaboration/TASK_ASSIGNMENT.json`
  - `ai_collaboration/HANDOVER.md`
- Root `README.md`

## [0.2.0] — 2026-07-03

### Added
- Backend Foundation 建立
  - FastAPI 專案骨架 with modular structure (api/, crawler/, database/, models/, services/, utils/)
  - `backend/app/main.py` — FastAPI app entry point with health router included
  - `backend/app/api/health.py` — `GET /api/health` endpoint returning `{"status":"ok","version":"0.1.0","service":"ptt-joke-meme-api"}`
  - `backend/requirements.txt` — fastapi, uvicorn

## [0.3.0] — 2026-07-03

### Added
- SQLite Foundation 建立
  - `backend/app/database/database.py` — engine, Base, init_db (auto-creates database/memes.db)
  - `backend/app/database/session.py` — SessionLocal, get_db dependency
  - `backend/app/models/meme.py` — Meme model with id, title, author, article_date, push_count, article_url, image_url, image_type, source_board, created_at, updated_at
  - Unique constraint on (article_url, image_url)
  - `backend/requirements.txt` — added sqlalchemy
  - Database auto-initialization on app startup via lifespan

## [0.4.0] — 2026-07-03

### Added
- Requirement Document v1.0
  - `docs/Requirement.md` — SDS Requirement Template 套版
  - 7 項功能需求 (FR-001 ~ FR-007)
  - 4 項非功能需求 (NFR-001 ~ NFR-004)
  - 5 個使用案例 (UC-01 ~ UC-05)
  - Data Source Policy 章節
  - Acceptance Criteria 章節 (每項 FR 對應驗收項目)

## [0.5.0] — 2026-07-03

### Added
- System Design v1.0 — Sprint 2
  - `docs/04_Database_Design.md` — Article + Image normalized schema, ER diagram, FK, indexes, future expansion
  - `docs/05_Crawler_Design.md` — Crawler flow (Scheduler → Board → Article Parser → Image Parser → Dedup → DB), error retry, rate limit, logging, multi-platform extension
  - `docs/06_API_Design.md` — 6 endpoints: health, articles, article detail, images, search, popular. Request/response specs, error codes, pagination

## [0.6.0] — 2026-07-03

### Added
- Sprint 3 Backend Foundation v1.0
  - Restructured database layer: `database.py`, `session.py`, `init_db.py`
  - Models: `Article` (articles), `Image` (images), `CrawlerLog` (crawler_logs)
  - Article 1:N Image relationship with FK + unique constraints
  - Indexes on `article_date`, `push_count`, `author`
  - Repositories: `article_repository`, `image_repository`, `crawler_log_repository`
  - Service: `statistics_service`
  - API: `GET /api/statistics` — article/image/log counts + last crawler status
  - Removed deprecated `Meme` model

## [0.7.0] — 2026-07-03

### Added
- Sprint 4 PTT Crawler v1.0
  - `backend/app/crawler/ptt_joke_crawler.py` — Board page fetcher, article parser, article detail parser
  - `backend/app/crawler/image_extractor.py` — Image URL extraction from HTML (jpg/png/gif/webp, imgur)
  - `backend/app/services/crawler_service.py` — Orchestration: crawl → dedup → DB write → CrawlerLog
  - `backend/run_crawler.py` — CLI runner with --pages (max 3) and --delay args
  - `backend/requirements.txt` — added requests, beautifulsoup4
- Deduplication: article_url and image_url uniqueness enforced before insert
- CrawlerLog integration: each run records status, counts, errors

## [0.8.0] — 2026-07-03

### Added
- Sprint 5 Backend API v1.0
  - `GET /api/articles` — paginated article list with sorting (article_date, push_count, created_at)
  - `GET /api/articles/{id}` — article detail with images, 404 if not found
  - `GET /api/images` — image list with optional articleId filter
  - `GET /api/search?q=` — search articles by title or author, 400 if q missing
  - `GET /api/popular` — articles sorted by push_count desc
  - Pydantic schemas: `common_schema`, `article_schema`, `image_schema`
  - Services: `article_service`, `image_service`, `search_service`
  - Unified error format: `{"error": {"code": "...", "message": "..."}}`
  - Error codes: NOT_FOUND (404), INVALID_PAGE (400), INVALID_PAGE_SIZE (400), INVALID_SORT (400), MISSING_QUERY (400)
  - Pagination: page validation (>=1), pageSize cap (max 100)

## [0.10.0] — 2026-07-03

### Added
- Sprint 7 Integration Review v1.0
  - `docs/REVIEW_REPORT.md` — comprehensive review report
  - Backend: all 13 API endpoints verified, database schema checked, crawler tested
  - Frontend: npm install + build verified, all UI states confirmed, PWA manifest/SW/offline OK
  - Bug fixes: TASK_ASSIGNMENT.json T004 status corrected, status values unified
