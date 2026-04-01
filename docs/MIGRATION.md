# Database Migrations

## 📋 Schema Overview

**Postgres 16** + **Alembic** for zero-downtime migrations.

### Core Tables

```sql
-- User (SIWE Auth)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agents
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Marketplace (Agent Listings)
CREATE TABLE marketplace_listings (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id),
    price DECIMAL,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Full schema:** [db/schema.sql](../db/schema.sql)

## 🔄 Alembic Workflow

### Local Development
```bash
cd backend

# Install
pip install -e .[dev]

# Initial migration
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Production (Railway)
1. Railway Postgres → `DATABASE_URL`
2. Backend deploy auto-runs migrations on startup
3. New migration → PR → Auto-deploy

### Commands
```bash
# Create migration
alembic revision --autogenerate -m "add-agent-price"

# Apply locally
alembic upgrade head

# Rollback
alembic downgrade -1

# Current status
alembic current
```

## 📁 Migration Files

```
db/migrations/
├── env.py
└── versions/
    └── 0001_initial.py  # User + Agent + Marketplace tables
```

**Config:** [alembic.ini](../db/alembic.ini)

## 🧪 Testing Migrations

```bash
# Test upgrade/downgrade
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## 🚨 Production Safety

✅ **Zero-downtime:** Alembic handles column adds/drops safely
✅ **Backup:** Railway Postgres snapshots
✅ **Rollback:** `alembic downgrade -1`
✅ **Schema validation:** Backend startup checks

---

**Reference:** [Alembic Docs](https://alembic.sqlalchemy.org/)