# Release Notes — v1.0.0-rc1

## Release Version

**v1.0.0-rc1**

## Release Date

2026-07-03

## Completed Features

| Feature | Description |
|---------|-------------|
| FastAPI Backend | Modular FastAPI application with health, statistics, and data APIs |
| SQLite Database | Auto-created SQLite database with SQLAlchemy ORM |
| Article + Image Models | Normalized schema with Article 1:N Image relationship |
| CrawlerLog | Execution logging for crawler runs (status, counts, errors) |
| PTT Crawler | Board page + article detail parser with image extraction |
| Deduplication | Unique constraints on article_url and image_url prevent duplicates |
| REST API | 6 endpoints: health, statistics, articles, images, search, popular |
| Pagination & Sorting | Page-based pagination, sort by date/push_count/created_at |
| Error Handling | Unified error format with error codes (NOT_FOUND, INVALID_PAGE, etc.) |
| React Frontend | React 19 + Vite 6 with modular component architecture |
| PWA Support | Web manifest, service worker, offline fallback page |
| RWD | Responsive design for mobile, tablet, and desktop (3 breakpoints) |
| Image Fallback | SafeImage component with broken image fallback UI |
| CORS Support | Cross-origin requests enabled for frontend-backend integration |
| API Integration | All 7 backend endpoints connected to frontend components |

## Known Limitations

| Limitation | Impact |
|------------|--------|
| External image URLs may fail | Images hosted on Imgur may become unavailable; fallback UI exists |
| PTT page structure may change | Crawler depends on HTML structure; changes would require parser update |
| No automated tests | Manual testing only; no regression safety net |
| SVG-only PWA icon | Older browsers may not render SVG manifest icons |
| Service worker does not cache API responses | Offline mode shows app shell only, no cached article data |

## Release Recommendation

This release candidate is ready for demo and acceptance verification. All core features are implemented and integrated. No blocking issues were found during the Sprint 7 integration review.

**Recommended next steps:**
1. Run the demo checklist (`docs/DEMO_CHECKLIST.md`)
2. Add automated tests
3. Prepare production deployment configuration
