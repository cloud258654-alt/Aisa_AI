# Known Risks — PTT Joke Meme PWA v1.0.0-rc1

| # | Risk | Severity | Impact | Mitigation |
|---|------|----------|--------|------------|
| 1 | External image URL may fail | Low | Images hosted on Imgur may become unavailable, resulting in broken image displays | SafeImage component provides fallback UI; article URLs preserved for manual access |
| 2 | PTT page structure may change | Medium | Crawler relies on specific HTML class names and DOM structure; layout changes by PTT would break article/image parsing | Crawler error handling logs parse failures without crashing; manual parser update needed if PTT changes layout |
| 3 | Crawler should remain low-frequency | Low | High-frequency crawling could overload PTT servers or trigger rate limiting / IP blocks | 2-second default delay, max 3 pages per run, configurable via --delay parameter |
| 4 | No automated tests | Medium | All testing is manual; no regression safety net for code changes | Mitigated by AI code review process; automated test suite should be added in next sprint |
| 5 | SVG-only PWA icon | Low | Some older browsers do not support SVG icons in web manifests | Modern browsers (Chrome, Firefox, Edge, Safari) support SVG manifest icons; PNG fallback can be added if needed |
| 6 | Service worker does not cache API responses | Low | Offline mode shows only the app shell; article/image data is unavailable without network | Mitigated by offline.html with clear messaging; full offline data caching can be added as future enhancement |
| 7 | SQLite concurrency limitations | Low | SQLite does not handle concurrent writes well; multiple crawler instances could cause write conflicts | Single crawler instance design; SQLite is suitable for MVP scale; PostgreSQL migration planned for production |
