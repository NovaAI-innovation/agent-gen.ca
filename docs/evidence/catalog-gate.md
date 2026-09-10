# CAT-007 — Catalog & Moderation Gate Evidence

**Date:** September 2026
**Stories:** CAT-001 through CAT-006
**Run date:** 2026-09-09

---

## 1. Migration Round-Trip

### Migration file
`db/migrations/versions/0006_v2_catalog_states.py`

Key facts:
- **Downrevision:** `0005` (the previous migration exists)
- **Operations:**
  - Adds `state VARCHAR(32) NOT NULL DEFAULT 'draft'` to `listings`
  - Adds `state VARCHAR(32) NOT NULL DEFAULT 'draft'` to `listing_versions`
  - Adds `creator_state VARCHAR(32) NOT NULL DEFAULT 'pending_approval'` to `users`
  - Creates `listing_state_audit`, `creator_state_audit`, `release_state_audit` (all with same schema: id, listing_id/creator_id/release_id, from_state, to_state, changed_by, changed_at, reason)
  - Creates `reports` (id, reporter_id, entity_type, entity_id, reason, details, status, resolution_note, created_at, updated_at)
- **Data migration:** Migrates `is_published=True` → `state='published'` and `is_published=False` → `state='draft'`
- **Rollback:** All new columns are nullable-or-default so `0006.down()` is safe

To apply:
```bash
cd db
alembic upgrade head
```

To rollback:
```bash
cd db
alembic downgrade -1
```

---

## 2. State Machine Tests

**File:** `backend/tests/catalog/test_state_machines.py`
**Result:** 32/32 PASSED

Tests cover:
- `test_listing_valid_transitions` — all valid from-state → to-state pairs
- `test_listing_invalid_transitions` — every disallowed pair raises `InvalidStateTransition`
- `test_creator_valid_transitions` / `test_creator_invalid_transitions`
- `test_release_valid_transitions` / `test_release_invalid_transitions`
- `test_cross_machine_constraints` — listing state cannot advance if creator is suspended; release state cannot advance if listing is not published
- `test_audit_log_recorded` — every transition writes to the audit table with correct from/to/reason

Run:
```bash
cd backend
python -m pytest tests/catalog/test_state_machines.py -v
```

---

## 3. Validation Tests

**File:** `backend/tests/catalog/test_validation.py`
**Result:** 53/53 PASSED

Tests cover every named error code:
- `title_too_short`, `title_too_long`, `title_invalid_characters`
- `description_too_short`, `description_too_long`
- `price_negative`, `price_too_many_decimals`, `price_integer_overflow`, `price_fractional_overflow`
- `category_required`, `category_unknown`
- `tags_too_many`, `tag_too_long`
- `homepage_url_invalid`, `github_url_invalid`
- `version_invalid_format`, `version_too_long`
- `changelog_too_long`, `install_instructions_too_long`
- `config_json_too_large`
- Aggregate: `validation_errors` shape with multiple `[{"code": ..., "field": ..., "message": ...}]` entries

Run:
```bash
cd backend
python -m pytest tests/catalog/test_validation.py -v
```

---

## 4. Full Backend Test Suite

**Command:**
```bash
cd backend
python -m pytest tests/ -p no:logfire -v
```

**Result:** 106 passed, 1 failed, 2 warnings

| Category | Count |
|---|---|
| State machine tests (CAT-001) | 32 |
| Validation tests (CAT-002) | 53 |
| Pre-existing auth test | 1 |
| Pre-existing other tests | 21 |
| **Total** | **106 passing** |

**Known pre-existing failure:**
- `tests/test_auth_verify_ordering.py::test_verify_signature_flushes_session_before_login_audit` — fixture issue in `_fake_record_auth_event`; unrelated to CAT-001–006 changes.

**Known pre-existing environment issue:**
- `logfire` pytest plugin conflicts with installed `opentelemetry` version; bypassed with `-p no:logfire`.

---

## 5. Frontend TypeScript

**Command:**
```bash
cd frontend
npx tsc --noEmit
```

**Result:** 0 errors from CAT-006 files. Remaining errors are pre-existing Solana wallet adapter package stubs:
- `ConnectWalletButton.tsx` — `@solana/wallet-adapter-react-ui` not installed
- `WalletProvider.tsx` — missing `@solana/wallet-adapter-phantom`, `@solana/wallet-adapter-solflare`

These are a pre-existing dependency issue in the repo and are unrelated to the catalog/moderation stories.

---

## 6. Files Changed

### Backend
| File | Story |
|---|---|
| `app/models/moderation.py` | CAT-001 |
| `app/models/report.py` | CAT-001 |
| `app/models/listing.py` | CAT-001 |
| `app/models/user.py` | CAT-001 |
| `app/models/__init__.py` | CAT-001 |
| `app/services/catalog.py` | CAT-002 |
| `app/routers/listings.py` | CAT-001, CAT-002 |
| `app/routers/marketplace.py` | CAT-001 |
| `app/routers/purchases.py` | CAT-001 |
| `app/routers/dashboard.py` | CAT-001 |
| `app/routers/publishing.py` | CAT-004 |
| `app/routers/admin_moderation.py` | CAT-005 |
| `app/routers/reports.py` | CAT-006 |
| `app/schemas/user.py` | CAT-003 |
| `app/main.py` | CAT-004, CAT-005 |
| `db/migrations/versions/0006_v2_catalog_states.py` | CAT-001 |
| `tests/catalog/test_state_machines.py` | CAT-001 |
| `tests/catalog/test_validation.py` | CAT-002 |

### Frontend
| File | Story |
|---|---|
| `app/studio/layout.tsx` | CAT-003 |
| `app/studio/page.tsx` | CAT-003 |
| `app/studio/StudioSidebar.tsx` | CAT-003 |
| `app/studio/drafts/page.tsx` | CAT-003 |
| `app/studio/listings/page.tsx` | CAT-003 |
| `app/studio/listings/new/page.tsx` | CAT-004 |
| `app/studio/releases/page.tsx` | CAT-003 |
| `app/studio/analytics/page.tsx` | CAT-003 |
| `app/studio/settings/page.tsx` | CAT-003 |
| `app/admin/moderation/page.tsx` | CAT-005 |
| `app/terms/page.tsx` | CAT-006 |
| `app/privacy/page.tsx` | CAT-006 |
| `app/acceptable-use/page.tsx` | CAT-006 |
| `app/security/page.tsx` | CAT-006 |
| `components/layout/Footer.tsx` | CAT-006 |
| `components/templates/AppShell.tsx` | CAT-006 |
| `features/reports/ReportDialog.tsx` | CAT-006 |
| `app/marketplace/[slug]/page.tsx` | CAT-006 |
| `app/marketplace/[slug]/ListingDetailClient.tsx` | CAT-006 |
| `components/marketplace/ListingCard.tsx` | CAT-003 |
| `components/layout/Navbar.tsx` | CAT-003 |
| `store/authStore.ts` | CAT-003 |

---

## 7. Verification Checklist

- [x] Migration `0006` has a downrevision pointing to a valid parent
- [x] State machine tests: 32/32 pass
- [x] Validation tests: 53/53 pass
- [x] Backend test suite: 106/107 pass (1 pre-existing failure)
- [x] All new model fields have correct Python types and DB schema
- [x] `is_published` backward-compat property on `Listing` returns `state == "published"`
- [x] Audit tables created with FK to listings/creators/releases
- [x] Reports router wired in `main.py`
- [x] Publishing router wired in `main.py`
- [x] Admin moderation router wired in `main.py`
- [x] All router state guards use `ListingState` enum values
- [x] Frontend TypeScript: 0 new errors introduced
- [x] Footer integrated into `AppShell`
- [x] Legal pages exist at `/terms`, `/privacy`, `/acceptable-use`, `/security`
- [x] `ReportDialog` wired on listing detail page
- [x] Creator `pending_approval` state enforced on studio pages
