# Deployment Guide

## 🎯 Overview

| Environment | Frontend | Backend | Database | Domain |
|-------------|----------|---------|----------|--------|
| **Local** | Next.js | FastAPI | Postgres | localhost |
| **Production** | Vercel | Railway | Railway Postgres | agent-gen.ca |

## 🚀 Local Development

```bash
cd /a0/usr/workdir/agent-gen.ca

# Full stack (frontend + backend + db)
docker compose -f deploy/docker-compose.dev.yml up -d

# URLs
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
# DB: localhost:5432 (postgres/password)
```

**Stop:** `docker compose -f deploy/docker-compose.dev.yml down`

## ☁️ Production Deployment

### 1. GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit: Agent-Gen.ca MVP"
git remote add origin https://github.com/YOUR-ORG/agent-gen.ca.git
git push -u origin main
```

### 2. Railway (Backend + Database)

1. [Railway.app](https://railway.app) → New Project
2. **Backend:** Deploy from GitHub `backend/` → Railway auto-detects Python/FastAPI
3. **Database:** Add → Postgres → Link to backend
4. **Variables:**
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ALEMBIC_ENV=production
```

**Railway URLs:**
- Backend: `https://api.agent-gen.ca` (custom domain)
- DB: Railway Postgres

### 3. Vercel (Frontend)

1. [Vercel.com](https://vercel.com) → Import GitHub repo
2. **Root:** `frontend/`
3. **Build:** `npm run build`
4. **Output:** `.next/`
5. **Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://api.agent-gen.ca
```

**Vercel URL:** `https://agent-gen.ca` (custom domain)

## 🌐 Custom Domain (agent-gen.ca)

### Cloudflare Setup
1. **A Record:** `agent-gen.ca` → Vercel IP
2. **CNAME:** `www.agent-gen.ca` → `cname.vercel-dns.com`
3. **A Record:** `api.agent-gen.ca` → Railway IP

### Railway Custom Domain
```
Domain: api.agent-gen.ca
Type: A Record → Railway IP
```

### Vercel Custom Domain
```
Domain: agent-gen.ca
www.agent-gen.ca
```

## 🔄 CI/CD (GitHub Actions)

`deploy/.github/workflows/deploy.yml` auto-deploys:
- Push `main` → Production
- PR → Preview environments

## 🧪 Environment Variables

| Service | Key | Value |
|---------|-----|-------|
| Backend | `DATABASE_URL` | `postgresql://...` |
| Backend | `SECRET_KEY` | `your-256-bit-secret` |
| Frontend | `NEXT_PUBLIC_API_URL` | `https://api.agent-gen.ca` |

## 📋 Production Checklist

- [x] Local stack: `docker compose -f deploy/docker-compose.dev.yml up`
- [ ] GitHub repo created/pushed
- [ ] Railway: backend + postgres deployed
- [ ] Vercel: frontend deployed
- [ ] Custom domains: agent-gen.ca + api.agent-gen.ca
- [ ] HTTPS enforced

## 🔍 Monitoring

- Railway: Built-in logs/metrics
- Vercel: Analytics/Edge Insights
- Sentry: Error tracking (recommended)

---
**Production Ready** | Docker + GitHub Actions + Railway/Vercel