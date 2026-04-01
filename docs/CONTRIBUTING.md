# Contributing Guide

Thanks for your interest in contributing to **Agent-Gen.ca**! 🎉

## 🤝 Development Workflow

### Prerequisites
```bash
# Node.js 20+, Python 3.12+, Docker, pnpm
pnpm install -g pnpm
pip install -e ./backend[dev]
```

### Local Setup
```bash
# Full stack development
docker compose -f deploy/docker-compose.dev.yml up -d

# Backend dev
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend dev
cd frontend
pnpm dev
```

## 🐛 Development Workflow

```mermaid
flowchart TD
    A[git checkout -b feature/agent-marketplace] --> B[code + tests]
    B --> C[git commit -m feat(agents): add marketplace listing]
    C --> D[git push origin feature/agent-marketplace]
    D --> E[Create PR]
    E --> F[CI passes + review]
    F --> G[Merge to main]
    G --> H[Deploy! 🚀]
```

### Commit Messages (Conventional Commits)
```bash
# Examples
git commit -m "feat(agents): add marketplace listing"
git commit -m "fix(auth): siwe signature validation"
git commit -m "docs(deploy): update railway guide"
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🧪 Testing

### Backend
```bash
cd backend
pytest tests/ -v
```

### Frontend
```bash
cd frontend
pnpm test
pnpm build
```

### E2E
```bash
# Full stack tests
docker compose -f deploy/docker-compose.test.yml up --abort-on-container-exit
```

## 🔄 Pull Requests

1. **Branch:** `feat/short-description` or `fix/issue-number`
2. **Template:** Use `.github/PULL_REQUEST_TEMPLATE.md`
3. **Checklist:**
   - [ ] Tests pass
   - [ ] Linting passes
   - [ ] Docs updated
   - [ ] No breaking changes
4. **Review:** 1 approval → Auto-merge

## 📦 Release Process

**GitHub Actions** auto-releases on `main`:

```yaml
# .github/workflows/release.yml
on:
  push:
    tags: ['v*']
jobs:
  release:
    # npm publish, docker push, changelog
```

## 🤖 Agent Zero Workflow

This project follows [web-app-workflow](AGENT-ZERO.md):
```bash
call_subordinate(profile="orchestrator", message="enhance agent-gen.ca [feature]")
```

## 📚 Code Style

- **Backend:** Black, isort, mypy
- **Frontend:** ESLint, Prettier, TypeScript
- **Commits:** Conventional Commits

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/org/agent-gen.ca/issues)
- **Discord:** #agent-gen-ca
- **Docs:** [docs/](README.md)

---

**Happy coding!** 👨‍💻