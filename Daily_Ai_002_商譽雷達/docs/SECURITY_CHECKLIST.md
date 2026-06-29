# Sentinel ECXIP — Security Checklist

> **Version:** 1.0.0 | **Date:** 2026-06-29 | **Status:** Enterprise MVP

---

## 1. Authentication & Authorization

### 1.1 JWT Token Security
- [ ] Secret key stored in `.env` (never committed to source control)
- [ ] JWT algorithm set to HS256 with minimum 256-bit key
- [ ] Access token expiry set to 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- [ ] Refresh token expiry set to 7 days (`REFRESH_TOKEN_EXPIRE_DAYS`)
- [ ] Token payload contains only non-sensitive claims (user_id, roles)
- [ ] Tokens verified on every authenticated request via middleware
- [ ] Token blacklist on logout (Redis-based invalidation)
- [ ] Refresh token rotation implemented to prevent replay attacks
- [ ] `iss` and `aud` claims validated to prevent cross-service token misuse

### 1.2 Password Hashing (bcrypt)
- [ ] Passwords hashed with bcrypt (passlib) before storage
- [ ] Salt rounds configured appropriately (minimum 12)
- [ ] Plain-text passwords never logged or returned in API responses
- [ ] Password strength policy enforced (minimum length, complexity)
- [ ] Password reset flow uses time-limited, single-use tokens
- [ ] Account lockout after N failed attempts (rate-limited at endpoint level)

### 1.3 Role-Based Access Control (RBAC)
- [ ] Role hierarchy defined (Admin > Manager > Analyst > Viewer)
- [ ] Permission checks enforced at API middleware level (not just UI)
- [ ] Organization-scoped queries prevent cross-tenant data leakage
- [ ] Least-privilege principle applied to all service accounts
- [ ] Role escalation requires re-authentication

---

## 2. Network & Transport Security

### 2.1 CORS Configuration
- [ ] `CORS_ORIGINS` restricted to known frontend domains only
- [ ] Wildcard (`*`) origins NOT used in production
- [ ] `allow_credentials=True` only for authenticated endpoints
- [ ] Allowed methods restricted to `GET, POST, PUT, DELETE, PATCH`
- [ ] Allowed headers restricted to `Authorization, Content-Type, X-Request-ID`
- [ ] Pre-flight caching configured (max-age) for performance
- [ ] Separate CORS config for development vs production environment

### 2.2 HTTPS / TLS
- [ ] All traffic encrypted with TLS 1.2+ (Nginx reverse proxy)
- [ ] HTTP-to-HTTPS redirect enforced (301)
- [ ] HSTS header set (`Strict-Transport-Security: max-age=31536000`)
- [ ] Certificate renewal automated (Let's Encrypt certbot)
- [ ] HTTP/2 enabled where supported

### 2.3 Rate Limiting (Redis Sliding Window)
- [ ] Global rate limit: 100 requests/min per IP
- [ ] Auth endpoints: 10 requests/min per IP (brute-force protection)
- [ ] AI/LLM endpoints: 20 requests/min per user (cost control)
- [ ] WebSocket connections: max 50 concurrent per user
- [ ] Rate limit headers sent in response (`X-RateLimit-*`)
- [ ] Rate limiter uses Redis for distributed deployment compatibility
- [ ] Burst allowance configured for legitimate spikes

---

## 3. Data Protection

### 3.1 SQL Injection Protection
- [ ] All database queries use SQLAlchemy ORM (parameterized queries)
- [ ] No raw SQL string concatenation with user input
- [ ] Raw SQL queries (if needed) use bind parameters only
- [ ] Database user has minimum required permissions (no DDL for app)
- [ ] Prepared statements used for frequently executed queries

### 3.2 XSS Protection
- [ ] Content-Security-Policy (CSP) header configured via Nginx
- [ ] HTML output properly escaped (Vanilla JS renders via textContent/setAttribute)
- [ ] `data-i18n` attributes sanitized before DOM injection
- [ ] User-generated content sanitized before display (bleach or similar)
- [ ] `X-XSS-Protection: 1; mode=block` header set
- [ ] `X-Content-Type-Options: nosniff` header set

### 3.3 CSRF Considerations for SPA
- [ ] SPA uses JWT in `Authorization: Bearer` header (not cookies)
- [ ] SameSite cookie attribute set to Strict/Lax where cookies are used
- [ ] Token stored in memory or httpOnly cookie (not localStorage for production)
- [ ] CSRF token validation for state-changing operations (POST/PUT/DELETE)
- [ ] Origin and Referer headers validated server-side

### 3.4 Secret Management
- [ ] All secrets in `.env` file (never committed to git)
- [ ] `.env.example` provided without real secrets
- [ ] Secrets rotated periodically (especially SECRET_KEY)
- [ ] Separate secrets for development, staging, and production
- [ ] No secrets hardcoded in source code, Dockerfiles, or CI configs
- [ ] API keys stored as environment variables, not in configuration files

---

## 4. API & WebSocket Security

### 4.1 API Key Management
- [ ] Demo Mode enforces simulated data (no real API keys required)
- [ ] Production Mode validates API keys at startup
- [ ] API keys never exposed in client-side code or logs
- [ ] API key usage tracked and rate-limited per key
- [ ] Graceful degradation when API keys are invalid/missing

### 4.2 WebSocket Security
- [ ] WebSocket connections authenticated via token (passed as query parameter or first message)
- [ ] Connection origin validated against allowed CORS origins
- [ ] Message payload size limits enforced (prevent DoS)
- [ ] Idle connections timed out (heartbeat/keepalive)
- [ ] Maximum connections per user/channel capped
- [ ] No sensitive data broadcast to unauthorized channels

---

## 5. Multi-Tenant Data Isolation

- [ ] All database queries scoped by `organization_id`
- [ ] Organization context extracted from JWT claims
- [ ] Cross-tenant data access prevented at API middleware layer
- [ ] Audit log records tenant context for all operations
- [ ] Database indexes include `organization_id` for query isolation
- [ ] Tenant-level rate limiting enforced

---

## 6. Audit & Monitoring

### 6.1 Audit Logging
- [ ] User authentication events logged (login, logout, failed attempts)
- [ ] Data modification events logged (create, update, delete)
- [ ] API access logs include user_id, IP, user-agent, latency
- [ ] Admin actions require additional audit trail
- [ ] Logs include correlation IDs for request tracing

### 6.2 Security Monitoring
- [ ] Failed authentication alerts (threshold-based)
- [ ] Rate limit breach alerts
- [ ] Unusual access pattern detection (geo-location, time-of-day)
- [ ] API error rate monitoring (4xx vs 5xx)
- [ ] DDoS detection and mitigation strategy

---

## 7. Demo Mode Security Warnings

- [ ] Demo Mode clearly indicated in UI (banner/badge)
- [ ] Demo credentials documented as INSECURE for production
- [ ] Demo data does NOT contain real user information
- [ ] Demo Mode disables external API calls to prevent cost leakage
- [ ] Warning in README: "Demo Mode is NOT suitable for production use"

---

## 8. Production Hardening Recommendations

### 8.1 Infrastructure
- [ ] Use Docker secrets or HashiCorp Vault for production secrets
- [ ] Enable PostgreSQL TLS for database connections
- [ ] Enable Redis AUTH (password protection)
- [ ] Run containers as non-root user (`USER` directive in Dockerfile)
- [ ] Set resource limits on all containers (CPU, memory)
- [ ] Regular vulnerability scanning of Docker images
- [ ] Network segmentation (backend, database, cache on private network)

### 8.2 Application
- [ ] Add `Referrer-Policy: strict-origin-when-cross-origin` header
- [ ] Add `Permissions-Policy` header to restrict browser features
- [ ] Enable gzip/brotli compression at Nginx level
- [ ] Add security-focused npm audit / pip-audit to CI pipeline
- [ ] Implement proper session management (server-side session store)
- [ ] Add CAPTCHA for public-facing forms (registration, password reset)

### 8.3 Compliance Preparation
- [ ] Data retention policy document
- [ ] Privacy policy and terms of service pages
- [ ] GDPR: data export, deletion, consent management
- [ ] SOC 2: access controls, change management, monitoring
- [ ] ISO 27001: ISMS documentation framework

---

## 9. Security Testing

- [ ] Dependency vulnerability scan (`pip-audit`, `npm audit`)
- [ ] SAST (Static Application Security Testing) scan
- [ ] DAST (Dynamic Application Security Testing) on staging
- [ ] Manual penetration testing before production launch
- [ ] Security headers verification (securityheaders.com equivalent)

---

**Last Reviewed:** 2026-06-29  
**Next Review:** Before production deployment
