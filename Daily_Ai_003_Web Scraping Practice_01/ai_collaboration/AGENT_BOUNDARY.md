# AGENT_BOUNDARY

## OpenCode (Backend)
- Backend API (FastAPI)
- Crawler (Python)
- Database (SQLite schema + queries)
- API documentation
- Scripts for crawling and seeding

## Gemini (Frontend)
- PWA shell (HTML/CSS/JS)
- Service Worker (sw.js)
- PWA manifest (manifest.json)
- Responsive UI
- Frontend routing and state management

## Codex (Review)
- Code review for all PRs
- Architecture review
- Performance and security review

## Handover Protocol
1. OpenCode writes backend code → updates CHANGELOG.md + HANDOVER.md
2. Gemini writes frontend code → updates CHANGELOG.md + HANDOVER.md
3. Codex reviews → updates HANDOVER.md with review notes
4. At end of each session, CURRENT_TASK.md is updated with next steps
