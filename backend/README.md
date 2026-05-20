# agent-gen.ca backend

FastAPI API for wallet auth, listings, reviews, marketplace, and purchase flows.

## Setup
```bash
cd backend
pip install -e .[dev]
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Prerequisites
1. PostgreSQL running and reachable by `DATABASE_URL`
2. Migrations applied from `db/`:
```bash
cd ../db
alembic upgrade head
```

## Auth flow
1. `GET /auth/challenge`
2. Wallet signs SIWS-style message
3. `POST /auth/verify`
4. Access token + refresh cookie issued

## Notes
1. `ENFORCE_ALEMBIC_VERSION=true` makes startup fail fast when migration state is missing/mismatched.
2. Rate limits are enforced on challenge/verify/refresh endpoints.
