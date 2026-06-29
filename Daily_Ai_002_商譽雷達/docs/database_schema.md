# Sentinel AI ECXIP — Database Schema

## Overview

The database consists of 24 models (tables) organized across 7 domain groups:
- **Organization** (7 tables): Multi-tenant identity, users, roles, stores
- **VOC** (3 tables): Voice feedback ingestion and AI analysis
- **CX** (3 tables): Customer journey, touchpoints, insights
- **Brand** (3 tables): Brand health, store health, alerts
- **Workflow** (3 tables): Case management, timeline, attachments
- **Knowledge** (2 tables): RAG knowledge base with versioning
- **Competitor** (3 tables): Competitive intelligence tracking

All models extend `Base` (`AsyncAttrs, DeclarativeBase`) from `core.database.py`.

---

## Organization Domain

### `organizations` — Multi-tenant organizations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique org ID |
| `name` | VARCHAR(255) | NOT NULL | Organization display name |
| `slug` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | URL-safe identifier |
| `plan` | VARCHAR(20) | DEFAULT 'free' | Subscription plan tier |
| `is_active` | BOOLEAN | DEFAULT true, NOT NULL | Soft-delete flag |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), ON UPDATE NOW() | Last update timestamp |

**Indexes:** `idx_organizations_slug` on `slug`

### `departments` — Organizational departments (hierarchical)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique dept ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `name` | VARCHAR(255) | NOT NULL | Department name |
| `parent_id` | INTEGER | FK → departments.id ON DELETE SET NULL, NULLABLE, INDEX | Self-referential parent |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation timestamp |

**Indexes:** `idx_departments_org_id`, `idx_departments_parent_id`

### `regions` — Geographic regions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique region ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `name` | VARCHAR(255) | NOT NULL | Region name |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation timestamp |

### `stores` — Physical or virtual store locations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique store ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `dept_id` | INTEGER | FK → departments.id ON DELETE SET NULL, NULLABLE, INDEX | Department |
| `region_id` | INTEGER | FK → regions.id ON DELETE SET NULL, NULLABLE, INDEX | Region |
| `name` | VARCHAR(255) | NOT NULL | Store name |
| `address` | TEXT | NULLABLE | Physical address |
| `phone` | VARCHAR(50) | NULLABLE | Contact phone |
| `manager_name` | VARCHAR(255) | NULLABLE | Store manager |
| `is_active` | BOOLEAN | DEFAULT true, NOT NULL | Active status |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |
| `updated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), ON UPDATE NOW() | Last update |

**Relationships:** `organization`, `department`, `region`, `users`

### `users` — Platform users scoped to organization

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique user ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `email` | VARCHAR(320) | UNIQUE, NOT NULL, INDEX | Login email |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| `full_name` | VARCHAR(255) | NOT NULL | Display name |
| `role` | VARCHAR(20) | DEFAULT 'viewer', NOT NULL | Legacy role string |
| `dept_id` | INTEGER | FK → departments.id ON DELETE SET NULL, NULLABLE, INDEX | Department |
| `store_id` | INTEGER | FK → stores.id ON DELETE SET NULL, NULLABLE, INDEX | Store assignment |
| `is_active` | BOOLEAN | DEFAULT true, NOT NULL | Active status |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |
| `updated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), ON UPDATE NOW() | Last update |

**Enum values for `role`:** `viewer`, `analyst`, `manager`, `admin`, `superadmin`

**Relationships:** `organization`, `department`, `store`, `roles` (M2M via `user_role`), `assigned_cases`, `created_cases`, `case_timelines`

### `roles` — Custom roles with JSON permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique role ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `name` | VARCHAR(100) | NOT NULL | Role name |
| `permissions` | JSON | NULLABLE | JSON permission definitions |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |

**Relationships:** `organization`, `users` (M2M via `user_role`)

### `user_role` — M2M join table

| Column | Type | Constraints |
|--------|------|-------------|
| `user_id` | INTEGER | FK → users.id ON DELETE CASCADE, PK |
| `role_id` | INTEGER | FK → roles.id ON DELETE CASCADE, PK |

---

## VOC Domain

### `voice_sources` — Raw customer feedback from all channels

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique voice ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `store_id` | INTEGER | FK → stores.id ON DELETE SET NULL, NULLABLE, INDEX | Related store |
| `channel` | VARCHAR(30) | NOT NULL, INDEX | Source channel |
| `source_url` | TEXT | NULLABLE | Original URL |
| `author_name` | VARCHAR(255) | NULLABLE | Reviewer name |
| `content` | TEXT | NOT NULL | Raw feedback text |
| `rating` | FLOAT | NULLABLE | Numeric rating (1-5) |
| `posted_at` | TIMESTAMPTZ | NULLABLE | When original was posted |
| `fetched_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | When data was fetched |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Record creation |

**Enum values for `channel`:** `google_review`, `threads`, `facebook`, `instagram`, `ptt`, `dcard`, `in_store`, `survey`, `email`, `chat`, `phone`, `app`, `news`, `forum`

### `voice_analyses` — AI-analyzed insights from voice sources

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique analysis ID |
| `voice_source_id` | INTEGER | FK → voice_sources.id ON DELETE CASCADE, NOT NULL, INDEX | Parent voice |
| `sentiment` | VARCHAR(20) | NOT NULL, INDEX | Sentiment label |
| `sentiment_score` | FLOAT | NOT NULL | Score -1.0 to +1.0 |
| `emotion` | VARCHAR(50) | NULLABLE | Primary emotion |
| `topic` | VARCHAR(100) | NULLABLE | Classified topic |
| `journey_touchpoint` | VARCHAR(50) | NULLABLE | Customer journey phase |
| `pain_point_score` | FLOAT | NULLABLE | Friction probability 0-1 |
| `intent` | VARCHAR(50) | NULLABLE | Customer intent |
| `need_detected` | TEXT | NULLABLE | Detected customer need |
| `risk_level` | VARCHAR(20) | NULLABLE, INDEX | Risk classification |
| `risk_score` | INTEGER | NULLABLE | Risk 0-100 |
| `analyzed_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Analysis time |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Record creation |

**Enum values for `sentiment`:** `positive`, `neutral`, `negative`
**Enum values for `emotion`:** `joy`, `trust`, `anticipation`, `surprise`, `sadness`, `fear`, `anger`, `disgust`, `frustration`, `confusion`, `disappointment`, `mixed`, `neutral`
**Enum values for `risk_level`:** `low`, `medium`, `high`, `critical`
**Enum values for `intent`:** `complain`, `inquire`, `praise`, `suggest`, `warn`

### `voice_tags` — Tags for categorizing voice data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique tag ID |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Tag name |
| `color` | VARCHAR(7) | DEFAULT '#6366f1' | Hex color code |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |

---

## CX Domain

### `cx_journeys` — End-to-end customer journey records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique journey ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `store_id` | INTEGER | FK → stores.id ON DELETE SET NULL, NULLABLE, INDEX | Store |
| `customer_id` | VARCHAR(100) | NULLABLE, INDEX | Customer identifier |
| `touchpoints` | JSON | NULLABLE | Ordered touchpoint data |
| `satisfaction_score` | FLOAT | NULLABLE | Overall CSAT |
| `effort_score` | FLOAT | NULLABLE | Customer Effort Score |
| `nps_score` | FLOAT | NULLABLE | Net Promoter Score |
| `completed_at` | TIMESTAMPTZ | NULLABLE | Journey completion time |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Record creation |

### `touch_points` — Customer experience touchpoint definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique touchpoint ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `name` | VARCHAR(50) | NOT NULL | Touchpoint name |
| `satisfaction_score` | FLOAT | NULLABLE | Current satisfaction |
| `friction_score` | FLOAT | NULLABLE | Friction level 0-1 |
| `status` | VARCHAR(20) | DEFAULT 'healthy' | Health status |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |
| `updated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), ON UPDATE NOW() | Last update |

**Enum values for `name`:** `search`, `book`, `wait`, `service`, `pay`, `review`, `store_entry`, `product_browsing`, `checkout`, `customer_support`, `mobile_app`, `website`
**Enum values for `status`:** `healthy`, `warning`, `critical`

### `cx_insights` — AI-detected CX insights and anomalies

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique insight ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `store_id` | INTEGER | FK → stores.id ON DELETE SET NULL, NULLABLE, INDEX | Store |
| `touchpoint_id` | INTEGER | FK → touch_points.id ON DELETE SET NULL, NULLABLE, INDEX | Related touchpoint |
| `insight_type` | VARCHAR(50) | NULLABLE, INDEX | Type of insight |
| `description` | TEXT | NULLABLE | Detailed description |
| `severity` | VARCHAR(20) | NULLABLE | Impact severity |
| `detected_at` | TIMESTAMPTZ | NULLABLE | Detection time |
| `resolved_at` | TIMESTAMPTZ | NULLABLE | Resolution time |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Record creation |

**Enum values for `insight_type`:** `friction_detection`, `anomaly`, `trend_shift`, `pattern`, `opportunity`
**Enum values for `severity`:** `low`, `medium`, `high`, `critical`

---

## Brand Domain

### `brand_health` — Daily snapshot of overall brand health

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique snapshot ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `calculated_date` | DATE | NOT NULL, INDEX | Calculation date |
| `brand_score` | FLOAT | NULLABLE | Overall brand score 0-100 |
| `store_health_index` | FLOAT | NULLABLE | Aggregated store health |
| `csat_score` | FLOAT | NULLABLE | Customer Satisfaction 1-5 |
| `resolution_rate` | FLOAT | NULLABLE | Case resolution rate 0-1 |
| `reputation_risk_score` | FLOAT | NULLABLE | Reputation risk 0-100 |
| `brand_momentum` | FLOAT | NULLABLE | Trend momentum score |
| `calculated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Calculation time |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Record creation |

### `store_health` — Per-store health metrics snapshot

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique snapshot ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `store_id` | INTEGER | FK → stores.id ON DELETE CASCADE, NOT NULL, INDEX | Store |
| `calculated_date` | DATE | NOT NULL, INDEX | Calculation date |
| `store_health_score` | FLOAT | NULLABLE | Store health 0-100 |
| `csat_score` | FLOAT | NULLABLE | Store CSAT 1-5 |
| `review_count` | INTEGER | NULLABLE | Total reviews |
| `avg_rating` | FLOAT | NULLABLE | Average rating 1-5 |
| `negative_ratio` | FLOAT | NULLABLE | Negative review ratio |
| `response_rate` | FLOAT | NULLABLE | Response rate 0-1 |
| `resolution_rate` | FLOAT | NULLABLE | Resolution rate 0-1 |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Record creation |

### `brand_alerts` — Brand health alerts and notifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique alert ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `store_id` | INTEGER | FK → stores.id ON DELETE SET NULL, NULLABLE, INDEX | Affected store |
| `alert_type` | VARCHAR(50) | NOT NULL, INDEX | Alert category |
| `severity` | VARCHAR(20) | NOT NULL | Severity level |
| `title` | VARCHAR(500) | NOT NULL | Alert title |
| `description` | TEXT | NULLABLE | Detailed description |
| `is_active` | BOOLEAN | DEFAULT true, NOT NULL, INDEX | Active status |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |
| `resolved_at` | TIMESTAMPTZ | NULLABLE | Resolution time |

**Enum values for `alert_type`:** `operations`, `reputation`, `staffing`, `compliance`, `quality`, `technology`, `general`
**Enum values for `severity`:** `low`, `medium`, `high`, `critical`

---

## Workflow Domain

### `cases` — Customer issue cases and workflow management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique case ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `store_id` | INTEGER | FK → stores.id ON DELETE SET NULL, NULLABLE, INDEX | Affected store |
| `voice_source_id` | INTEGER | FK → voice_sources.id ON DELETE SET NULL, NULLABLE, INDEX | Source voice |
| `title` | VARCHAR(500) | NOT NULL | Case title |
| `description` | TEXT | NULLABLE | Detailed description |
| `status` | VARCHAR(20) | DEFAULT 'new', NOT NULL, INDEX | Case status |
| `priority` | VARCHAR(20) | DEFAULT 'medium', NOT NULL, INDEX | Priority level |
| `assigned_to` | INTEGER | FK → users.id ON DELETE SET NULL, NULLABLE, INDEX | Assignee |
| `created_by` | INTEGER | FK → users.id ON DELETE SET NULL, NULLABLE, INDEX | Creator |
| `resolved_at` | TIMESTAMPTZ | NULLABLE | Resolution time |
| `closed_at` | TIMESTAMPTZ | NULLABLE | Closure time |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |
| `updated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), ON UPDATE NOW() | Last update |

**Enum values for `status`:** `new`, `open`, `in_progress`, `pending`, `resolved`, `closed`
**Enum values for `priority`:** `low`, `medium`, `high`, `critical`

**Relationships:** `voice_source`, `assignee`, `creator`, `timeline`, `attachments`

### `case_timeline` — Audit trail for case actions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique entry ID |
| `case_id` | INTEGER | FK → cases.id ON DELETE CASCADE, NOT NULL, INDEX | Parent case |
| `action` | VARCHAR(100) | NOT NULL | Action type |
| `comment` | TEXT | NULLABLE | Comment body |
| `performed_by` | INTEGER | FK → users.id ON DELETE SET NULL, NULLABLE, INDEX | Actor |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Timestamp |

**Enum values for `action`:** `created`, `assigned`, `status_change`, `comment`, `attachment_added`, `resolved`, `closed`, `reopened`

### `case_attachments` — Files attached to cases

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique attachment ID |
| `case_id` | INTEGER | FK → cases.id ON DELETE CASCADE, NOT NULL, INDEX | Parent case |
| `filename` | VARCHAR(500) | NOT NULL | Original filename |
| `file_url` | TEXT | NOT NULL | Storage URL |
| `uploaded_by` | INTEGER | FK → users.id ON DELETE SET NULL, NULLABLE | Uploader |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Upload time |

---

## Knowledge Domain

### `knowledge_bases` — RAG knowledge base articles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique article ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `category` | VARCHAR(50) | NOT NULL, INDEX | Article category |
| `title` | VARCHAR(500) | NOT NULL | Article title |
| `content` | TEXT | NOT NULL | Markdown content |
| `embedding` | JSON | NULLABLE | Vector embedding data |
| `version` | INTEGER | DEFAULT 1, NOT NULL | Current version number |
| `is_published` | BOOLEAN | DEFAULT false, NOT NULL, INDEX | Publication status |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |
| `updated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), ON UPDATE NOW() | Last update |

**Enum values for `category`:** `customer_service`, `policies`, `operations`, `training`, `compliance`, `crisis_management`, `general`

### `knowledge_versions` — Version history for articles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique version ID |
| `knowledge_base_id` | INTEGER | FK → knowledge_bases.id ON DELETE CASCADE, NOT NULL, INDEX | Parent article |
| `version` | INTEGER | NOT NULL | Version number |
| `content` | TEXT | NOT NULL | Article content at this version |
| `created_by` | INTEGER | FK → users.id ON DELETE SET NULL, NULLABLE | Editor |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Version timestamp |

---

## Competitor Domain

### `competitors` — Tracked competitors

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique competitor ID |
| `org_id` | INTEGER | FK → organizations.id ON DELETE CASCADE, NOT NULL, INDEX | Parent org |
| `name` | VARCHAR(255) | NOT NULL | Competitor name |
| `website` | VARCHAR(500) | NULLABLE | Website URL |
| `industry` | VARCHAR(100) | NULLABLE | Industry classification |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |
| `updated_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), ON UPDATE NOW() | Last update |

**Relationships:** `metrics`, `swots`

### `competitor_metrics` — Time-series competitor metrics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique metric ID |
| `competitor_id` | INTEGER | FK → competitors.id ON DELETE CASCADE, NOT NULL, INDEX | Competitor |
| `google_rating` | FLOAT | NULLABLE | Google Maps rating |
| `review_volume` | INTEGER | NULLABLE | Total review count |
| `sentiment_score` | FLOAT | NULLABLE | Aggregate sentiment |
| `brand_health` | FLOAT | NULLABLE | Brand health score |
| `share_of_voice` | FLOAT | NULLABLE | Share of voice ratio |
| `recorded_at` | TIMESTAMPTZ | SERVER DEFAULT NOW(), INDEX | Recording time |

### `competitor_swot` — SWOT analysis entries

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Unique SWOT ID |
| `competitor_id` | INTEGER | FK → competitors.id ON DELETE CASCADE, NOT NULL, INDEX | Competitor |
| `category` | VARCHAR(20) | NOT NULL, INDEX | SWOT category |
| `description` | TEXT | NOT NULL | Analysis text |
| `created_at` | TIMESTAMPTZ | SERVER DEFAULT NOW() | Creation |

**Enum values for `category`:** `strength`, `weakness`, `opportunity`, `threat`

---

## Migration Strategy

Migrations are managed via **Alembic** with async support. The configuration lives at `backend/alembic/env.py`.

### Creating a Migration
```bash
cd backend
alembic revision --autogenerate -m "description_of_changes"
alembic upgrade head
```

### Key Migration Settings
- `compare_type=True` — Detects column type changes
- `compare_server_default=True` — Detects server default changes
- Async engine via `async_engine_from_config` with NullPool
- All models are auto-discovered via `from models import *` in `env.py`

### Rollback
```bash
alembic downgrade -1     # One version back
alembic downgrade base   # Reset all migrations
```

### Production Considerations
- Always review autogenerated migrations before applying
- Run migrations during deployment before starting new app instances
- Use `alembic check` in CI to detect uncommitted schema changes
- Back up database before running `downgrade` in production
