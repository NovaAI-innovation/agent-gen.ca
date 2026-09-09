# ADR: v2 Bounded Contexts

- Status: Accepted
- Date: 2026-09-09
- Deciders: Product and engineering

## Context

agent-gen.ca v1 mixed identity, listing, purchase, and marketplace concerns into loosely separated routers with shared models. As the product expands to moderated publishing, artifact scanning, verified payments, and entitlement-bound delivery, the v1 structure cannot enforce ownership, state isolation, or safe evolution.

v2 needs explicit bounded contexts so that each module owns its data, state machines, validation rules, and public interface.

## Decision

Define nine bounded contexts:

### 1. Identity

**Owns:** Wallet sign-in, nonces, sessions, creator profiles, rate limits.

**Data:** `users`, `auth_nonces`, `sessions`, `creator_profiles`

**Key invariant:** A session is valid only if its nonce was consumed exactly once, its refresh credential has not rotated to a newer token, and its wallet signature remains valid.

**Cross-context calls:** Catalog, Publishing, Moderation, and Entitlements depend on Identity to resolve the current user and creator status.

### 2. Catalog

**Owns:** Listing metadata, categories, search indexes, compatibility information, and public discovery surfaces.

**Data:** `listings`, `listing_categories`, `listing_compatibilities`, search indexes

**Key invariant:** A listing appears in public queries only when its state is `published`, its creator is approved, and at least one release is approved and not suspended.

**Cross-context calls:** Reads creator status from Identity, release status from Artifacts, and moderation status from Moderation.

### 3. Publishing

**Owns:** Draft lifecycle, editor state, validation, autosave, preview, and review submission.

**Data:** `drafts`, `draft_revisions`

**Key invariant:** A draft transitions to `submitted` only when all required fields pass validation and the creator has not exceeded submission rate limits.

**Cross-context calls:** Reads creator approval from Identity. Submission creates a moderation queue entry in Moderation.

### 4. Artifacts

**Owns:** Release manifests, versioned artifacts, object storage, scanning, delivery URLs, and install analytics.

**Data:** `releases`, `artifacts`, `artifact_scans`, `install_events`

**Key invariant:** A release is installable only when its artifact passes scanning, its release is approved, and the requesting user holds a valid entitlement.

**Cross-context calls:** Reads entitlement grants from Entitlements. Scan results feed moderation decisions.

### 5. Moderation

**Owns:** Review queues, approve/reject/suspend/restore decisions, and audit events for creators, listings, and releases.

**Data:** `moderation_actions`, `moderation_audit`

**Key invariant:** Every state transition produces an immutable audit event with actor, reason, timestamp, and affected entity.

**Cross-context calls:** Publishes decisions that Catalog, Publishing, and Artifacts consume to update entity states.

### 6. Reports

**Owns:** User-submitted abuse reports against listings, releases, creators, and reviews.

**Data:** `reports`

**Key invariant:** A report links to exactly one entity and tracks submitted → triaged → resolved/dismissed lifecycle.

**Cross-context calls:** Reports may trigger moderation actions.

### 7. Payments (Release B)

**Owns:** Payment-intent lifecycle, USDC checkout transaction construction, chain verification, reconciliation, and refunds.

**Data:** `payment_intents`, `onchain_transactions`, `payment_receipts`

**Key invariant:** A paid entitlement is granted only after the verifier confirms exact signer, cluster, finality, mint, base-unit amounts, recipients, fee split, memo/reference, and transaction success.

**Cross-context calls:** Verification result triggers entitlement creation in Entitlements.

### 8. Entitlements

**Owns:** Acquisition grants binding a user to a specific release, buyer library, download access, and install records.

**Data:** `entitlements`, `download_audit`

**Key invariant:** A download URL is valid only when the entitlement is active, the release is not suspended, and the URL has not expired.

**Cross-context calls:** Free acquisitions are created by Catalog. Paid acquisitions are created by Payments. Download access reads release status from Artifacts.

### 9. Operations

**Owns:** Deployment topology, health endpoints, observability, backups, CI/CD, and incident response.

**Data:** Logs, metrics, alerts, backup records

**Key invariant:** Health endpoints distinguish liveness (process is up), readiness (dependencies available), and detailed dependency status.

**Cross-context calls:** Reads health signals from all other contexts.

## Consequences

**Positive:**
- Each context can evolve its schema and logic independently.
- State machines are explicit and auditable.
- Rate limits, validation, and authorization rules are co-located with their owning context.
- Testing boundaries are clear — each context can be tested with controlled mocks of its dependencies.

**Negative:**
- Cross-context queries (e.g., listing search that filters by scan status and moderation state) require careful join design or materialized views.
- The moderation decision broadcast pattern needs a reliable in-process or queue-based mechanism.

**Neutral:**
- Some v1 tables (e.g., `listings`, `purchases`) will need migration to align with their owning context's state machine.
