# 02_Requirements

## Functional Requirements
1. Crawl PTT Joke board periodically for new posts
2. Extract post title, content, image URLs, and article URL
3. Store data in database (no image download)
4. Provide REST API to query stored posts
5. Display posts in a mobile-friendly PWA
6. Support search/filter by keyword
7. Offline access to cached posts

## Non-Functional Requirements
1. PWA must work offline (Service Worker + Cache API)
2. Responsive design for mobile and desktop
3. API response time < 500ms for cached queries
4. Crawler should respect PTT rate limits

## Out of Scope (MVP)
- User accounts / login
- Comments / voting
- Image hosting
- Real-time updates
- Push notifications
