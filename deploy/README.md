# Deployment Notes

## Development profile
```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev up -d --build
```

Services:
1. Frontend: `http://localhost:3000`
2. Backend: `http://localhost:8000`
3. Postgres: `localhost:5432`
4. PgAdmin: `http://localhost:8080`

## Production-like profile
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

Proxy entrypoint:
1. App: `http://localhost:3000`
2. API through nginx: `http://localhost:3000/api`

## Important
1. Apply `db` migrations before enabling strict migration checks in backend.
2. Keep Solana cluster and RPC values aligned between backend and frontend env files.
