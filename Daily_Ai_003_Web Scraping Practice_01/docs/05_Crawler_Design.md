# Crawler Design — PTT Joke Meme PWA

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| v1.0 | 2026-07-03 | Initial crawler design | OpenCode |

## 1. Crawler Flow

```
┌──────────────┐
│  Scheduler   │  Triggered periodically (e.g., every 30 min)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PTT Joke     │  HTTP GET https://www.ptt.cc/bbs/Joke/index.html
│ Board        │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Article      │  Parse HTML: extract title, author, date, push count,
│ Parser       │  article_url for each post on the index page
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Image        │  For each new article, fetch article page and
│ Parser       │  extract image URLs from content
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Deduplicate  │  Check Article.article_url and Image.image_url
│              │  against existing records before insert
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Database    │  Insert new Article and Image records
└──────────────┘
```

### Step Details

1. **Scheduler** — Triggers crawl at a fixed interval (configurable). Uses APScheduler or simple `time.sleep` loop.
2. **PTT Joke Board** — Fetches the PTT Joke board index page. Handles pagination if needed.
3. **Article Parser** — Parses the index HTML to extract article metadata (title, author, date, push count, article URL).
4. **Image Parser** — For each new article, fetches the article page and extracts `<img>` or `a-tag` image URLs from the content.
5. **Deduplicate** — Checks uniqueness constraints before writing. Skips existing records.
6. **Database** — Inserts new Article and Image records via SQLAlchemy session.

## 2. Error Retry

| Scenario | Strategy |
|----------|----------|
| Network error | Retry up to 3 times with exponential backoff (1s, 2s, 4s) |
| HTTP 503 / 429 | Wait 60 seconds, then retry once |
| Parse failure | Log error, skip the article, continue with next |
| Database write failure | Log error, retry once after 1 second |

## 3. Rate Limit

- Minimum 2-second delay between consecutive HTTP requests to PTT.
- Configurable via `CRAWLER_DELAY` environment variable.
- Respect `Retry-After` header if present in HTTP response.

## 4. Logging

| Level | When |
|-------|------|
| INFO | Crawl start, articles found, images found, crawl end |
| WARNING | Rate limit hit, retry attempt, skipped duplicate |
| ERROR | Network failure after retries, parse error, DB error |

Log format: `[timestamp] [LEVEL] [crawler] message`

## 5. Future Multi-platform

| Platform | Integration Strategy |
|----------|---------------------|
| Dcard | Add DcardCrawler class sharing the same BaseCrawler interface |
| Threads | Add ThreadsCrawler (via API if available, or scraping) |
| Facebook | Add FacebookCrawler (via Graph API or public page scraping) |

Each new platform implements:

```
class BaseCrawler:
    def fetch(self) -> list[dict]: ...
    def parse(self, raw: str) -> list[Article]: ...
    def extract_images(self, article) -> list[str]: ...
    def save(self, articles, images): ...
```
