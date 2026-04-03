# Repository Guidelines

## Project Structure & Module Organization
- `frontend/`: Next.js App Router UI (pages in `src/app`, shared UI in `src/components`, client state in `src/store`, API helpers in `src/lib`).
- `backend/`: FastAPI service (`app/routers`, `app/models`, `app/schemas`, `app/crud`, `app/core`, `app/db`).
- `db/`: SQL schema and Alembic migration source (`migrations/versions`).
- `deploy/`: Docker Compose files and nginx config for local/prod orchestration.
- `docs/`: architecture, API, deployment, and contributor documentation.

## Build, Test, and Development Commands
- Full stack (recommended from repo root):
  - `docker compose -f deploy/docker-compose.dev.yml up -d`
- Frontend (`cd frontend`):
  - `npm install` installs dependencies.
  - `npm run dev` starts Next.js dev server on `:3000`.
  - `npm run lint` runs ESLint.
  - `npm run build` validates production build.
- Backend (`cd backend`):
  - `pip install -e .[dev]` installs API + dev tooling.
  - `uvicorn app.main:app --reload --port 8000` runs API locally.
- Database (`cd db`):
  - `alembic upgrade head` applies migrations.
  - `alembic revision --autogenerate -m "add <feature>"` creates migrations.

## Coding Style & Naming Conventions
- TypeScript/React: strict TS, ESLint (`frontend/eslint.config.mjs`), 2-space indentation, `PascalCase` component files, `camelCase` hooks/stores/utilities.
- Python: PEP 8, 4-space indentation, `snake_case` modules/functions, explicit Pydantic schemas for request/response models.
- Keep concerns separated: routers should stay thin; business/data logic belongs in `crud/` or service helpers.

## Testing Guidelines
- There are currently no committed test suites; new features should include tests.
- Backend tests: place in `backend/tests/` as `test_*.py`; run with `pytest -v`.
- Frontend tests: add `*.test.ts(x)` files when introducing a test runner; at minimum verify `npm run lint` and `npm run build` pass.
- For schema changes, include an Alembic migration and verify `alembic upgrade head` succeeds on a clean DB.

## Commit & Pull Request Guidelines
- Current history is minimal (`Initial commit: ...`), but project docs use Conventional Commits; follow: `feat(scope): summary`, `fix(scope): summary`, etc.
- PRs should include:
  - Clear description of behavior changes.
  - Linked issue/task.
  - UI screenshots/GIFs for frontend changes.
  - Migration notes for DB updates.
  - Evidence of checks run (lint/build/tests).
