# Architecture

## System overview
agent-gen.ca is a marketplace for agent listings with Solana wallet-native auth and upcoming on-chain purchase verification.

## Components
1. Frontend (`frontend/`)
   1. Next.js App Router (React 19 + TypeScript)
   2. Solana wallet adapter integration for wallet connect and message signing
   3. React Query + Zustand state management
2. Backend (`backend/`)
   1. FastAPI + async SQLAlchemy
   2. Wallet challenge/verify authentication
   3. JWT access tokens + refresh cookie sessions
   4. Marketplace, listing, review, and purchase APIs
3. Database (`db/`)
   1. PostgreSQL schema
   2. Alembic migrations as source of truth
4. Runtime (`deploy/`)
   1. Docker Compose dev/prod profiles
   2. nginx reverse proxy in production profile

## Auth model
1. Frontend requests challenge: `GET /auth/challenge?wallet=<base58_pubkey>`
2. Backend returns SIWS-style message and challenge metadata.
3. Wallet signs message with `signMessage`.
4. Frontend submits signature to `POST /auth/verify`.
5. Backend verifies ed25519 signature and issues:
   1. access JWT (bearer token)
   2. refresh cookie (HttpOnly)

## Solana integration approach
MVP payment flows use native programs:
1. System Program (SOL)
2. SPL Token Program
3. Token-2022 Program
4. Associated Token Account Program
5. Memo Program
6. Compute Budget Program

Custom Anchor program support is deferred until escrow/dispute requirements are confirmed.

## Web3 data model (Sprint 1 foundation)
1. `payment_intents` for expected recipient/mint/amount and idempotency.
2. `onchain_transactions` for observed signature metadata and confirmation state.
3. `listing_payment_config` for per-listing payout wallet and fee policy.
4. `entitlements` for post-verification access grants.
5. `purchases` extended with mint, lamports, cluster, confirmation metadata.

## Security controls
1. Rate limiting on challenge/verify/refresh auth endpoints.
2. JWT issuer and audience validation.
3. Session-backed refresh token rotation.
4. Request metadata hashing in auth audit logs.

## Configuration contract
Reference: [ADR-0001-solana-foundation.md](/C:/Users/casey/agent-gen.ca/docs/ADR-0001-solana-foundation.md)
