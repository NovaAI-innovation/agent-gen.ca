# 🚀 agent-gen.ca Deployment Guide

## 📋 Overview

**Stack:** Next.js 15 (frontend:3000) + FastAPI (backend:8000) + PostgreSQL (5432)
**Production:** nginx(80/443) → Vercel(frontend) + Railway(backend+db)
**Monorepo:** GitHub → GHCR → Railway/Vercel

## 🏠 Local Development

```bash
cd /a0/usr/workdir/agent-gen.ca/deploy
cp .env.dev .env
ln -s ../db migrations

docker compose -f docker-compose.dev.yml up -d
```

**Ports:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/health
- DB: localhost:5432 (agentgen/agentgen123)
- PgAdmin: http://localhost:8080 (admin@agent-gen.ca/admin123)

## 🔧 Production Local

```bash
cp .env.prod .env
mkdir -p certs
# Copy SSL certs to certs/

docker compose -f docker-compose.prod.yml up -d
```

**Test:** curl http://localhost/health, http://localhost/api/health

## ☁️ Cloud Deployment

### 1. GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/agent-gen.ca.git
git push -u origin main
```

### 2. GitHub Secrets
**Settings → Secrets & variables → Actions:**
- `RAILWAY_TOKEN`: Railway API token
- `RAILWAY_BACKEND_SERVICE_ID`: Backend service ID
- `VERCEL_TOKEN`: Vercel API token
- `VERCEL_PROJECT_ID`: Frontend project ID
- `ORG_ID`: Vercel org ID

### 3. Railway (Backend + DB)
```bash
npm i -g @railway/cli
railway login
railway init
railway link YOUR_PROJECT_ID
railway up
```

**env vars:** DATABASE_URL, POSTGRES_PASSWORD, SECRET_KEY

### 4. Vercel (Frontend)
```bash
npm i -g vercel
vercel login
vercel --prod
```

**env vars:** NEXT_PUBLIC_API_URL=https://api.agent-gen.ca

## ✅ Health Checks

```bash
# Backend
curl https://api.agent-gen.ca/health

# Frontend
curl https://agent-gen.ca/api/health

# DB (psql)
psql $DATABASE_URL -c "SELECT 1;"
```

## 🔄 CI/CD

Push to `main` → GitHub Actions:
1. ✅ Tests (pytest, eslint, black)
2. 🐳 Docker build → GHCR
3. 🚀 Deploy Railway backend
4. 🌐 Deploy Vercel frontend

## 📊 Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://agent-gen.ca |
| API | https://api.agent-gen.ca |
| Docs | https://agent-gen.ca/docs |
| Health | https://api.agent-gen.ca/health |

## 🛠️ Troubleshooting

**DB Migration:** `poetry run alembic upgrade head`
**Rebuild:** `docker compose down -v && docker compose up -d`
**Logs:** `docker compose logs -f`

---

**Phase 6 ✅ Production Ready**

**Full stack up:** `cd deploy && docker compose -f docker-compose.dev.yml up -d`

**Next:** Phase 7 `web-documentation` (README + API docs)
