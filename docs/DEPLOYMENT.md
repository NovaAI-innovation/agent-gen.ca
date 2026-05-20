# Deployment

## Local dev stack
1. Start services:
```bash
docker compose -f deploy/docker-compose.dev.yml --env-file deploy/.env.dev up -d --build
```
2. Apply migrations:
```bash
cd db
alembic upgrade head
```
3. Verify:
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

## Production-like local stack
1. Start services:
```bash
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build
```
2. Verify:
```bash
curl http://localhost:3000/api/health
```

## Required backend env
1. `DATABASE_URL`
2. `SECRET_KEY`
3. `ALLOWED_ORIGINS`
4. `JWT_ISSUER`
5. `JWT_AUDIENCE`
6. `REFRESH_COOKIE_SECURE`
7. `REFRESH_COOKIE_SAMESITE`
8. `ENFORCE_ALEMBIC_VERSION`
9. `SOLANA_CLUSTER`
10. `SOLANA_RPC_HTTP`
11. `SOLANA_RPC_WS`
12. `SOLANA_RPC_FALLBACK`
13. `USDC_MINT`
14. `PLATFORM_FEE_BPS`

## Required frontend env
1. `NEXT_PUBLIC_API_URL`
2. `NEXT_PUBLIC_SOLANA_CLUSTER`
3. `NEXT_PUBLIC_SOLANA_RPC_HTTP`
4. `NEXT_PUBLIC_SOLANA_RPC_WS`
5. `NEXT_PUBLIC_SOLANA_RPC_FALLBACK`
6. `NEXT_PUBLIC_USDC_MINT`
7. `NEXT_PUBLIC_PLATFORM_FEE_BPS`

## Migration policy
1. Alembic migrations are the source of truth.
2. Run `alembic upgrade head` before backend startup in environments with `ENFORCE_ALEMBIC_VERSION=true`.
