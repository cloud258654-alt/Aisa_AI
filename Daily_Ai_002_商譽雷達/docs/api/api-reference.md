# Sentinel AI ECXIP — API Reference

**Base URL:** `/api/v1`

## Authentication

All endpoints except `/auth/login` and `/auth/refresh` require a valid JWT Bearer token.

```
Authorization: Bearer <access_token>
```

Token is obtained via `POST /api/v1/auth/login`. Access tokens expire after 30 minutes. Use `POST /api/v1/auth/refresh` with a refresh token to obtain a new token pair.

---

## Pagination Convention

All list endpoints return a `PaginatedResponse` envelope:

```json
{
  "items": [...],
  "total": 1547,
  "page": 1,
  "page_size": 20,
  "pages": 78
}
```

Query parameters: `?page=1&page_size=20` (page_size max: 100)

---

## Common Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `date_from` | date | Filter from date (inclusive) |
| `date_to` | date | Filter to date (inclusive) |
| `store_id` | string | Filter by store ID |
| `channel` | enum | `email`, `chat`, `phone`, `social`, `survey`, `in_store`, `app`, `all` |
| `sentiment` | enum | `positive`, `neutral`, `negative`, `all` |
| `risk_level` | enum | `low`, `medium`, `high`, `critical`, `all` |
| `keyword` | string | Search keyword in content |
| `sort_by` | string | Field to sort by |
| `sort_order` | string | `asc` or `desc` |

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "VALIDATION_ERROR",
  "errors": [{"field": "email", "message": "Invalid email format"}]
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Resource not found |
| 422 | Validation error (Pydantic) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service unavailable (DB/Redis down) |

---

## Endpoints

### Authentication

#### `POST /auth/login`
Login and obtain access/refresh tokens.

**Request Body:**
```json
{
  "email": "admin@sentinel.ai",
  "password": "admin123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

---

#### `POST /auth/refresh`
Exchange refresh token for new token pair.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOi..."
}
```

**Response:** `200 OK` — same as login response.

---

#### `POST /auth/register`
Register a new user (admin only).

**Request Body:**
```json
{
  "email": "newuser@sentinel.ai",
  "password": "securepass123",
  "full_name": "New User",
  "role": "viewer",
  "department": "Marketing",
  "store_id": "str_000000000000000000000001"
}
```

**Response:** `201 Created`
```json
{
  "id": "usr_20250629120000",
  "email": "newuser@sentinel.ai",
  "full_name": "New User",
  "role": "viewer",
  "department": "Marketing",
  "store_id": "str_000000000000000000000001",
  "organization_id": "org_000000000000000000000001",
  "is_active": true,
  "avatar_url": null,
  "created_at": "2026-06-29T12:00:00Z",
  "last_login_at": null
}
```

---

#### `GET /auth/me`
Get current user profile.

**Response:** `200 OK` — UserResponse object.

---

#### `PUT /auth/me`
Update current user profile.

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "department": "Engineering",
  "avatar_url": "https://cdn.example.com/avatar.jpg"
}
```

**Response:** `200 OK` — UserResponse object.

---

#### `GET /auth/users`
List all users (admin only). Supports pagination.

**Response:** `200 OK` — `PaginatedResponse[UserResponse]`

---

#### `PUT /auth/users/{user_id}/role`
Update user role (admin only).

**Query:** `?role=manager`

**Response:** `200 OK` — UserResponse object.

---

### Voice of Customer (VOC)

#### `GET /voc/voices`
List voice feedback entries (paginated, filterable). Supports all common query params.

**Query:** `?page=1&page_size=20&channel=social&sentiment=negative&risk_level=high`

**Response:** `200 OK` — `PaginatedResponse[VoiceResponse]`

---

#### `GET /voc/voices/{voice_id}`
Get single voice entry with AI analysis.

**Response:** `200 OK`
```json
{
  "id": "voc_001",
  "channel": "in_store",
  "store_id": "str_000000000000000000000001",
  "customer_id": "cus_000000000000000000000001",
  "content": "I waited 20 minutes and the staff was unhelpful.",
  "language": "en",
  "analysis": {
    "sentiment": "negative",
    "sentiment_score": -0.72,
    "emotion": "frustration",
    "emotion_score": 0.85,
    "topics": ["wait_time", "staff_attitude"],
    "touchpoint": "in_store_service",
    "risk_level": "medium",
    "risk_score": 0.55,
    "summary": "Customer expresses frustration...",
    "keywords": ["wait", "slow", "staff", "service"]
  },
  "status": "processed",
  "tags": ["complaint", "service"],
  "created_at": "2026-06-29T12:00:00Z",
  "recorded_at": "2026-06-29T11:45:00Z"
}
```

---

#### `POST /voc/voices`
Ingest new customer voice from any channel. Triggers NLP analysis pipeline.

**Request Body:**
```json
{
  "channel": "social",
  "store_id": "str_000000000000000000000001",
  "customer_id": "cus_abc123",
  "content": "The service was absolutely terrible today.",
  "language": "en",
  "metadata": {"source": "twitter", "post_id": "12345"},
  "recorded_at": "2026-06-29T11:00:00Z"
}
```

**Response:** `201 Created` — VoiceResponse object.

---

#### `GET /voc/voices/stats/summary`
Aggregate voice statistics.

**Query:** `?date_from=2026-06-01&date_to=2026-06-29`

**Response:** `200 OK`
```json
{
  "total_voices": 1547,
  "by_sentiment": {"positive": 680, "neutral": 423, "negative": 444},
  "by_channel": {"in_store": 520, "survey": 380, "social": 290, "email": 210, "chat": 147},
  "by_risk_level": {"low": 1100, "medium": 320, "high": 105, "critical": 22},
  "avg_sentiment_score": 0.12,
  "period_start": "2026-06-01",
  "period_end": "2026-06-29"
}
```

---

#### `GET /voc/voices/stats/trends`
Voice sentiment trends over time.

**Query:** `?days=30`

**Response:** `200 OK` — Array of `VoiceTrendPoint` with daily sentiment breakdown.

---

#### `DELETE /voc/voices/{voice_id}`
Delete a voice entry (admin only).

**Response:** `204 No Content`

---

### Customer Experience (CX)

#### `GET /cx/journeys`
List customer journeys (paginated, filterable).

**Response:** `200 OK` — `PaginatedResponse[CxJourneyResponse]`

---

#### `GET /cx/journeys/{journey_id}`
Get journey detail with touchpoints.

**Response:** `200 OK` — CxJourneyResponse with touchpoint array, NPS, CSAT, CES scores.

---

#### `GET /cx/touchpoints`
List all touchpoints.

**Response:** `200 OK` — Array of TouchpointResponse with volume, sentiment, CSAT, top complaints.

---

#### `GET /cx/touchpoints/{touchpoint_id}/insights`
Get AI-generated insights for a specific touchpoint.

**Response:** `200 OK` — Array of CxInsightResponse with severity, metrics, recommendations.

---

#### `GET /cx/diagnostics`
Current CX journey diagnostic summary.

**Response:** `200 OK`
```json
{
  "overall_nps": 38.5,
  "overall_csat": 3.8,
  "overall_ces": 3.4,
  "journey_completion_rate": 0.72,
  "friction_hotspots": [
    {"touchpoint": "Checkout", "friction_score": 0.85, "affected_users": 520, "root_cause": "Understaffing during peak"}
  ],
  "top_pain_points": ["Long checkout wait times", "Unresolved support tickets"],
  "improvement_areas": [...]
}
```

---

#### `GET /cx/diagnostics/store/{store_id}`
Store-specific CX diagnostics.

**Response:** `200 OK` — CxDiagnosticResponse scoped to one store.

---

### Brand Health

#### `GET /brand-health/current`
Latest brand health metrics.

**Response:** `200 OK`
```json
{
  "id": "bh_000000000000000000000001",
  "sentiment_index": 12.5,
  "nps_score": 38.0,
  "reputation_score": 72.0,
  "share_of_voice": 0.28,
  "engagement_rate": 0.045,
  "alert_count": 3,
  "trend_direction": "slightly_improving",
  "measured_at": "2026-06-29T12:00:00Z"
}
```

---

#### `GET /brand-health/history`
Paginated historical brand health data.

**Query:** Standard pagination + date range filters.

**Response:** `200 OK` — `PaginatedResponse[BrandHealthResponse]`

---

#### `GET /brand-health/stores/{store_id}/health`
Store-specific health metrics.

**Response:** `200 OK`
```json
{
  "store_id": "str_000000000000000000000001",
  "store_name": "Store 0001",
  "sentiment_index": 15.2,
  "nps_score": 42.0,
  "csat_score": 4.1,
  "alert_count": 1,
  "top_issues": ["Understaffing", "Cleanliness"],
  "staff_sentiment": 0.62,
  "measured_at": "2026-06-29T12:00:00Z"
}
```

---

#### `GET /brand-health/alerts`
Active brand alerts.

**Query:** `?status_filter=active`

**Response:** `200 OK` — Array of AlertResponse.

---

#### `POST /brand-health/alerts`
Create a manual brand alert.

**Request Body:**
```json
{
  "store_id": "str_000000000000000000000001",
  "title": "Checkout Wait Time Spiking",
  "description": "Average checkout wait time increased 40% in 48 hours.",
  "severity": "high",
  "category": "operations",
  "source": "manual",
  "metadata": {"metric": "avg_wait_minutes", "current": 8.5, "threshold": 5.0}
}
```

**Response:** `201 Created` — AlertResponse.

---

#### `PUT /brand-health/alerts/{alert_id}/resolve`
Resolve a brand alert.

**Query:** `?resolution_notes=Issue%20resolved%20by%20adding%20staff`

**Response:** `200 OK` — Updated AlertResponse.

---

### Root Cause Analysis

#### `GET /root-cause/analyses`
List root cause analyses (paginated).

**Response:** `200 OK` — `PaginatedResponse[RootCauseAnalysisResponse]` with Pareto data.

---

#### `POST /root-cause/analyze`
Trigger root cause analysis.

**Request Body:**
```json
{
  "case_id": "cas_001",
  "incident_type": "service_delay",
  "store_id": "str_000000000000000000000001",
  "description": "Checkout wait times have spiked 40% at 3 stores",
  "date_range_start": "2026-06-01",
  "date_range_end": "2026-06-29",
  "analysis_depth": "deep",
  "include_competitor_data": true
}
```

**Response:** `202 Accepted` — Pending analysis with `status: "pending"`.

---

#### `GET /root-cause/analyses/{analysis_id}`
Get root cause analysis detail.

**Response:** `200 OK` — Full RootCauseAnalysisResponse with root causes, Pareto data, methodology.

---

#### `GET /root-cause/summary`
Top root causes and Pareto analysis.

**Query:** `?days=30`

**Response:** `200 OK` — Top causes with frequency, impact, percentage, suggested actions.

---

#### `GET /root-cause/comparison/stores`
Compare root causes across stores.

**Query:** `?store_ids=str_001,str_002,str_003`

**Response:** `200 OK` — Common causes, unique causes per store, correlation matrix.

---

### Executive Dashboard

#### `GET /executive/morning-brief`
AI-generated morning executive brief.

**Response:** `200 OK`
```json
{
  "date": "2026-06-29",
  "summary": "Good morning. Today's customer sentiment index is at +12.5...",
  "key_metrics": {
    "total_voices_today": 342,
    "new_cases": 18,
    "resolved_cases": 22,
    "active_alerts": 3,
    "nps": 38.0,
    "csat": 3.8,
    "sentiment_index": 12.5,
    "avg_resolution_time_hours": 4.2
  },
  "store_ranking": [...],
  "voc_summary": "...",
  "cx_summary": "...",
  "risk_alerts": [...],
  "recommendations": [
    {
      "priority": "critical",
      "category": "Crisis Management",
      "action": "Issue a social media statement...",
      "expected_impact": "Reduce negative social sentiment by 40%"
    }
  ],
  "generated_at": "2026-06-29T07:00:00Z"
}
```

---

#### `GET /executive/today-summary`
Key metrics for today.

**Response:** `200 OK`
```json
{
  "date": "2026-06-29",
  "total_voices": 342,
  "total_cases": 18,
  "active_alerts": 3,
  "overall_nps": 38.0,
  "overall_csat": 3.8,
  "sentiment_index": 12.5,
  "trend_direction": "slightly_improving",
  "top_channels": [...]
}
```

---

#### `GET /executive/store-ranking`
Ranked store performance.

**Response:** `200 OK`
```json
{
  "rankings": [
    {"rank": 1, "store_id": "str_032", "store_name": "Downtown Flagship", "score": 92.5, "nps": 55.0, "trend": "improving"}
  ],
  "total_stores": 5,
  "best_performer": {...},
  "worst_performer": {...}
}
```

---

#### `GET /executive/risk-summary`
Current risk landscape.

**Response:** `200 OK` — Risk by severity, category, critical alerts, trend, risk score.

---

### NLP Sandbox

#### `POST /sandbox/analyze`
Analyze text through the NLP pipeline.

**Request Body:**
```json
{
  "text": "I had to wait 25 minutes just to pay and the staff was rude.",
  "language": "en",
  "context": "in_store",
  "store_id": "str_000000000000000000000001",
  "channel": "google_review",
  "include_sop": true,
  "include_pr_draft": true
}
```

**Response:** `200 OK`
```json
{
  "sentiment": "negative",
  "sentiment_score": -0.78,
  "emotion": "frustration",
  "emotion_breakdown": [
    {"name": "frustration", "score": 0.8, "confidence": 0.85},
    {"name": "anger", "score": 0.7, "confidence": 0.88}
  ],
  "topics": ["wait", "staff", "rude"],
  "touchpoint": "in_store_experience",
  "risk_level": "medium",
  "risk_score": 0.55,
  "summary": "Customer expresses negative sentiment regarding wait, staff at the in store experience touchpoint.",
  "keywords": ["negative", "frustration", "in_store_experience"],
  "pr_draft": "We appreciate your feedback regarding your recent experience...",
  "sop_suggestions": [
    {"category": "Checkout", "action": "Implement queue-busting protocol when wait exceeds 5 minutes", "priority": "high"}
  ],
  "processing_time_ms": 245.3,
  "model_used": "sentinel-nlp-v3",
  "analyzed_at": "2026-06-29T12:00:00Z"
}
```

---

### Case Workflow

#### `GET /workflow/cases`
List cases (paginated, filterable).

**Query:** `?page=1&status_filter=in_progress&priority_filter=high&assigned_to=usr_002`

**Response:** `200 OK` — `PaginatedResponse[CaseResponse]`

---

#### `POST /workflow/cases`
Create a new case.

**Request Body:**
```json
{
  "store_id": "str_000000000000000000000001",
  "voice_id": "voc_001",
  "title": "Checkout wait time complaint",
  "description": "Customer reported 25-minute wait at checkout counter.",
  "priority": "high",
  "category": "operations",
  "assigned_to": "usr_000000000000000000000002",
  "tags": ["checkout", "wait_time"],
  "due_date": "2026-07-01T00:00:00Z"
}
```

**Response:** `201 Created` — CaseResponse.

---

#### `GET /workflow/cases/{case_id}`
Get case detail with timeline.

**Response:** `200 OK` — Full CaseResponse with timeline entries.

---

#### `PUT /workflow/cases/{case_id}`
Update case status or assignment.

**Request Body:**
```json
{
  "status": "in_progress",
  "priority": "critical",
  "assigned_to": "usr_003",
  "tags": ["checkout", "wait_time", "escalated"],
  "resolution_notes": "Added extra cashier during peak hours."
}
```

**Response:** `200 OK` — Updated CaseResponse.

---

#### `POST /workflow/cases/{case_id}/comments`
Add comment to case timeline.

**Request Body:**
```json
{
  "content": "Investigating the staffing schedule for that shift.",
  "is_internal": true
}
```

**Response:** `201 Created` — CaseResponse with updated timeline.

---

#### `POST /workflow/cases/{case_id}/attachments`
Upload attachment to a case (multipart form).

**Response:** `201 Created`
```json
{
  "id": "att_20250629120000",
  "case_id": "cas_001",
  "filename": "receipt.png",
  "content_type": "image/png",
  "size_bytes": 245760,
  "uploaded_by": "usr_001",
  "uploaded_at": "2026-06-29T12:00:00Z"
}
```

---

#### `GET /workflow/cases/stats`
Workflow statistics.

**Response:** `200 OK` — Total cases, by status, priority, category, store, SLA breach count.

---

### Knowledge Base

#### `GET /knowledge/articles`
List articles (paginated).

**Query:** `?page=1&category=customer_service&search=wait+times`

**Response:** `200 OK` — `PaginatedResponse[ArticleResponse]`

---

#### `POST /knowledge/articles`
Create knowledge base article.

**Request Body:**
```json
{
  "title": "Handling Customer Complaints About Wait Times",
  "content": "# Handling Wait Time Complaints\n\n## Overview\nWhen a customer...",
  "category": "customer_service",
  "tags": ["wait_times", "complaints", "service_recovery"],
  "is_published": true,
  "source_voice_id": "voc_001",
  "source_case_id": null
}
```

**Response:** `201 Created` — ArticleResponse.

---

#### `GET /knowledge/articles/{article_id}`
Get article detail.

**Response:** `200 OK` — ArticleResponse.

---

#### `PUT /knowledge/articles/{article_id}`
Update an article.

**Request Body:** — Partial ArticleUpdate.

**Response:** `200 OK` — Updated ArticleResponse with incremented version.

---

#### `DELETE /knowledge/articles/{article_id}`
Delete an article (admin only).

**Response:** `204 No Content`

---

#### `GET /knowledge/search`
Semantic search across knowledge base.

**Query:** `?q=how+to+handle+angry+customers&limit=10`

**Response:** `200 OK`
```json
{
  "query": "how to handle angry customers",
  "results": [
    {
      "id": "kb_001",
      "title": "Handling Customer Complaints About Wait Times",
      "category": "customer_service",
      "snippet": "When a customer complains about wait times, follow the CARE protocol...",
      "relevance_score": 0.92,
      "tags": ["wait_times", "complaints"],
      "updated_at": "2026-06-29T12:00:00Z"
    }
  ],
  "total_results": 2,
  "search_time_ms": 45.2
}
```

---

### Trend Intelligence

#### `GET /trends/overview`
Multi-period trend overview (7d, 30d, 90d, 1y).

**Response:** `200 OK`
```json
{
  "current_7d": {"period": "7d", "total_voices": 1547, "sentiment_index": 12.5, ...},
  "current_30d": {"period": "30d", "total_voices": 6200, "sentiment_index": 10.8, ...},
  "current_90d": {...},
  "current_1y": {...},
  "generated_at": "2026-06-29T12:00:00Z"
}
```

---

#### `GET /trends/topics`
Top trending topics and complaints.

**Query:** `?period=7d`

**Response:** `200 OK` — Topics with count, sentiment trend, growth rate, related keywords.

---

#### `GET /trends/emotions`
Emotion distribution over time.

**Query:** `?days=30`

**Response:** `200 OK` — Time series of 8 Plutchik emotions with daily values and dominant emotion.

---

#### `GET /trends/predictions`
AI risk predictions for coming weeks.

**Query:** `?forecast_weeks=4`

**Response:** `200 OK` — Weekly predictions with volume, sentiment, risk level, confidence.

---

### Competitor Intelligence

#### `GET /competitors/`
List all competitors.

**Query:** `?is_active=true`

**Response:** `200 OK` — Array of CompetitorResponse.

---

#### `POST /competitors/`
Add a new competitor.

**Request Body:**
```json
{
  "name": "RetailMax Corp",
  "industry": "retail",
  "website": "https://retailmax.example.com",
  "description": "Largest brick-and-mortar retail competitor.",
  "tags": ["retail", "brick-and-mortar", "enterprise"],
  "is_active": true
}
```

**Response:** `201 Created` — CompetitorResponse.

---

#### `GET /competitors/{competitor_id}/metrics`
Competitor metrics comparison (NPS, CSAT, CES, social sentiment, SOV, response time).

**Response:** `200 OK` — CompetitorMetricsResponse with our vs competitor vs industry values.

---

#### `GET /competitors/benchmark`
Benchmark comparison across all competitors.

**Response:** `200 OK` — All metrics benchmarked with percentile ranking, strengths/weaknesses.

---

#### `GET /competitors/{competitor_id}/swot`
SWOT analysis for a competitor.

**Response:** `200 OK` — Strengths, weaknesses, opportunities, threats with impact scores and evidence.

---

### Health Check

#### `GET /api/v1/health`
System health check (unauthenticated).

**Response:** `200 OK` (healthy) or `503 Service Unavailable`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

---

## WebSocket Endpoints

### Voice Stream: `ws://<host>/ws/voice-stream/{channel}`
Real-time voice data streaming channel. Clients subscribe to receive new analyzed voices as they are ingested.

**Server Push Format:**
```json
{
  "channel": "voice-stream:all",
  "type": "new_voice",
  "data": {
    "id": "voc_new_001",
    "channel": "social",
    "content": "Just had the worst experience at Store #3...",
    "analysis": {"sentiment": "negative", "risk_level": "high", ...},
    "created_at": "2026-06-29T12:00:00Z"
  }
}
```

### Alert Notifications: `ws://<host>/ws/alerts/{user_id}`
Personalized alert channel for a specific user.

**Server Push Format:**
```json
{
  "channel": "alerts:usr_001",
  "type": "brand_alert",
  "data": {
    "alert_id": "alt_001",
    "title": "Checkout Wait Time Spike",
    "severity": "high",
    "created_at": "2026-06-29T12:00:00Z"
  }
}
```
