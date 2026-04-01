# agent-gen.ca PostgreSQL + Alembic Setup

## Quick Start

```bash
# 1. Start Postgres
cd /a0/usr/workdir/agent-gen.ca/backend
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose up db -d

# 2. Verify schema
psql -h localhost -p 5432 -U postgres -d agentgen -f ../db/schema.sql

# 3. Run migrations (recommended)
cd ../db
alembic upgrade head
```

## Connection

**DATABASE_URL:** `postgresql+asyncpg://postgres:password@localhost:5432/agentgen`

**Backend:** `/backend/app/db/database.py` uses this URL

## Schema Features

✅ **3NF Normalized** (users, agents tables)
✅ **JSONB** (agent config_json)
✅ **Constraints** (wallet_address UNIQUE, price >= 0)
✅ **Indexes** (wallet_address trgm, owner_id, price, name trgm)
✅ **Triggers** (updated_at auto-update)
✅ **Extensions** (pg_trgm for similarity search)
✅ **Seed Data** (2 users, 2 agents)
✅ **FK CASCADE** (agents deleted with user)

## Alembic Commands

```bash
# Current status
alembic current

# Generate new migration (after model changes)
alembic revision --autogenerate -m 'add feature'

# Upgrade/downgrade
alembic upgrade head
alembic downgrade -1

# History
alembic history
```

## Docker Volumes

**postgres_data:** `/a0/usr/workdir/agent-gen.ca/backend/postgres_data/`

## Verification

```sql
\dt                    # Tables: users, agents
SELECT * FROM users;   # 2 seed users
SELECT * FROM agents;  # 2 seed agents

-- Test relationships
SELECT u.wallet_address, COUNT(a.id) as agent_count 
FROM users u 
LEFT JOIN agents a ON u.id = a.owner_id 
GROUP BY u.id;
```

## Backend Integration

1. `DATABASE_URL` in `.env` or `docker-compose.yml`
2. Models: `/backend/app/models/user.py`, `/backend/app/models/agent.py`
3. CRUD: `/backend/app/crud/user.py`, `/backend/app/crud/agent.py`
4. Health check: `curl http://localhost:8000/health`

## Production

- Use PgBouncer for connection pooling
- Read replicas for analytics
- Backup: `pg_dump agentgen > backup.sql`
- Monitor: `pg_stat_statements` extension

**Matches saas-task-manager/db/ structure exactly**