# Auth Abuse Controls — Runbook

Quick reference for diagnosing and responding to authentication abuse.

## Architecture

```
Client → nginx (rate limit zones) → FastAPI (slowapi limits) → handler
```

**Two layers of rate limiting:**

1. **nginx** — Per-endpoint rate limit zones (`auth_challenge`, `auth_verify`, `auth_refresh`) using `$binary_remote_addr`. These run before proxying to the backend and block at the edge. Limits are shared across nginx workers via shared memory zones.

2. **FastAPI slowapi** — Route decorators (`@limiter.limit(...)`) on `/auth/challenge`, `/auth/verify`, `/auth/siws/verify`, and `/auth/refresh`. When `REDIS_URL` points to a non-localhost Redis (production), limits are shared across API workers. Locally, in-memory storage is used.

## Limit Configuration

| Endpoint | nginx rate | nginx burst | slowapi rate | 
|----------|-----------|-------------|--------------|
| `/auth/challenge` | 20r/m | 5 | `AUTH_RATE_LIMIT_CHALLENGE` (default 20/minute) |
| `/auth/verify` + `/auth/siws/verify` | 10r/m | 3 | `AUTH_RATE_LIMIT_VERIFY` (default 10/minute) |
| `/auth/refresh` | 30r/m | 5 | `AUTH_RATE_LIMIT_REFRESH` (default 30/minute) |
| General `/api/` | 120r/m | 20 | (none) |

All limits are per-client-IP. 429 responses include `Retry-After` and `X-RateLimit-*` headers.

## Client IP Trust Model

- **Production:** Set `TRUST_PROXY_IP` to the nginx container IP (e.g. `TRUST_PROXY_IP=10.0.0.4`). The backend then trusts X-Forwarded-For only when the immediate peer matches.
- **Local dev:** `TRUST_PROXY_IP` is unset; any peer is trusted. X-Forwarded-For works for local testing.

## Observing Abuse

### Slowapi 429s (backend)
```bash
# nginx access log shows 429 from upstream
grep '429' /var/log/nginx/access.log

# Backend logs show rate limit exceeded
2026-09-09T16:30:00Z WARNING Rate limit exceeded: 20/minute for client IP 203.0.113.9
```

### Nginx 429s (edge)
```bash
grep '429' /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn
```

### Audit events
Login failures, locked accounts, and repeated 429s are recorded in `auth_audit_events` with `event_type` values: `login_failed`, `siws_login_success`, `refresh_success`, `logout`, `logout_all`.

## Response Procedures

### Triage a 429 spike

1. **Check which endpoint:** Look at the request path in nginx or backend logs.
2. **Identify the IP:** The `X-RateLimit-Remaining: 0` response header or the client IP in logs.
3. **Determine intent:**
   - Single wallet retrying → likely a bad UX loop; not abuse.
   - Many wallets from one IP → automated enumeration attempt.
   - Distributed across IPs → may need Cloudflare or WAF upstream.

### Adjust limits in production

1. Update `backend/.env` with new rate values (e.g. `AUTH_RATE_LIMIT_VERIFY=5/minute`).
2. Restart the API container.
3. Update nginx `limit_req_zone` rates in `deploy/nginx/conf.d/default.conf` and reload nginx.

```bash
docker compose exec nginx nginx -s reload
```

### Block a specific IP at the edge

Add a block in the nginx `server` block before the location blocks:

```nginx
if ($remote_addr = "203.0.113.9") {
    return 403;
}
```

Or use iptables on the host:

```bash
iptables -A INPUT -s 203.0.113.9 -j DROP
```

## Verifying Limits

```bash
# Test challenge rate limit (should get 429 after 20 requests)
for i in $(seq 1 25); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    "http://localhost:8000/auth/challenge?wallet=6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73"
done | sort | uniq -c
```

Expected output:
```
20 200
 5 429
```

## Deployment Notes

- `memory://` fallback means limits are **per-worker** locally. Two uvicorn workers = each has its own counter. Production Redis storage avoids this.
- Add `TRUST_PROXY_IP` to the production `.env` when deploying behind nginx.
- `headers_enabled=True` means rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) are sent on every response, not just 429s.