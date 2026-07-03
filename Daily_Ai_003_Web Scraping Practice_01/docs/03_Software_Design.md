# 03_Software_Design

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   PTT Joke   │────▶│   Crawler    │────▶│   Database   │
│   (Web)      │     │  (Python)    │     │   (SQLite)   │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
┌─────────────┐     ┌──────────────┐            │
│   Browser   │────▶│  FastAPI     │◀───────────┘
│   (PWA)     │◀────│  (Backend)   │
└─────────────┘     └──────────────┘
```

## Database Schema

### `posts`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| title | TEXT | Post title |
| content | TEXT | Post text content |
| image_url | TEXT | Extracted image URL |
| article_url | TEXT | PTT article URL (unique) |
| author | TEXT | Post author |
| published_at | DATETIME | PTT post timestamp |
| created_at | DATETIME | Crawl timestamp |

## API Endpoints (MVP)

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/posts | List posts (paginated) |
| GET | /api/posts/{id} | Get single post |
| GET | /api/posts/search?q= | Search posts |
| GET | /api/health | Health check |

## Frontend Structure (MVP)

- `index.html` — Shell
- `css/style.css` — Styles
- `js/app.js` — App logic
- `sw.js` — Service Worker
- `manifest.json` — PWA manifest
