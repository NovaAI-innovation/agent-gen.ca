# ADR: Release Boundaries

- Status: Accepted
- Date: 2026-09-09
- Deciders: Product and engineering

## Context

agent-gen.ca v2 has two releases with fundamentally different risk profiles. Release A is a curated free beta that validates the marketplace without financial risk. Release B adds paid USDC purchases with on-chain verification, which introduces financial, security, and operational requirements that cannot be shortcut.

Without explicit boundaries, implementation tends to leak paid features into the free release, expose incomplete payment surfaces to users, or defer trust and safety work that should block launch.

## Decision

### Release A: Curated free beta

Release A validates discovery, publishing, moderation, artifact delivery, and buyer experience using free listings only.

#### Included

1. **Wallet sign-in** — Wallet Standard SIWS with legacy fallback, session rotation, session revocation
2. **Creator onboarding** — Profile submission, approval workflow, approved-creator gating for publishing
3. **Draft and review workflows** — Private drafts, autosave, validation, preview, explicit review submission
4. **Moderated listings** — Moderator approve/reject/suspend/restore with audit events
5. **Versioned artifacts** — Release manifests, signed uploads, quarantine, scanning, immutable release records
6. **Protected downloads** — Entitlement-bound short-lived download URLs, install event tracking
7. **Buyer library** — Acquired listings with version history and install instructions
8. **Real analytics** — Measured install counts, time-bounded public metrics, creator dashboard
9. **Legal and reporting** — Terms, Privacy, Acceptable Use, Security pages; abuse report workflow
10. **Production VPS operations** — Health checks, backups, CI/CD, deploy/rollback procedures

#### Explicitly excluded from Release A

- Paid listings, tips, or any financial transaction
- Platform fees or fee splits
- Public self-service publishing (publishing is gated by creator approval)
- Escrow, disputes, refunds, or chargeback handling
- On-chain transaction verification
- Payment intents or receipt generation
- Entitlements derived from payment verification
- Any public claim not backed by measured production data

### Release B: Paid USDC mainnet

Release B adds the payment stack to Release A's validated marketplace.

#### Added on top of Release A

1. **USDC-denominated pricing** — Listings priced in USDC with integer base-unit storage
2. **Payment intents** — Server-created intent freezing buyer, seller, listing, release, mint, amount, fee, recipient, memo/reference, cluster, and expiry
3. **Checkout transaction** — Client-side transaction construction matching server intent
4. **Chain verification** — Async worker verifying signer, cluster, finality, token program, mint, source owner, exact amounts, recipients, fee split, memo/reference, and transaction success
5. **Paid entitlements** — Entitlements granted only after verifier confirmation
6. **Receipts** — Stable receipt with transaction, release, amount, fee, and entitlement status
7. **Reconciliation** — Operator tools to inspect, replay, expire, and reconcile intents
8. **Refund and dispute operations** — Documented runbooks and operator workflows
9. **Finance-grade observability** — Intent expiry rate, verification failure rate, entitlement drift, reconciliation age, RPC latency/failover metrics

#### Excluded from both releases

1. Escrow or an on-chain marketplace program
2. Anonymous public publishing
3. Custody of user wallets or private keys
4. Automated endorsement of arbitrary agent code
5. Multi-chain support
6. Social feeds, follower counts, or reputation graphs before marketplace trust is proven
7. A broad affiliate-resource directory inside the primary marketplace navigation

### Gate requirements

#### Release A gate

- At least ten legitimate, reviewed listings from at least three approved creators
- All public listings have installable releases and passing scans
- Terms, Privacy, Acceptable Use, Security, and reporting flows are live
- Production dependency and container scans have no unresolved critical or high findings
- Backup restore and deploy rollback succeed on staging
- Desktop, mobile, keyboard, and accessibility test suites pass

#### Release B gate

- Payment state-machine, semantic verifier, replay, and chaos tests pass
- Staging completes at least 100 successful devnet purchase simulations
- A 24-hour production-like soak has no unresolved P0 or P1 incident
- An independent reviewer signs off on payment, entitlement, auth, and operational threat controls
- Refund, dispute, reconciliation, and incident runbooks are approved

## Consequences

**Positive:**
- Release A can launch without any financial risk or on-chain complexity.
- The artifact, moderation, and entitlement infrastructure is validated before money is involved.
- Release B's payment stack builds on proven trust and delivery flows.
- Each release has a clear, testable gate.

**Negative:**
- Free entitlements in Release A will need a migration path when Release B introduces paid entitlements — the entitlement model must support both from the start.
- Some UI surfaces (listing detail, library) will need conditional rendering for the payment affordance that does not exist yet.

**Neutral:**
- SOL as a payment asset is deferred but not excluded — the architecture supports adding it as an optional payment mint after Release B proves the USDC flow.
