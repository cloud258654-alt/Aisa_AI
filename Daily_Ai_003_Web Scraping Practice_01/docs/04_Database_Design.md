# Database Design — PTT Joke Meme PWA

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| v1.0 | 2026-07-03 | Initial database design | OpenCode |

## 1. Design Goal

- Store PTT Joke articles and their associated image URLs.
- Normalize data to avoid duplication: one article can have multiple images.
- No image binary data stored — only image URLs.
- Support future multi-platform expansion (Dcard, Threads, Facebook).

## 2. ER Diagram

```
  ┌───────────┐          ┌───────────┐
  │  Article  │ 1      N │   Image   │
  │           │◄─────────│           │
  │  id (PK)  │          │  id (PK)  │
  │  title    │          │  article_id│
  │  author   │          │  image_url│
  │  ...      │          │  ...      │
  └───────────┘          └───────────┘
```

An Article has one or more Images. Each Image belongs to exactly one Article.

## 3. Table Design

### Article

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique article ID |
| title | TEXT | NOT NULL | Post title |
| author | TEXT | NOT NULL | Post author |
| article_url | TEXT | NOT NULL, UNIQUE | PTT article URL |
| article_date | DATETIME | | PTT post timestamp |
| push_count | INTEGER | DEFAULT 0 | Push count |
| source_board | TEXT | DEFAULT 'Joke' | Source board name |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record created time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record updated time |

### Image

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique image ID |
| article_id | INTEGER | FK → Article.id, NOT NULL | Parent article |
| image_url | TEXT | NOT NULL, UNIQUE | Image URL |
| image_type | TEXT | | Image type (jpg, gif, imgur, etc.) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record created time |

## 4. Primary Key

- **Article:** `id` (INTEGER, auto-increment)
- **Image:** `id` (INTEGER, auto-increment)

## 5. Foreign Key

- **Image.article_id → Article.id**
  - Ensures referential integrity.
  - Allows cascading queries: fetch all images for a given article.

## 6. Unique Constraint

- **Article.article_url** — prevents duplicate articles from the same PTT URL.
- **Image.image_url** — prevents duplicate image URLs across all articles.

## 7. Index Strategy

| Column | Table | Purpose |
|--------|-------|---------|
| article_date | Article | Sort articles by date (newest first) |
| push_count | Article | Sort or filter by popularity |
| author | Article | Filter articles by author |

Indexes improve query performance for the expected read patterns (latest articles, popular articles, author lookup).

## 8. Future Expansion

The design reserves for multi-platform support:

| Platform | Strategy |
|----------|----------|
| Dcard | Add `source_board = 'Dcard'` or introduce `platform` column |
| Threads | Same approach — platform-agnostic schema |
| Facebook | Facebook posts can map to Article; embedded media to Image |

Potential schema extension:

```
Article
  └── platform      TEXT     (e.g., 'ptt', 'dcard', 'threads')
  └── external_id   TEXT     (platform-specific post ID)

Image
  └── ─ (already platform-agnostic via article_id)
```
