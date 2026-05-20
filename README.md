# agent-gen.ca

Monorepo for the agent-gen marketplace:
1. `frontend/` - Next.js App Router client
2. `backend/` - FastAPI API
3. `db/` - PostgreSQL schema and Alembic migrations
4. `deploy/` - local/prod Docker Compose and nginx

## Current implementation status
Sprint 1 foundation is in progress:
1. Solana wallet auth is live (ed25519 challenge/verify).
2. SIWS-style challenge format and auth hardening are enabled.
3. Payment verification tables are present for Sprint 2 on-chain execution.

## Local development
1. Start infrastructure:
```bash
docker compose -f deploy/docker-compose.dev.yml --env-file deploy/.env.dev up -d
```
2. Run migrations:
```bash
cd db
alembic upgrade head
```
3. Frontend:
```bash
cd frontend
npm install
npm run dev
```
4. Backend:
```bash
cd backend
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

## Web3 config contract
Backend env:
1. `SOLANA_CLUSTER`
2. `SOLANA_RPC_HTTP`
3. `SOLANA_RPC_WS`
4. `SOLANA_RPC_FALLBACK`
5. `USDC_MINT`
6. `PLATFORM_FEE_BPS`

Frontend env:
1. `NEXT_PUBLIC_SOLANA_CLUSTER`
2. `NEXT_PUBLIC_SOLANA_RPC_HTTP`
3. `NEXT_PUBLIC_SOLANA_RPC_WS`
4. `NEXT_PUBLIC_SOLANA_RPC_FALLBACK`
5. `NEXT_PUBLIC_USDC_MINT`
6. `NEXT_PUBLIC_PLATFORM_FEE_BPS`
