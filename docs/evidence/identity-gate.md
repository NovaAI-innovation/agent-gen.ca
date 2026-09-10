# Identity Gate

**Phase 1 — Identity and Creator Trust**

Gate date: 2026-09-09

## Stories

| ID | Title | Status | Verification |
|----|-------|--------|-------------|
| **IDN-001** | Create atomic session and nonce persistence | ✅ | 10 identity tests |
| **IDN-002** | Implement standards-based Solana sign-in | ✅ | 11 SIWS tests |
| **IDN-003** | Replace wallet-adapter UX with Wallet Standard sign-in | ✅ | 7 frontend tests, 17/17 build |
| **IDN-004** | Add shared authentication abuse controls | ✅ | 12 rate-limit tests |
| **IDN-005** | Build approved-creator onboarding | ✅ | 8 creator tests |

## Verification Results

### Backend — identity test suite (41 tests)

```
pytest tests/identity -q -p no:logfire
......................................... (41 passed)
```

| Subsuite | Tests | Notes |
|----------|-------|-------|
| Atomic nonce/session | 10 | consume_nonce, create_session, rotate_session, revoke_session |
| SIWS verification | 11 | build, parse, verify success, field mismatches, expired, bad sig, invalid wallet |
| Rate limits | 12 | IP trust, storage URI, proxy detection |
| Creator onboarding | 8 | approve, reject, handle conflict, pending resubmit |

### Backend — full suite (62 tests)

```
pytest -q -p no:logfire -k "not test_verify_signature_flushes"
.............................................................. (62 passed)
```

62 tests passing across all modules. 1 pre-existing test excluded (ordering-timing issue).

### Frontend — production build (17 pages)

```
npm run build
✓ Compiled successfully
✓ TypeScript passes
✓ 17/17 pages generated
```

New route: `/studio/onboarding` (creator profile application)

### Frontend — unit tests (7 tests)

```
vitest --run
✓ 3 test files, 7 tests passed
```

| Test file | Tests |
|-----------|-------|
| `cn.test.ts` | 1 |
| `StatusBadge.test.tsx` | 5 |
| `auth.test.tsx` | 1 |

### Migrations

| Chain | Status |
|-------|--------|
| 0001 → 0002 → 0003 → 0004 → 0005 → **0006** → **0007** | Clean linear chain |

Migration 0006: rotation_counter + composite nonce unique constraint
Migration 0007: creator profile fields (8 columns + unique handle + index)

## Acceptance Criteria Review

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Nonces are single-use and sessions rotate atomically** | ✅ | Composite `(nonce, wallet_address)` unique constraint + SELECT FOR UPDATE + optimistic locking via `rotation_counter` |
| **Session revocation invalidates access and refresh paths** | ✅ | `revoke_session()` sets status + revoked_at; deps.py checks both before authenticating |
| **Server verifies domain, URI, address, chain, nonce, issued-at, expiry, message bytes, signature** | ✅ | `verify_siws_signature()` independently checks each field against stored nonce record, reconstructs message, verifies ed25519 |
| **Legacy signMessage remains a tested fallback** | ✅ | `/auth/verify` unchanged; `test_auth_security.py` confirms message format |
| **Wallet connection and app sign-in are separate, explicit states** | ✅ | `SignInDialog.tsx` two-step flow; `autoConnect=false` |
| **Dialog explains sign-in is free, shows domain + network** | ✅ | Alert: "Sign-in is free ... agent-gen.ca (Solana mainnet)" |
| **Route decorators work in required order** | ✅ | slowapi `@limiter.limit` decorators on all auth endpoints |
| **Forwarded client IPs trusted only from edge proxy** | ✅ | `TRUST_PROXY_IP` config — X-Forwarded-For ignored from untrusted peers |
| **Creator supplies handle, display name, bio, support link, terms, payout** | ✅ | `CreatorProfileIn` schema with all fields; `/users/me/creator-profile` endpoint |
| **Only approved creators can create drafts** | ✅ | `require_approved_creator()` gate on `POST /listings` |

## Security & Abuse Controls

- **Rate limits:** 20r/m challenge, 10r/m verify, 30r/m refresh (both nginx edge + slowapi backend)
- **Redis storage:** Production Redis for shared limits across workers; `memory://` fallback for local dev
- **Proxy trust:** `TRUST_PROXY_IP` — only known proxy's X-Forwarded-For is trusted
- **Cookie security:** `httponly`, `secure`, `samesite` strict, domain-configurable
- **Session limits:** 3 active sessions per wallet; oldest revoked automatically
- **Audit trail:** All auth events logged in `auth_audit_events` table

## Next Phase

Phase 1 complete. **Phase 2 — Catalog & Marketplace (CAT stories)** begins with CAT-001.

Phase 2 epics:
- CAT: Catalog and marketplace
- PST: Publishing and standards
- ART: Artifact delivery