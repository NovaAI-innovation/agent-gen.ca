# Agent Gen CA 👨‍💻🤖

[![Next.js](https://img.shields.io/badge/Next.js-15-blue.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-purple.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-yellow.svg)](https://github.com/features/actions)

**Agent Gen CA** is a full-stack AI agent marketplace built with the [Agent Zero web-app-workflow](https://github.com/blade-runner/A0). 

Cyber-themed UI (Next.js 15 + Tailwind), secure FastAPI backend with SIWE auth, Postgres + Alembic, production Docker deployment.

## ✨ Features

- **Agent Marketplace** - Browse, purchase, deploy AI agents
- **SIWE Authentication** - Wallet-based secure login
- **Cyber UI** - Dark mode, neon accents, responsive design
- **Production Ready** - Docker, GitHub Actions, Railway/Vercel deploy
- **Agent Zero Integration** - Built using web-app-workflow phases 1-7

## 🛠 Tech Stack

| Frontend | Backend | Database | DevOps |
|----------|---------|----------|--------|
| Next.js 15 | FastAPI | PostgreSQL 16 | Docker |
| Tailwind CSS | Pydantic | Alembic | GitHub Actions |
| TypeScript | SQLAlchemy | | Railway/Vercel |

```mermaid
graph TB
    FE[Next.js 15 Frontend] --> BE[FastAPI Backend]
    BE --> DB[Postgres + Alembic]
    FE -.->|SIWE Auth| BE
    subgraph Deploy
        DC[Docker Compose]
        GH[GitHub Actions]
        R[Railway]
        V[Vercel]
    end
    DC --> R
    DC --> V
    GH --> DC
```

## 🚀 Quickstart (Development)

```bash
# Clone & Install
git clone <repo> agent-gen.ca
cd agent-gen.ca

# Start full stack (frontend + backend + db)
docker compose -f deploy/docker-compose.dev.yml up -d

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
# DB: localhost:5432 (user: postgres, pass: password)
```

## 📚 Documentation

- [Architecture](./ARCHITECTURE.md)
- [API Docs](./API-DOCS.md)
- [Deployment](./DEPLOYMENT.md)
- [Agent Zero Workflow](./AGENT-ZERO.md)
- [Database](./MIGRATION.md)
- [Contributing](./CONTRIBUTING.md)

## 🏗 Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Railway + Vercel + Custom Domain setup.

## 🎯 Next Steps

- [ ] GitHub Repository
- [ ] Railway (backend + db)
- [ ] Vercel (frontend)
- [ ] Custom Domain: agent-gen.ca

---

**Built with Agent Zero [web-app-workflow](https://github.com/blade-runner/A0)** | **Phase 7 ✅ FULL PROJECT DOCUMENTATION COMPLETE**