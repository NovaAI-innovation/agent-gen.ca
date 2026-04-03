# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**agent-gen.ca** is a full-stack AI Agent Marketplace where users buy/sell MCP servers, agent skills, custom agents, and packs using Solana wallets. Authentication is Solana-wallet-based (SIWE with ed25519 signatures), not username/password.

**Stack:** Next.js 15 (App Router) + FastAPI + PostgreSQL 16 + Solana/Phantom wallet

## Commands

### Frontend (`cd frontend`)
```bash
npm run dev       # Dev server on :3000
npm run build     # Production build
npm run lint      # ESLint
```

### Backend (`cd backend`)
```bash
pip install -e .[dev]                        # Install with dev tools
uvicorn app.main:app --reload --port 8000    # Dev server
pytest -v                                    # Run tests
black . && isort .                           # Format
mypy .                                       # Type check
```

### Database (`cd db`)
```bash
alembic upgrade head                          # Apply migrations
alembic revision --autogenerate -m "message"  # New migration
```

### Full Stack
```bash
docker compose -f deploy/docker-compose.dev.yml up -d
```

## Architecture

### Monorepo Layout
- `frontend/` — Next.js 15 App Router, TypeScript, Tailwind v4
- `backend/` — FastAPI with async SQLAlchemy 2.0
- `db/` — Alembic migrations, PostgreSQL schema
- `deploy/` — Docker Compose (dev/prod), nginx, GitHub Actions
- `docs/` — Architecture, API docs, deployment guides

### Authentication Flow
Solana SIWE (Sign-In With Ethereum adapted for Solana):
1. Frontend requests a nonce from `GET /auth/challenge`
2. Backend stores nonce with 5-minute TTL in `auth_nonces` table
3. User signs message with Phantom wallet (ed25519)
4. `POST /auth/verify` validates ed25519 signature, issues JWT (HS256, 24h)
5. JWT stored in localStorage via Zustand `authStore` with persistence

### Frontend State & Data Fetching
- **Zustand** (`authStore`): persisted auth state (JWT token + user object)
- **TanStack React Query**: all server data fetching (30s stale time)
- **Axios** (`lib/api.ts`): configured with `NEXT_PUBLIC_API_URL`, token injected via interceptor
- Next.js 15 uses React 19 — some libraries may have compatibility quirks

### Backend Structure
- `app/main.py` — FastAPI app, CORS config, startup (creates tables), router registration
- `app/routers/` — `auth.py`, `users.py`, `listings.py`, `marketplace.py`, `purchases.py`, `reviews.py`
- `app/models/` — SQLAlchemy ORM models (async)
- `app/deps.py` — `get_current_user()` dependency for protected routes
- All DB sessions are async (asyncpg driver)

### Data Model
Four listing types via enum: `mcp_server`, `agent_skill`, `custom_agent`, `pack`

Key tables: `users` (wallet_address UNIQUE), `listings` (slug UNIQUE, price_sol NUMERIC), `listing_versions` (config_json JSONB), `auth_nonces` (ephemeral), `reviews`, `purchases`

### Deployment
- **Frontend**: Vercel
- **Backend**: Railway
- **Database**: Railway PostgreSQL
- CI/CD: GitHub Actions (`.github/workflows/deploy.yml`) — test → build Docker images → deploy on push to `main`

## Key Conventions

- Listing prices are in SOL (Solana), stored as `NUMERIC(18,9)`
- Wallet addresses are Solana base58 strings, not Ethereum hex
- `listing_versions.config_json` is JSONB — store MCP server configs, agent skill definitions, etc. here
- Frontend uses Tailwind v4 with custom neon CSS variables (cyan/amber/lime/purple palette defined in `globals.css`)
- Next.js config includes Webpack polyfills for `Buffer` and `process` — required for Solana Web3.js in browser
