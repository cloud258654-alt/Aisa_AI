# API Design — PTT Joke Meme PWA

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| v1.0 | 2026-07-03 | Initial API design | OpenCode |

## 1. Global Specification

- **Base URL:** `/api`
- **Protocol:** HTTP
- **Format:** JSON (all requests and responses)
- **Authentication:** None (MVP — public access)
- **Pagination:** `?page=1&per_page=20` (default per_page: 20, max: 100)

### Common Response Envelope

```json
{
  "data": { ... },
  "page": 1,
  "per_page": 20,
  "total": 100
}
```

### Error Response Format

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Article not found"
  }
}
```

## 2. Endpoints

### GET /api/health

Health check endpoint.

**Response `200`**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "service": "ptt-joke-meme-api"
}
```

---

### GET /api/articles

List articles with pagination.

**Query Parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| per_page | int | 20 | Items per page |
| sort | string | `-article_date` | Sort field (+/- for asc/desc) |

**Response `200`**

```json
{
  "data": [
    {
      "id": 1,
      "title": "笑死",
      "author": "john123",
      "article_url": "https://www.ptt.cc/bbs/Joke/...",
      "article_date": "2026-07-03T12:00:00",
      "push_count": 99,
      "source_board": "Joke",
      "images": [
        {
          "id": 1,
          "image_url": "https://i.imgur.com/abc123.jpg",
          "image_type": "jpg"
        }
      ]
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 100
}
```

**Error Codes**

| Code | Status | When |
|------|--------|------|
| INVALID_PAGE | 400 | Page or per_page out of range |

---

### GET /api/articles/{id}

Get a single article with its images.

**Path Parameters**

| Param | Type | Description |
|-------|------|-------------|
| id | int | Article ID |

**Response `200`**

```json
{
  "data": {
    "id": 1,
    "title": "笑死",
    "author": "john123",
    "article_url": "https://www.ptt.cc/bbs/Joke/...",
    "article_date": "2026-07-03T12:00:00",
    "push_count": 99,
    "source_board": "Joke",
    "images": [
      {
        "id": 1,
        "image_url": "https://i.imgur.com/abc123.jpg",
        "image_type": "jpg"
      }
    ]
  }
}
```

**Error Codes**

| Code | Status | When |
|------|--------|------|
| NOT_FOUND | 404 | Article ID does not exist |

---

### GET /api/images

List images with optional article filter.

**Query Parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| per_page | int | 20 | Items per page |
| article_id | int | | Filter by article ID |

**Response `200`**

```json
{
  "data": [
    {
      "id": 1,
      "article_id": 1,
      "image_url": "https://i.imgur.com/abc123.jpg",
      "image_type": "jpg"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 50
}
```

**Error Codes**

| Code | Status | When |
|------|--------|------|
| INVALID_PAGE | 400 | Page or per_page out of range |

---

### GET /api/search

Search articles by keyword.

**Query Parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| q | string | (required) | Search keyword |
| page | int | 1 | Page number |
| per_page | int | 20 | Items per page |

**Response `200`**

```json
{
  "data": [
    {
      "id": 1,
      "title": "笑死",
      "author": "john123",
      "article_url": "https://www.ptt.cc/bbs/Joke/...",
      "push_count": 99,
      "images": [...]
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 5
}
```

**Error Codes**

| Code | Status | When |
|------|--------|------|
| MISSING_QUERY | 400 | `q` parameter is missing or empty |

---

### GET /api/popular

Get popular articles sorted by push_count.

**Query Parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| per_page | int | 20 | Items per page |
| min_push | int | 10 | Minimum push count filter |

**Response `200`**

```json
{
  "data": [
    {
      "id": 1,
      "title": "笑死",
      "author": "john123",
      "push_count": 99,
      "images": [...]
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 30
}
```

---

## 3. Error Codes Summary

| Code | HTTP Status | Description |
|------|-------------|-------------|
| NOT_FOUND | 404 | Requested resource not found |
| INVALID_PAGE | 400 | Page number or per_page out of valid range |
| MISSING_QUERY | 400 | Required query parameter missing |
| INTERNAL_ERROR | 500 | Unexpected server error |
