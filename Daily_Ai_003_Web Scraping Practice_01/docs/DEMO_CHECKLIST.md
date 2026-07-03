# Demo Checklist — PTT Joke Meme PWA v1.0.0-rc1

Use this checklist to verify the release candidate is ready for demo.

---

## Backend Check

- [ ] Start backend: `cd backend && uvicorn app.main:app --reload`
- [ ] `GET /api/health` returns `200 {"status":"ok",...}`
- [ ] `GET /api/statistics` returns `200` with article/image/log counts
- [ ] `GET /api/articles?pageSize=2` returns `200` with paginated items
- [ ] `GET /api/articles/1` returns `200` with article detail + images
- [ ] `GET /api/articles/999999` returns `404` with error format
- [ ] `GET /api/images?pageSize=2` returns `200` with image list
- [ ] `GET /api/search?q=test` returns `200` (may be empty)
- [ ] `GET /api/search` (no q) returns `400 MISSING_QUERY`
- [ ] `GET /api/popular?pageSize=2` returns `200` sorted by push_count
- [ ] Invalid sortBy returns `400 INVALID_SORT`
- [ ] Page=0 returns `400 INVALID_PAGE`

## Crawler Check

- [ ] Run: `cd backend && python run_crawler.py --pages 1`
- [ ] Crawler completes with status=success
- [ ] Re-run: `python run_crawler.py --pages 1` — confirms dedup (0 new)
- [ ] CrawlerLog updated (check via `/api/statistics`)
- [ ] `--pages 5` rejected (max 3)

## Frontend Check

- [ ] `cd frontend && npm install` — 0 vulnerabilities
- [ ] `npm run build` — builds successfully
- [ ] `npm run dev` — dev server starts
- [ ] Open `http://127.0.0.1:5173` in browser
- [ ] Statistics panel displays articles and images count
- [ ] Latest view shows article list
- [ ] Images view shows meme grid with thumbnails
- [ ] Popular view shows articles sorted by push count
- [ ] Broken image shows fallback UI (not broken icon)
- [ ] Click image thumbnail opens preview modal
- [ ] Click "開啟 PTT 原文" opens original article in new tab
- [ ] Click article "詳情" button shows detail modal with images
- [ ] Search by keyword returns matching results
- [ ] Search with empty input shows error state
- [ ] Sort dropdown changes article ordering
- [ ] Pagination controls (previous/next) work correctly
- [ ] Loading state appears during API calls
- [ ] Error state appears when API is unavailable

## PWA Check

- [ ] `frontend/public/manifest.json` exists with valid fields
- [ ] `frontend/public/service-worker.js` exists with install/activate/fetch
- [ ] `frontend/public/offline.html` exists
- [ ] `frontend/public/icons/icon.svg` exists
- [ ] Service worker registers on page load (check browser DevTools)
- [ ] Offline: stop backend, navigate — app shows offline fallback

## Demo Summary

**Passed:** ___ / ___

**Notes:**

---

**Checked by:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Date:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
