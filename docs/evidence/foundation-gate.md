# Foundation Gate Evidence

Gate: FND-005
Date: 2026-09-09
Branch: `main` (merge of FND-001 through FND-004)
Status: ✅ PASSED

## Verification summary

All three foundation contracts pass together on a clean checkout.

| Contract | Story | Verification | Result |
|----------|-------|-------------|--------|
| Configuration | FND-002 | `pytest backend/tests/test_config.py` | 19/19 passed |
| Design system | FND-003 | `npm run lint` + `npm run build` | 0 errors, 16/16 pages |
| CI harness | FND-004 | `npm test -- --run` + `pytest` | 6/6 frontend, 19/19 backend |

## Configuration contract (FND-002)

### Backend validation

- **Placeholder secrets rejected in production:** SECRET_KEY must not be `change-in-production`, `change-me`, or other known placeholders.
- **Loopback URLs rejected in production:** DATABASE_URL, REDIS_URL, SOLANA_RPC_HTTP must not point to localhost/127.0.0.1/::1.
- **Cluster validation:** SOLANA_CLUSTER must be one of `localnet`, `devnet`, `mainnet-beta`. Production must not use `localnet`.
- **Cookie security:** REFRESH_COOKIE_SECURE must be `true` in production.
- **Fee bounds:** PLATFORM_FEE_BPS must be between 0 and 10000.
- **SameSite validation:** REFRESH_COOKIE_SAMESITE must be `lax`, `strict`, or `none`.

### Frontend validation

- **Cluster validation:** NEXT_PUBLIC_SOLANA_CLUSTER must be one of `localnet`, `devnet`, `mainnet-beta`.
- **Production guards:** `localnet` cluster and loopback RPC URLs are rejected in production.
- **Typed config:** Centralized `frontend/src/lib/config.ts` exports `AppConfig` interface. Solana config delegates to it.

### Documentation

- `docs/configuration.md` documents all environment variables, scopes, defaults, and production rules.
- `backend/.env.example` and `frontend/.env.example` list every variable with descriptions.

## Design system (FND-003)

### Semantic tokens

All tokens defined as CSS custom properties in `globals.css`:

- **Surfaces:** page, elevated, muted, hover, accent, overlay
- **Text:** primary (94% lightness), secondary (77%), muted (58%), on-action
- **Actions:** primary (cyan), primary-fg, primary-hover, secondary, secondary-fg
- **Feedback/status:** success, warning, danger, info — each with solid and muted variants
- **Borders:** subtle, strong, focus, error
- **Typography:** 8-step scale (xs through 4xl), tight/normal/relaxed line heights, tight/wide letter spacing
- **Spacing:** 10-step scale at 4px base (space-1 through space-12)
- **Radii:** sm, md, lg, xl, full
- **Motion:** fast (120ms), normal (200ms), slow (350ms), ease-out, ease-in-out
- **Focus ring:** 2px width, 2px offset, cyan-400 color
- **Shadows:** neon (primary glow), elevated (dark shadow)

### Components

| Component | File | Variants | Key accessibility |
|-----------|------|----------|-------------------|
| Button | `ui/Button.tsx` | primary, secondary, ghost, danger × sm, md, lg, icon | Focus ring, aria-disabled, aria-busy (loading), Slot compatibility |
| Field | `ui/Field.tsx` | — | aria-describedby, aria-invalid, aria-required, label/error/hint linking |
| StatusBadge | `ui/StatusBadge.tsx` | 10 statuses | role="status", aria-label, animated dot for pending states |
| Alert | `ui/Alert.tsx` | info, success, warning, danger | role="alert", dismissible, SVG icons |
| Panel | `ui/Panel.tsx` | default, accent, muted × none, sm, md, lg | — |
| Skeleton | `ui/Skeleton.tsx` | shimmer, pulse, none + Card/Row layouts | aria-hidden |

### Accessibility

- `prefers-reduced-motion` disables all animations
- `:focus-visible` uses ring tokens on all focusable elements
- All interactive components use semantic HTML and ARIA attributes
- `body` uses antialiased font rendering

## CI harness (FND-004)

### Frontend testing

- **Vitest** configured with jsdom environment, @testing-library/react, path aliases
- **Test setup** mocks matchMedia and IntersectionObserver
- **Sample tests:** cn utility (3 assertions), StatusBadge (3 assertions) — 6/6 pass
- **Playwright** configured for chromium and mobile-chrome, auto-starts dev server
- **Smoke E2E:** home page loads, marketplace loads, publish loads, keyboard focusable

### CI workflow (`.github/workflows/ci.yml`)

| Job | Checks | Blocks merge |
|-----|--------|-------------|
| `frontend` | lint → unit tests → build | Yes |
| `frontend-e2e` | Playwright chromium smoke (artifact upload on failure) | Yes |
| `backend` | pytest → black --check → isort --check-only | Yes |
| `dependency-audit` | npm audit, pip-audit | Soft (returns 0) |

### Local verification

`scripts/verify.ps1` runs all checks locally: frontend install/lint/test/build, backend install/pytest/black/isort, E2E smoke.

## Story completion

| Story | Status | Evidence |
|-------|--------|----------|
| FND-001 | ✅ | `docs/ARCHITECTURE.md`, `docs/API-DOCS.md`, `docs/adr/ADR-v2-bounded-contexts.md`, `docs/adr/ADR-release-boundaries.md` |
| FND-002 | ✅ | `docs/configuration.md`, `backend/.env.example`, `frontend/.env.example`, `backend/tests/test_config.py` |
| FND-003 | ✅ | `docs/DESIGN-SYSTEM.md`, `frontend/src/app/globals.css`, 6 component files in `ui/` |
| FND-004 | ✅ | `.github/workflows/ci.yml`, `scripts/verify.ps1`, vitest/playwright configs, 2 test files |

## Integration check

On a clean merge of FND-001 through FND-004 into `main`:

- `pytest backend/tests/test_config.py -q` → **19 passed**
- `npx vitest --run` → **6 passed**
- `npm run build` → **Compiled successfully, 16/16 pages generated**
- No merge conflicts, no circular dependencies, no import errors
