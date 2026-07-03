# PTT Joke Meme PWA

**Version:** v1.0.0-rc1 — Release Candidate

A Progressive Web App that aggregates meme-worthy posts from PTT Joke board. Browse, search, and share funny posts with image previews.

## Features

- **PTT Joke Crawler** — Periodically fetches latest posts from PTT Joke board
- **Deduplication** — Avoids duplicate articles and images via unique constraints
- **REST API** — FastAPI backend with 6 endpoints (articles, images, search, popular)
- **React PWA** — Mobile-first responsive UI with offline support
- **PWA Ready** — Manifest, service worker, offline fallback
- **Image Fallback** — Graceful handling of broken or missing images

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| PowerShell | 5.1+ | `$PSVersionTable.PSVersion` |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python (FastAPI), SQLAlchemy, SQLite |
| Crawler | Python (requests, BeautifulSoup) |
| Frontend | React 19, Vite 6 |
| PWA | Service Worker, Cache API, Web Manifest |
| AI Team | OpenCode (backend), Gemini (frontend), Codex (review) |

## Folder Structure

```
├── backend/               # FastAPI backend (API, crawler, models, repos)
├── frontend/              # React + Vite PWA frontend
├── database/              # SQLite database (auto-created)
├── docs/                  # Documentation & release notes
├── ai_collaboration/      # AI coordination files
├── scripts/               # Start / run scripts
└── tests/                 # (placeholder for future tests)
```

## Backend Setup

Open a terminal and run:

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Or use the script:

```powershell
.\scripts\start_backend.ps1
```

Backend runs at `http://127.0.0.1:8000`. The database is auto-created on first startup.

## Frontend Setup

Open a **second** terminal and run:

```powershell
cd frontend
npm install
npm run dev
```

Or use the script:

```powershell
.\scripts\start_frontend.ps1
```

Frontend runs at `http://127.0.0.1:5173`.

## Crawler Run Command

Open a **third** terminal and run:

```powershell
cd backend
python run_crawler.py --pages 1
```

Or use the script:

```powershell
.\scripts\run_crawler.ps1 -pages 1
```

- Max 3 pages per run (`--pages 3`).
- 2-second delay between HTTP requests to respect PTT server.
- Duplicate articles/images are automatically skipped.

## Demo Steps

1. Start backend (terminal 1).
2. Start frontend (terminal 2).
3. Open `http://127.0.0.1:5173` in a browser.
4. **Statistics panel** shows article and image counts.
5. **Latest** tab shows article list (default view).
6. Switch to **Images** tab to see the meme grid with thumbnails.
7. Switch to **Popular** tab for articles sorted by push count.
8. Use the **Search** bar to search by keyword.
9. Click an article's **詳情** button to view detail + images.
10. Click an image thumbnail to open the **preview modal**.
11. Click **開啟 PTT 原文** to open the original article in a new tab.
12. Run crawler (`python run_crawler.py --pages 1`), then refresh to see updated stats.

## API List

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/statistics` | DB statistics |
| GET | `/api/articles` | Article list (paginated, sortable) |
| GET | `/api/articles/{id}` | Article detail with images |
| GET | `/api/images` | Image list (optional articleId filter) |
| GET | `/api/search?q=` | Search articles by title/author |
| GET | `/api/popular` | Popular articles by push_count |

## Known Limitations

| Limitation | Impact |
|------------|--------|
| External image URLs may fail | Images on Imgur may become unavailable; fallback UI handles this |
| PTT page structure may change | Crawler relies on HTML parsing; layout changes require updates |
| No automated tests yet | Manual testing only |
| Crawler must remain low-frequency | 2s delay + max 3 pages per run to avoid overloading PTT |
| SVG-only PWA icon | Older browsers may not render it |

See `docs/KNOWN_RISKS.md` for full details.

## Release Candidate Status

**v1.0.0-rc1** — Ready for demo and acceptance verification.

## Live Demo

> This project runs locally. No public hosted demo is available yet.
> 本專案為本地執行，目前尚無公開部署版本。

```text
Backend  → http://127.0.0.1:8000
Frontend → http://127.0.0.1:5173
```

### Quick Start / 快速啟動

| Step | English | 中文 |
|------|---------|------|
| 1 | `.\scripts\start_backend.ps1` | 啟動後端 API |
| 2 | `.\scripts\start_frontend.ps1` | 啟動前端畫面 |
| 3 | Open `http://127.0.0.1:5173` | 開啟瀏覽器 |
| 4 | `.\scripts\run_crawler.ps1 -pages 1` | 執行爬蟲抓資料 |

### What You Can See / 功能預覽

| Feature | English | 中文 |
|---------|---------|------|
| Statistics | Dashboard shows article & image counts | 儀表板顯示文章與圖片數量 |
| Articles | Browse PTT joke articles in list view | 以列表瀏覽 PTT 笑話文章 |
| Images | Grid view with image thumbnails | 網格檢視含圖片縮圖 |
| Search | Search by title or author keyword | 依標題或作者關鍵字搜尋 |
| Popular | Articles sorted by push count | 依推文數排序熱門文章 |
| Detail | Click to view article detail + images | 點擊查看文章詳情與圖片 |
| Modal | Click image for full-size preview | 點擊圖片開啟全尺寸預覽 |
| PTT Link | One-click to open original article | 一鍵開啟 PTT 原文 |
| Offline | Service worker + offline fallback page | 離線支援與離線提示頁面 |

### Live Screenshots / 實際畫面

> Screenshots to be added.
> 截圖待補。
