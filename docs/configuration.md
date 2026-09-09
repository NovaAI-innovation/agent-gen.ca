# Configuration Contract

Every environment variable that affects runtime behavior is listed here. The backend and frontend share a consistent set of variable names, defaults, and validation rules.

## Environment

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `ENVIRONMENT` | both | `development` | `development` or `production`. Controls validation strictness. |

## Database

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `DATABASE_URL` | backend | `postgresql+asyncpg://agentgen:agentgen123@localhost:5432/agentgen` | PostgreSQL connection string. Production MUST use a non-loopback host. |

## Redis

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `REDIS_URL` | backend | `redis://localhost:6379` | Redis for rate limiting, sessions, and job queues. Production MUST use a non-loopback host. |

## Security

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `SECRET_KEY` | backend | `change-in-production` | JWT signing key. Production MUST set a real secret. |
| `ALGORITHM` | backend | `HS256` | JWT algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | backend | `1440` (24h) | Access token lifetime. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | backend | `30` | Refresh token lifetime. |
| `MAX_ACTIVE_SESSIONS_PER_USER` | backend | `3` | Max concurrent sessions per wallet. |
| `NONCE_EXPIRE_MINUTES` | backend | `5` | Sign-in challenge nonce TTL. |

## Cookies

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `REFRESH_COOKIE_NAME` | backend | `refresh_token` | Refresh cookie name. |
| `REFRESH_COOKIE_SECURE` | backend | `true` | Secure flag. Production MUST be `true`. |
| `REFRESH_COOKIE_SAMESITE` | backend | `strict` | SameSite attribute. One of `lax`, `strict`, `none`. |
| `REFRESH_COOKIE_DOMAIN` | backend | (none) | Cookie domain. |

## CORS

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `ALLOWED_ORIGINS` | backend | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated allowed origins. |

## Rate limits

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `AUTH_RATE_LIMIT_CHALLENGE` | backend | `20/minute` | Challenge endpoint limit. |
| `AUTH_RATE_LIMIT_VERIFY` | backend | `10/minute` | Verify endpoint limit. |
| `AUTH_RATE_LIMIT_REFRESH` | backend | `30/minute` | Refresh endpoint limit. |

## JWT claims

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `JWT_ISSUER` | backend | `agent-gen.ca` | JWT `iss` claim. |
| `JWT_AUDIENCE` | backend | `agent-gen.ca-web` | JWT `aud` claim. |
| `JWT_LEEWAY_SECONDS` | backend | `30` | Clock skew tolerance. |

## SIWS authentication

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `AUTH_DOMAIN` | backend | `agent-gen.ca` | Domain verified in the signed message. |
| `AUTH_URI` | backend | `https://agent-gen.ca` | URI verified in the signed message. |
| `AUTH_CHAIN_ID` | backend | `solana:mainnet` | Chain identifier in the signed message. |
| `AUTH_STATEMENT` | backend | `Sign in to agent-gen.ca` | Human-readable statement. |

## Solana

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `SOLANA_CLUSTER` | both | `mainnet-beta` | One of `localnet`, `devnet`, `mainnet-beta`. Production MUST NOT be `localnet`. |
| `SOLANA_RPC_HTTP` | both | `https://api.mainnet-beta.solana.com` | Primary JSON-RPC HTTP endpoint. Production MUST use a non-loopback host. |
| `SOLANA_RPC_WS` | both | `wss://api.mainnet-beta.solana.com` | Primary JSON-RPC WebSocket endpoint. |
| `SOLANA_RPC_FALLBACK` | both | (none) | Comma-separated fallback RPC endpoints. |

Frontend equivalents are prefixed with `NEXT_PUBLIC_`:
- `NEXT_PUBLIC_SOLANA_CLUSTER`
- `NEXT_PUBLIC_SOLANA_RPC_HTTP`
- `NEXT_PUBLIC_SOLANA_RPC_WS`
- `NEXT_PUBLIC_SOLANA_RPC_FALLBACK`

## Payments (Release B)

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `USDC_MINT` | backend | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | USDC token mint address. |
| `PLATFORM_FEE_BPS` | backend | `250` | Platform fee in basis points (0–10000). |
| `NEXT_PUBLIC_USDC_MINT` | frontend | (same) | Public USDC mint for checkout UI. |
| `NEXT_PUBLIC_PLATFORM_FEE_BPS` | frontend | `250` | Public fee display. |

## Migrations

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `ENFORCE_ALEMBIC_VERSION` | backend | `false` | When `true`, refuse to start if the DB revision does not match. |
| `ALEMBIC_EXPECTED_REVISION` | backend | (none) | Expected Alembic revision hash. |

## Frontend

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | frontend | `http://localhost:8000` | Backend API base URL. In production behind the edge proxy, use `/api`. |

## Production validation rules

When `ENVIRONMENT=production`, the following are enforced at startup:

**Backend (FastAPI):**
1. `SECRET_KEY` must not be a known placeholder.
2. `DATABASE_URL` must not point to a loopback address.
3. `REDIS_URL` must not point to a loopback address.
4. `SOLANA_RPC_HTTP` must not point to a loopback address.
5. `SOLANA_CLUSTER` must not be `localnet`.
6. `REFRESH_COOKIE_SECURE` must be `true`.

**Frontend (Next.js build):**
1. `NEXT_PUBLIC_SOLANA_CLUSTER` must not be `localnet`.
2. `NEXT_PUBLIC_SOLANA_RPC_HTTP` must not point to a loopback address.

If any rule fails, the process refuses to start or build.
