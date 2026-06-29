# Sentinel AI ECXIP — Deployment Guide

## Prerequisites

| Requirement | Minimum Version | Purpose |
|-------------|----------------|---------|
| Docker | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | Multi-service orchestration |
| Python | 3.12+ | Local development |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Cache, queue, WebSocket pub/sub |

LLM API keys (at least one required):
- OpenAI API key (for GPT-tier analysis)
- Google Gemini API key (for PRO-tier analysis)

---

## Docker Compose Quick Start

### 1. Clone and navigate
```powershell
Set-Location "D:\Ai study\Aisa_AI\Daily_Ai_002_商譽雷達"
```

### 2. Configure environment
```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item docker\.env.example docker\.env
```

Edit `backend\.env` and set required values:
```env
SECRET_KEY=your-random-secret-key-at-least-32-chars
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key
```

### 3. Start all services
```powershell
docker compose -f docker\docker-compose.yml up -d
```

### 4. Verify deployment
```powershell
# Check all services are healthy
docker compose -f docker\docker-compose.yml ps

# Test API health
Invoke-WebRequest http://localhost/api/v1/health | Select-Object -ExpandProperty Content
```

### 5. Access the platform
- **Dashboard:** http://localhost
- **API Docs (Swagger):** http://localhost/docs
- **API Docs (ReDoc):** http://localhost/redoc
- **Backend direct:** http://localhost:8000

---

## Service Descriptions

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| `postgres` | `sentinel_postgres` | 5432 | PostgreSQL 16 with persistent volume |
| `redis` | `sentinel_redis` | 6379 | Redis 7 with AOF persistence, 256MB max memory |
| `backend` | `sentinel_backend` | 8000 | FastAPI with 4 Uvicorn workers |
| `celery_worker` | `sentinel_celery_worker` | — | 4 concurrent workers across 4 queues |
| `celery_beat` | `sentinel_celery_beat` | — | Scheduled task scheduler |
| `frontend` | `sentinel_frontend` | 26117 | Nginx serving static SPA files |
| `nginx` | `sentinel_nginx` | 80 | Reverse proxy routing |

### Celery Queues

| Queue | Purpose | Scheduled Tasks |
|-------|---------|----------------|
| `ingestion` | Web crawling, data fetching | Recurring social crawl (every 15 min) |
| `analysis` | AI analysis, brand health, risk | Voice analysis (every 10 min), Risk alerts (every 5 min), Daily brand health (6 AM), Daily brief (7 AM), Weekly report (Mon 8 AM), Cleanup (Mon 3 AM) |
| `notifications` | Email, push, alert dispatch | — |
| `reports` | Scheduled report generation | — |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/sentinel_ecxip` | Async PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for caching |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery message broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery result store |
| `SECRET_KEY` | *Required* | JWT signing key (min 32 chars) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `CORS_ORIGINS` | `["http://localhost:26117",...]` | Allowed CORS origins (JSON array) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `GEMINI_API_KEY` | — | Google Gemini API key |
| `SENTRY_DSN` | — | Optional Sentry error tracking |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `API_V1_PREFIX` | `/api/v1` | API version prefix |
| `PROJECT_NAME` | `Sentinel AI ECXIP` | App display name |
| `PROJECT_VERSION` | `1.0.0` | App version |

### Docker Compose (`docker/.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | PostgreSQL superuser |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB` | `sentinel_ecxip` | Database name |

---

## Health Check Endpoints

### API Health
```
GET /api/v1/health
```
Returns `200` with database and Redis status when healthy, `503` otherwise.

### Backend Container Health
```bash
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"
```
Interval: 30s, Timeout: 10s, Retries: 3, Start period: 40s

### PostgreSQL Health
```bash
pg_isready -U postgres -d sentinel_ecxip
```

### Redis Health
```bash
redis-cli ping
```

### Celery Worker Health
```bash
celery -A tasks.celery_app inspect ping -d celery@<hostname>
```

### Frontend Health
```bash
wget --quiet --spider http://localhost:80/
```

### Nginx Health
```bash
wget --quiet --spider http://localhost:80/
```

---

## Scaling Considerations

### Vertical Scaling
- **Backend workers:** Increase `--workers` in the backend command (default: 4). Rule of thumb: `(2 × CPU cores) + 1`
- **Celery concurrency:** Increase `--concurrency` (default: 4). Match to CPU cores for CPU-bound tasks
- **PostgreSQL:** Increase `pool_size` in `core/database.py` (default: 20)
- **Redis:** Increase `--maxmemory` (default: 256MB)

### Horizontal Scaling
- Backend can be scaled by running multiple container instances behind nginx using `upstream backend_servers` with `least_conn` load balancing
- Celery workers can be scaled by running additional worker containers
- PostgreSQL requires a separate strategy (read replicas, connection pooling with PgBouncer)
- Redis can use Sentinel or Cluster for HA

### Production Recommendations
- Set `ENVIRONMENT=production` to disable OpenAPI docs on `/docs`
- Use a strong, unique `SECRET_KEY`
- Configure proper CORS origins (not wildcard)
- Enable HTTPS with SSL termination at nginx
- Set up log aggregation (ELK, Loki)
- Configure monitoring (Prometheus + Grafana)
- Set up database backup automation
- Use managed PostgreSQL/Redis services for production

---

## Backup and Restore

### PostgreSQL Backup
```powershell
# Full dump
docker exec sentinel_postgres pg_dump -U postgres sentinel_ecxip > backup_$(Get-Date -Format 'yyyyMMdd').sql

# Compressed
docker exec sentinel_postgres pg_dump -U postgres -Fc sentinel_ecxip > backup_$(Get-Date -Format 'yyyyMMdd').dump
```

### PostgreSQL Restore
```powershell
# From SQL dump
Get-Content backup_20260629.sql | docker exec -i sentinel_postgres psql -U postgres sentinel_ecxip

# From compressed dump
docker exec -i sentinel_postgres pg_restore -U postgres -d sentinel_ecxip < backup_20260629.dump
```

### Redis Backup
Redis data is persisted via AOF (`--appendonly yes`) at `/data/appendonly.aof` in the `redis_data` volume.

### Docker Volume Backup
```powershell
# Backup volumes
docker run --rm -v sentinel_postgres_data:/data -v $PWD/backups:/backup alpine tar czf /backup/postgres_$(Get-Date -Format 'yyyyMMdd').tar.gz -C /data .

# Restore volumes
docker run --rm -v sentinel_postgres_data:/data -v $PWD/backups:/backup alpine tar xzf /backup/postgres_20260629.tar.gz -C /data
```

---

## Local Development Setup

### 1. Start infrastructure only
```powershell
docker compose -f docker\docker-compose.yml up -d postgres redis
```

### 2. Setup Python environment
```powershell
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure environment
```powershell
Copy-Item .env.example .env
# Edit .env to use localhost for DB and Redis
```

### 4. Run migrations
```powershell
alembic upgrade head
```

### 5. Start development server
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start Celery worker (separate terminal)
```powershell
celery -A tasks.celery_app worker --loglevel=info --concurrency=2
```

### 7. Serve frontend
```powershell
# From project root
python -m http.server 26117
```

---

## Useful Commands

### View logs
```powershell
docker compose -f docker\docker-compose.yml logs -f backend
docker compose -f docker\docker-compose.yml logs -f celery_worker
```

### Restart a service
```powershell
docker compose -f docker\docker-compose.yml restart backend
```

### Run database migrations in Docker
```powershell
docker exec sentinel_backend alembic upgrade head
```

### Create a new migration
```powershell
Set-Location backend
alembic revision --autogenerate -m "add_new_feature_table"
```

### Enter PostgreSQL shell
```powershell
docker exec -it sentinel_postgres psql -U postgres sentinel_ecxip
```

### Enter Redis CLI
```powershell
docker exec -it sentinel_redis redis-cli
```

### Clear Redis cache
```powershell
docker exec sentinel_redis redis-cli FLUSHALL
```

### Reset everything
```powershell
docker compose -f docker\docker-compose.yml down -v
docker compose -f docker\docker-compose.yml up -d
```
