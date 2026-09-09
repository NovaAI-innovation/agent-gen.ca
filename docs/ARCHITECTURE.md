# Architecture

## System overview

agent-gen.ca is a curated marketplace for installable AI-agent components. Buyers discover, evaluate, acquire, and install MCP servers, skills, agents, and packs. Creators publish versioned artifacts through a moderated workflow. The platform establishes trust through moderation, signed release manifests, artifact scanning, transparent publisher history, and verified transaction records.

## Bounded contexts

The system is organized into nine bounded contexts. Each owns its data, state machines, and public interface. Cross-context communication uses explicit service calls and domain events — never shared mutable state.

| Context | Owns | Key states |
|---------|------|------------|
| **Identity** | Wallet sign-in, nonces, sessions, creator profiles, rate limits | anonymous → connected → signed-in → creator-approved |
| **Catalog** | Listing metadata, categories, search indexes, compatibility, discovery | draft → in-review → published → suspended → archived |
| **Publishing** | Draft editor, validation, review submission, autosave, preview | draft → valid → submitted → approved → published |
| **Artifacts** | Releases, manifests, object storage, scanning, delivery, install events | uploading → quarantined → scanned → approved → delivered |
| **Moderation** | Review queues, approve/reject decisions, suspension, restoration, audit | pending → approved / rejected / suspended |
| **Reports** | User-submitted abuse reports against listings, releases, creators, reviews | submitted → triaged → resolved → dismissed |
| **Payments** | Payment intents, USDC checkout, chain verification, reconciliation, refunds (Release B) | intent → submitted → verifying → finalized / failed / expired |
| **Entitlements** | Acquisition grants, buyer library, download access, install records | free-acquired → paid-acquired → active → revoked |
| **Operations** | Deployment, health checks, observability, backups, CI/CD, alerts | live → degraded → recovering |

### Identity

Identity owns wallet-based authentication using Wallet Standard Sign In With Solana (SIWS), with a legacy message-signing fallback. Sign-in inputs are generated server-side and verify exact domain, URI, address, chain, nonce, issued-at, and expiry. Refresh credentials live in HttpOnly cookies; access tokens live in memory. Sessions rotate atomically and can be revoked by the user or an operator.

Creator profiles extend the identity context. An approved creator is a prerequisite for publishing. Profile fields include unique handle, display name, bio, support link, terms acceptance, and payout address.

Shared Redis-backed rate limits protect authentication endpoints at both edge and application layers. Forwarded client IPs are trusted only from the edge proxy.

### Catalog

Catalog owns listing metadata, validation rules, search, and discovery. Listings have a type (MCP server, agent skill, custom agent, pack), structured metadata, and a lifecycle state machine. Drafts are invisible to public queries. Only published listings with passing releases appear in search results.

Validation constrains content lengths, URLs, prices (NUMERIC 18,9 SOL-denominated for Release A; USDC-denominated for Release B), categories, licenses, and listing-type-specific fields. Duplicate submissions return stable error codes.

### Publishing

Publishing owns the creator-facing draft editor, autosave, validation, preview, and review-submission workflow. A draft is saved privately by default and never publishes directly. The editor surfaces validation errors inline. Submission triggers a moderation review.

### Artifacts

Artifacts own release manifests, versioned artifacts, object storage, scanning, delivery, and install analytics.

Every release records: semantic version, artifact URI, SHA-256 digest, size, media type, license, compatibility data, permission declarations, install instructions, and support information. Published release records are immutable — corrections create a new release.

Uploads use short-lived signed URLs and private object storage. A scanner quarantines artifacts until policy checks pass. Downloads use short-lived entitlement-bound URLs and append-only audit records. Install counters derive from deduplicated install events.

### Moderation

Moderation owns review queues and decisions for creators, listings, and releases. Moderators approve, reject, suspend, and restore with reasons. Every decision produces an immutable audit event. Moderators can suspend access immediately without destroying evidence.

### Reports

Reports own user-submitted abuse reports against public entities. Users can report listings, releases, creators, and reviews. Reports track receipt and resolution status.

### Payments (Release B)

Payments own the USDC payment state machine. The server creates a payment intent that freezes buyer, seller, listing, release, mint, amount, fee, recipient accounts, memo/reference, cluster, and expiry. Submission accepts one transaction signature per intent and enqueues verification.

The verifier parses exact token instructions, account ownership, mint, amount, recipients, fee split, memo/reference, signer, cluster, error state, and finality. Only the verifier grants a paid entitlement. SOL pays network fees and may become an optional payment asset later.

### Entitlements

Entitlements own acquisition grants that bind a user to a specific release. Free listings grant an entitlement on acquisition. Paid listings grant an entitlement after payment verification succeeds. The buyer library surfaces all active entitlements with download access and install instructions.

### Operations

Operations owns deployment topology, health endpoints, observability, backups, CI/CD, and incident response. Health endpoints distinguish liveness, readiness, and dependency health. Logs use correlation IDs without storing secrets.

## Target architecture

```text
Internet
  → single TLS edge proxy (ports 80/443 only)
     → Next.js web (frontend/)
     → FastAPI API (backend/)
        → PostgreSQL 16 (async via asyncpg)
        → Redis (queue + rate-limit store)
        → private object storage
     → chain verification worker (Release B)
     → artifact scanning worker
     → metrics, logs, and alerts
```

PostgreSQL, Redis, workers, and administrative tools remain on private container networks. Staging uses a separate database, object prefix, Redis namespace, Solana devnet configuration, and hostname.

## Frontend stack

- **Framework:** Next.js 15 App Router, React 19, TypeScript
- **Styling:** Tailwind v4 with custom neon CSS variables (cyan/amber/lime/purple palette)
- **State:** Zustand (`authStore` with persistence) for auth; TanStack React Query for server data (30s stale time)
- **HTTP:** Axios configured with `NEXT_PUBLIC_API_URL`, token injected via interceptor
- **Wallet:** Solana wallet adapter (Wallet Standard preferred, legacy fallback)
- **Polyfills:** Webpack Buffer and process polyfills for Solana Web3.js in browser

## Backend stack

- **Framework:** FastAPI with async SQLAlchemy 2.0 (asyncpg driver)
- **Auth:** JWT (HS256, 24h access), HttpOnly refresh cookies, ed25519 signature verification
- **Database:** PostgreSQL 16, Alembic migrations as source of truth
- **Cache/queue:** Redis for rate limiting, session management, and job queues

## Security controls

1. Rate limiting on challenge/verify/refresh auth endpoints (Redis-backed, shared across workers)
2. JWT issuer and audience validation
3. Session-backed refresh token rotation
4. Request metadata hashing in auth audit logs
5. Short-lived signed URLs for artifact upload and download
6. Artifact quarantine and scanning before publication
7. Entitlement-bound download URLs

## Configuration contract

Reference: [ADR-0001-solana-foundation.md](/docs/ADR-0001-solana-foundation.md)

## Architecture decision records

- [ADR-v2-bounded-contexts.md](/docs/adr/ADR-v2-bounded-contexts.md) — bounded context definitions and ownership
- [ADR-release-boundaries.md](/docs/adr/ADR-release-boundaries.md) — Release A and Release B scope boundaries
