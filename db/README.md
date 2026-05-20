# Database

PostgreSQL schema and Alembic migrations for agent-gen.ca.

## Apply migrations
```bash
cd db
alembic upgrade head
```

## Migration commands
```bash
alembic current
alembic history
alembic revision --autogenerate -m "describe-change"
alembic upgrade head
alembic downgrade -1
```

## Sprint 1 web3 foundation
Added data structures:
1. `payment_intents`
2. `onchain_transactions`
3. `listing_payment_config`
4. `entitlements`
5. Extended `purchases` with mint/cluster/finality metadata

## Policy
1. Alembic migrations are canonical for runtime schema.
2. `db/schema.sql` mirrors latest migration state for bootstrap environments.
