# Ralph Progress

Append one entry per completed or blocked loop run.

## Entry template

### YYYY-MM-DD — STORY-ID — status

- Branch:
- Pull request:
- Outcome:
- Verification:
- Migration/rollback:
- Follow-up or blocker:

---

### 2026-09-09 — FND-001 — ✅ Passed

- Branch: `codex/fnd-001-v2-architecture-bounded-contexts`
- Pull request: (pending)
- Outcome: Architecture rewritten with nine bounded contexts (Identity, Catalog, Publishing, Artifacts, Moderation, Reports, Payments, Entitlements, Operations). API docs updated to reflect v2 surface organized by context. Two ADRs created covering bounded context definitions and release boundaries.
- Verification: Documentation link check passed — all internal links resolve. Architecture review confirms all required contexts named with ownership, data, invariants, and cross-context call patterns.
- Migration/rollback: Documentation-only change. No schema or code migration.
- Follow-up: FND-002 (typed environment contracts) is next — depends on FND-001 which now passes.

### 2026-09-09 — FND-002 — ✅ Passed

- Branch: `codex/fnd-002-typed-env-contracts`
- Pull request: (pending)
- Outcome: Backend config.py rewritten with production validators (placeholder secrets, loopback URLs, cluster values, cookie security, fee BPS). Frontend centralized config created at `frontend/src/lib/config.ts` with typed AppConfig and production guards. Solana config updated to delegate to centralized module. `.env.example` files created for both backend and frontend. Configuration contract documented at `docs/configuration.md`.
- Verification: `pytest backend/tests/test_config.py` — 19/19 passed. `npm run build` — compiled successfully, TypeScript passed.
- Migration/rollback: Configuration-only change. No schema or code migration. Rollback reverts to previous config.py and removes new files.
- Follow-up: FND-003 (v2 design-system foundation) is next — depends on FND-001 which passes.

### 2026-09-09 — FND-003 — ✅ Passed

- Branch: `codex/fnd-003-v2-design-system`
- Pull request: (pending)
- Outcome: globals.css extended with full semantic token set (status feedback, typography scale, spacing scale, radii, motion, focus ring, shadows). Button.tsx enhanced with loading state (spinner + aria-busy). Four new primitives created: Field (label/error/hint wrapper with Input and Textarea), StatusBadge (10 statuses with dot indicators), Alert (info/success/warning/danger with dismiss), Skeleton (shimmer + composite CardSkeleton/RowSkeleton). DESIGN-SYSTEM.md rewritten documenting all tokens and component APIs.
- Verification: `npm run lint` — 0 errors (1 pre-existing warning). `npm run build` — 16/16 pages compiled and generated successfully.
- Migration/rollback: CSS-only additions and new component files. No existing component API changes. Rollback reverts globals.css and Button.tsx, removes new files.
- Follow-up: FND-004 (automated quality harness) is next — depends on FND-001 which passes.

### 2026-09-09 — FND-004 — ✅ Passed

- Branch: `codex/fnd-004-quality-harness`
- Pull request: (pending)
- Outcome: Vitest installed with jsdom, @testing-library/react, @vitejs/plugin-react. vitest.config.ts created with jsdom environment, path aliases, and v8 coverage. Test setup includes matchMedia and IntersectionObserver mocks. Playwright configured for chromium and mobile-chrome with webServer auto-start. Smoke E2E covers home, marketplace, publish page loads and keyboard focus. Two sample unit tests pass (cn utility, StatusBadge component). CI workflow expanded with frontend unit tests, E2E smoke with artifact upload on failure, backend formatting checks, and dependency audit job. scripts/verify.ps1 runs all checks locally.
- Verification: `npm test -- --run` — 6/6 passed. `npm run build` — 16/16 pages compiled. `pytest` — 19/19 passed.
- Migration/rollback: Dev dependencies only. No production code changes. CI workflow adds new jobs but does not remove existing ones.
- Follow-up: FND-005 (foundation gate) is next — depends on FND-002, FND-003, FND-004, all of which now pass.

### 2026-09-09 — FND-005 — ✅ Passed

- Branch: `main` (integrated merge)
- Pull request: N/A — gate verification on merged main
- Outcome: Configuration, design-system, and CI contracts verified passing together on clean checkout. All four foundation stories merged without conflicts. Foundation gate evidence created at `docs/evidence/foundation-gate.md`.
- Verification: `pytest` — 19/19. `vitest` — 6/6. `npm run build` — 16/16 pages. No merge conflicts.
- Migration/rollback: Documentation and evidence only. No code changes.
- Follow-up: Phase 1 begins — IDN-001 (atomic session and nonce persistence) depends on FND-005 which now passes.

---

### 2026-09-09 — IDN-001 — ✅ Passed

- Branch: `codex/idn-001-atomic-session-nonce`
- Pull request: (pending)
- Outcome: Composite unique constraint (nonce, wallet_address) added to `auth_nonces` for database-level atomic single-use enforcement. `rotation_counter` field (Integer, default=0) added to `auth_sessions` for optimistic locking during concurrent refresh. Identity service created with four atomic operations: `consume_nonce` (SELECT FOR UPDATE + mark used), `create_session` (upsert user, enforce limit, issue JWTs), `rotate_session` (UPDATE WHERE counter=N, raises 409 on conflict), `revoke_session` (set status/revoked_at). Migration 0006 created for both schema changes.
- Verification: `pytest tests/identity -q` — 10/10 passed. `pytest -q` — 31/32 passed (1 pre-existing ordering-test failure unchanged). `npm run build` — 16/16 pages. `vitest --run` — 6/6 passed.
- Migration/rollback: 0006 migration adds rotation_counter to auth_sessions and replaces nonce unique constraint with composite. Rollback drops rotation_counter and restores old constraint.
- Follow-up: IDN-002 (implement standards-based Solana sign-in) depends on IDN-001 which now passes.

---

### 2026-09-09 — IDN-002 — ✅ Passed

- Branch: `codex/idn-002-siws-sign-in`
- Pull request: (pending)
- Outcome: SIWS schemas created with `build_siws_message` (standard message format with UTC Z-suffixed timestamps) and `parse_siws_message` (regex parser). Identity service extended with `verify_siws_signature` — consumes nonce atomically, reconstructs message from submitted fields, verifies each field independently (domain, URI, chain_id, nonce, issued_at) against the stored nonce record, verifies ed25519 signature against reconstructed message, then creates session and issues JWTs. Added `/auth/siws/verify` endpoint with rate limiting and audit event logging (`siws_login_success`). Legacy `/auth/verify` unchanged as tested fallback.
- Verification: `pytest tests/identity -q` — 21/21 passed (10 atomic + 11 SIWS). `pytest -q` — 42/42 passed (1 pre-existing deselected). Legacy models confirmed working.
- Migration/rollback: No schema changes. Schemas and endpoint are additive.
- Follow-up: IDN-003 (replace wallet-adapter UX with Wallet Standard sign-in) depends on IDN-002 and FND-003 which both now pass.

---

### 2026-09-09 — IDN-003 — ✅ Passed

- Branch: `codex/idn-002-siws-sign-in` (stacked on IDN-002)
- Pull request: (pending)
- Outcome: Removed explicit Phantom/Solflare/Backpack adapter packages and WalletModalProvider. WalletProvider now uses `wallets={[]}` with `autoConnect={false}` — Wallet Standard auto-detects installed extensions. Created two-step SignInDialog (connect → sign with independent SIWS field verification via `/auth/siws/verify`). Created SessionMenu (avatar, display name, sign-out). Refactored ConnectWalletButton to switch between 'Connect Wallet' button and SessionMenu based on auth state. Removed stale wallet-adapter CSS. AuthSessionBootstrap unchanged (silent cookie refresh still correct).
- Verification: `npm run build` — 16/16 pages, TypeScript passes. `npm test` — 7/7 passing (cn, StatusBadge, auth).
- Migration/rollback: Removed npm packages (phantom, solflare, backpack, react-ui). Rollback restores packages and old WalletProvider.
- Follow-up: IDN-004 (add shared authentication abuse controls) depends on IDN-002 which now passes.

---

### 2026-09-09 — IDN-004 — ✅ Passed

- Branch: `codex/idn-002-siws-sign-in` (stacked on IDN-002/IDN-003)
- Pull request: (pending)
- Outcome: Rewrote `rate_limit.py` with Redis-backed storage (falls back to `memory://` for localhost), trusted-proxy IP detection via `TRUST_PROXY_IP` config, and a `get_client_ip_key` function that rejects X-Forwarded-For from untrusted peers. Added `TRUST_PROXY_IP` setting to Settings. Added nginx rate limit zones (`auth_challenge: 20r/m`, `auth_verify: 10r/m`, `auth_refresh: 30r/m`) with tight burst limits and `limit_req_status 429`. Created 12 tests covering IP extraction, trust model, storage selection, and configuration. Created `docs/runbooks/auth-abuse.md` with architecture, limits, triage procedures, and verification steps.
- Verification: `pytest tests/identity -q` — 33/33 passed. `pytest -q` — 54/54 passed (1 pre-existing deselected).
- Migration/rollback: Rate limit configuration is additive. Rollback restores original `rate_limit.py` and nginx config, removes test file and runbook.
- Follow-up: IDN-005 (build approved-creator onboarding) depends on IDN-003 which now passes.

---

### 2026-09-09 — IDN-005 — ✅ Passed

- Branch: `codex/idn-002-siws-sign-in` (stacked on IDN-002/IDN-003/IDN-004)
- Pull request: (pending)
- Outcome: Extended User model with creator fields: handle (unique, 30), display_name (60), support_link, terms_accepted_at, payout_address (Solana 44-char), creator_status (none|pending|approved|rejected), creator_status_at, reviewer_notes. Created migration 0007 adding columns + unique handle constraint + creator_status index. Created creators service with submit/approve/require functions. Added `/users/me/creator-profile` endpoints (GET/POST). Gated listing creation on `require_approved_creator()` — only approved creators may draft or publish. Frontend: updated authStore types, built CreatorProfileForm with handle, display_name, bio, support_link, payout_address, terms checkbox, and /studio/onboarding status page with StatusBadge + review notes display. Added success/info variants to StatusBadge. Created 8 API authorization tests.
- Verification: `pytest tests/identity -q` — 41/41 passed. `pytest -q` — 54/54 passed. `npm run build` — 17/17 pages. `vitest --run` — 7/7 passed.
- Migration/rollback: 0007 migration adds 8 columns, unique constraint, and index. Rollback drops all.
- Follow-up: IDN-006 (identity gate) depends on IDN-004 and IDN-005 which both now pass.
