# 01_Project_Overview

## Project Name
PTT Joke Meme PWA

## Description
A Progressive Web App that aggregates meme-worthy posts from PTT Joke board. Users can browse, search, and share funny posts with image previews.

## Tech Stack
- **Backend:** Python (FastAPI) — OpenCode
- **Frontend:** PWA (HTML/CSS/JS) — Gemini
- **Database:** SQLite (MVP) → PostgreSQL (future)
- **Crawler:** Python (requests + BeautifulSoup)

## Core Principles (MVP)
1. No image download — store only `image_url`
2. Preserve PTT `article_url`
3. Lightweight, mobile-first UI
4. Offline-capable via Service Worker

## Team
| Role | Agent | Responsibility |
|------|-------|----------------|
| Backend | OpenCode | Backend, crawler, database, API |
| Frontend | Gemini | Frontend, PWA, RWD, UI |
| Reviewer | Codex | Code review |
