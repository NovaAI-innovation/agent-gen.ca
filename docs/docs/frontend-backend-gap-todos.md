# Frontend vs Backend Functional Gap (Actionable Diff)

```yaml
snapshot:
  compared_on: 2026-04-03
  frontend_source: frontend/src
  backend_source: backend/app
  objective: "Define concrete backend work required to fully support current frontend behavior and near-term route expectations."
  implementation_progress:
    completed:
      - BE-TODO-001
      - BE-TODO-002
      - BE-TODO-003
      - BE-TODO-004
    in_progress: []
    pending:
      - BE-TODO-005
      - BE-TODO-006
```

## Coverage Matrix

```yaml
endpoint_alignment:
  - frontend_contract: "GET /auth/challenge"
    backend_status: aligned
    notes: "Implemented with wallet nonce + message."
  - frontend_contract: "POST /auth/verify"
    backend_status: aligned
    notes: "Implemented with ed25519 verification and token issuance."
  - frontend_contract: "POST /auth/refresh"
    backend_status: aligned
    notes: "Implemented; returns full Token object (frontend uses access_token)."
  - frontend_contract: "POST /auth/logout"
    backend_status: aligned
    notes: "Implemented and session-aware."
  - frontend_contract: "GET /users/me"
    backend_status: aligned
  - frontend_contract: "GET /users/{wallet}"
    backend_status: aligned
  - frontend_contract: "GET /users/{wallet}/listings"
    backend_status: aligned
    notes: "Supports owner-scoped drafts with include_drafts=true when requester is the same wallet user."
  - frontend_contract: "GET /listings"
    backend_status: aligned
  - frontend_contract: "POST /listings"
    backend_status: aligned
    notes: "Listing creation now publishes immediately for the current frontend publish wizard flow."
  - frontend_contract: "GET /listings/{slug}"
    backend_status: aligned
  - frontend_contract: "GET /listings/{slug}/versions"
    backend_status: aligned
  - frontend_contract: "GET /listings/{slug}/reviews"
    backend_status: aligned
  - frontend_contract: "POST /listings/{slug}/install"
    backend_status: aligned
    notes: "Tracks download/install and increments listing download_count."
  - frontend_contract: "POST /listings/{slug}/purchase"
    backend_status: aligned
    notes: "Slug-based purchase initiation added for listing detail CTA flows."
  - frontend_contract: "GET /marketplace/categories"
    backend_status: aligned
```

## Key Gaps (Diff Style)

### 1) Publish Flow Visibility Gap

```diff
- Frontend behavior: POST /listings then redirect to /marketplace/{slug} as a "published" creator action.
- Frontend dashboard intent: creator should see newly published asset in "My listings".
+ Backend behavior: create_listing leaves is_published=false by default.
+ Backend /users/{wallet}/listings returns only items from get_listings(), which filters is_published=true.
! Implemented in current branch: listing creation now sets is_published=true for this flow.
```

### 2) Creator Listings API Semantics Gap

```diff
- Frontend route /dashboard/listings is owner-scoped and operational ("manage listings").
+ Backend implementation of GET /users/{wallet}/listings is public-style and post-filters the generic listing query.
+ Missing explicit owner-mode include_drafts behavior and efficient DB-level owner filter.
! Implemented in current branch: include_drafts query + owner-aware auth + SQL-level owner filtering.
```

### 3) Install/Purchase Action Gap From Listing Detail

```diff
- Frontend detail page surfaces Install/Purchase CTA for each listing.
+ Backend supports POST /purchases with listing_id and confirm flow, but no slug-first purchase/init endpoint optimized for current listing detail UX.
+ No explicit free-install/download event endpoint for "Install" CTA behavior.
! Implemented in current branch: added POST /listings/{slug}/purchase and POST /listings/{slug}/install.
```

### 4) Dashboard Data Surface Gap (Next Backend Step)

```diff
- Frontend has dedicated dashboard surfaces: overview, earnings, installs, saves.
+ Backend currently has no dashboard aggregate endpoints for metrics/history used by these surfaces when they are wired.
+ Save/follow primitives exist, but retrieval endpoints for saved listings and creator dashboard analytics are absent.
! Implemented in current branch: added /dashboard/overview, /dashboard/earnings, /dashboard/installs, /dashboard/saves.
```

### 5) Query Reliability Gap (Search)

```diff
- Frontend ListingFilters always provides free-text q support.
+ Backend q search uses PostgreSQL %% operator; behavior depends on database/operator availability and is not fallback-safe.
+ Risk: search can fail or degrade depending on deployment DB setup.
```

## Backend To-Do Plan (Actionable)

```yaml
todo:
  - id: BE-TODO-001
    priority: P0
    title: "Fix publish lifecycle for frontend publish wizard"
    backend_changes:
      - "Decide and implement one contract:"
      - "A) POST /listings creates published listings by default for this UI flow, OR"
      - "B) keep drafts but add explicit publish endpoint and update frontend flow to call it."
      - "If keeping drafts, return publish_state in response to avoid ambiguity."
    acceptance_criteria:
      - "A listing created from /publish appears in creator listing management view without manual DB intervention."
      - "Marketplace visibility rules are explicit and test-covered."

  - id: BE-TODO-002
    priority: P0
    title: "Refactor GET /users/{wallet}/listings for owner/public modes"
    backend_changes:
      - "Add owner-aware logic via auth context."
      - "Support query flag include_drafts=true only for owner."
      - "Filter by owner_id at SQL layer; remove Python post-filter."
    acceptance_criteria:
      - "Owner sees own drafts and published records when requested."
      - "Public caller only receives published listings."
      - "Endpoint performance remains stable with large listing volume."

  - id: BE-TODO-003
    priority: P1
    title: "Add install and purchase UX-oriented endpoints"
    backend_changes:
      - "Add slug-friendly purchase init endpoint (or helper) for listing-detail CTA."
      - "Add free install/download tracking endpoint (e.g., POST /listings/{slug}/install) that records install event and increments counters."
      - "Return install entitlement/status data needed by detail page CTA states."
    acceptance_criteria:
      - "Listing detail can trigger backend actions for both free and paid flows using current page context."
      - "download_count/install history updates are persisted."

  - id: BE-TODO-004
    priority: P1
    title: "Create dashboard data endpoints (overview, earnings, installs, saves)"
    backend_changes:
      - "GET /dashboard/overview: listings_count, total_installs, avg_rating, reputation snapshot."
      - "GET /dashboard/earnings: payouts + purchase aggregates."
      - "GET /dashboard/installs: install/download history feed."
      - "GET /users/me/saves (or /dashboard/saves) for saved listings retrieval."
    acceptance_criteria:
      - "Each dashboard tab has a backend endpoint returning pagination-ready schema."
      - "Responses are scoped to authenticated creator."

  - id: BE-TODO-005
    priority: P2
    title: "Harden text search behavior for listing query"
    backend_changes:
      - "Replace or guard %% operator usage with ILIKE/tsvector fallback."
      - "Add query tests for q filter in local and production-like DB settings."
    acceptance_criteria:
      - "q search works consistently across environments without extension coupling."

  - id: BE-TODO-006
    priority: P2
    title: "Migration safety checks for non-ORM tables used by routers"
    backend_changes:
      - "Add startup/migration guard ensuring tables like user_saves and user_follows exist in all environments."
      - "Document migration requirement in backend README and deployment docs."
    acceptance_criteria:
      - "save/follow endpoints cannot fail due to missing table in a freshly deployed environment."
```

## Suggested Execution Order

```yaml
sequence:
  - "1. BE-TODO-001 (publish lifecycle)"
  - "2. BE-TODO-002 (owner listings semantics)"
  - "3. BE-TODO-003 (install/purchase action routes)"
  - "4. BE-TODO-004 (dashboard endpoints)"
  - "5. BE-TODO-005 and BE-TODO-006 (hardening)"
```
