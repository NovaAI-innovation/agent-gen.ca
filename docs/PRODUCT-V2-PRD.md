# agent-gen.ca v2 Product Requirements Document

Status: implementation-ready planning baseline  
Delivery model: long-running Ralph loop, one story and one pull request at a time  
Release strategy: curated free beta, followed by paid USDC mainnet

## 1. Product decision

agent-gen.ca v2 is a curated marketplace for installable AI-agent components. Buyers discover, evaluate, acquire, and install MCP servers, skills, agents, and packs. Creators publish versioned artifacts with explicit permissions, compatibility, provenance, and support information.

The product launches as a curated registry. A connected wallet proves control of an address; it does not prove that a creator or listing is trustworthy. The platform establishes trust through moderation, signed release manifests, artifact scanning, transparent publisher history, and verified transaction records.

## 2. Release boundaries

### Release A: curated free beta

Release A validates the marketplace without financial risk. It includes wallet sign-in, creator onboarding, draft and review workflows, moderated free listings, versioned artifacts, protected downloads, buyer libraries, real analytics, legal pages, and production VPS operations.

Release A excludes paid listings, tips, platform fees, public self-service publishing, escrow, disputes, refunds, and claims that are not backed by production data.

### Release B: paid mainnet

Release B adds USDC-denominated purchases, platform fees, payment intents, exact on-chain verification, asynchronous reconciliation, entitlements, receipts, refund and dispute operations, and finance-grade observability. SOL pays network fees and may become an optional payment asset later.

## 3. Goals

1. Let a buyer understand a listing's purpose, publisher, permissions, compatibility, and trust status before installation.
2. Let an approved creator publish a valid, versioned artifact through a reviewable workflow.
3. Make every installation traceable to a release manifest and entitlement.
4. Make every paid entitlement traceable to a finalized, semantically verified transaction.
5. Run the service safely on one VPS with tested backup, restore, deploy, and rollback procedures.
6. Present a focused, credible interface whose public claims come from live data.

## 4. Non-goals

1. Escrow or an on-chain marketplace program in Release A or B.
2. Anonymous public publishing.
3. Custody of user wallets or private keys.
4. Automated endorsement of arbitrary agent code.
5. Multi-chain support.
6. Social feeds, follower counts, or reputation graphs before marketplace trust is proven.
7. A broad affiliate-resource directory inside the primary marketplace navigation.

## 5. Users and jobs

### Buyer

- Find a component for a specific agent runtime or task.
- Compare compatibility, permissions, support, price, and trust signals.
- Acquire a listing with a clear transaction summary.
- Install a specific version and return to it later from a personal library.
- Report unsafe, deceptive, or broken content.

### Creator

- Prove wallet control and complete a public publisher profile.
- Create a draft that matches a listing-type schema.
- Upload or reference an artifact, define its permissions, and pass validation.
- Preview and submit a release for moderation.
- Publish updates and view real installs, revenue, and support signals.

### Moderator/operator

- Review creators, listings, releases, scans, and reports.
- Approve, reject, suspend, revoke, or restore records with reasons.
- Reconcile payments and entitlements without editing the database directly.
- Inspect system health, queue lag, RPC health, and security events.

## 6. Product principles

1. Truth before promotion. Display only measured metrics and implemented capabilities.
2. Trust before transaction. Put provenance, permissions, compatibility, and publisher identity before price.
3. Progressive commitment. Browsing requires no wallet; publishing, saving, acquiring, and installing do.
4. Explicit states. Draft, review, published, pending, finalized, failed, expired, revoked, and suspended must remain distinct.
5. Safe recovery. Every long-running operation must support retry, idempotency, audit history, and operator recovery.
6. One primary action per screen. Secondary actions must not compete with the next intended step.

## 7. Information architecture

### Public navigation

- Marketplace
- Publish
- Documentation
- Connect wallet

MCP Servers, Skills, Agents, and Packs become marketplace filters. Resources moves to documentation or leaves the launch scope.

### Buyer surfaces

- Marketing home
- Marketplace search and collections
- Listing detail and release history
- Checkout and transaction status
- Personal library
- Install instructions and artifact delivery
- Saved listings and reports

### Creator surfaces

- Creator onboarding
- Studio overview
- Draft editor
- Release and artifact editor
- Preview and review submission
- Listing and release management
- Install and revenue analytics
- Payout configuration

### Operator surfaces

- Creator review queue
- Listing and release moderation queue
- Abuse reports
- Artifact scan results
- Payment reconciliation
- Entitlement repair
- Operational health and audit log

## 8. Functional requirements

### Identity and sessions

- Use Wallet Standard Sign In With Solana where supported, with a legacy message-signing fallback.
- Generate sign-in inputs server-side and verify exact domain, URI, address, chain, nonce, issued-at, and expiry values.
- Store refresh credentials in secure HttpOnly cookies and access credentials in memory.
- Rotate sessions atomically and revoke them from an operator or user session list.
- Apply shared Redis-backed rate limits at the edge and application layers.

### Catalog and publishing

- Create drafts by default.
- Validate lengths, formats, prices, categories, licenses, URLs, and listing-type fields on the API.
- Model creator, listing, release, artifact, moderation, and publication states separately.
- Require an approved creator and approved release before public publication.
- Preserve immutable release records; corrections create a new release.

### Artifact and installation

- Every release has a manifest, semantic version, artifact URI, SHA-256 digest, size, media type, license, compatibility data, permission declarations, and install instructions.
- Uploads use short-lived signed URLs and private object storage.
- A scanner quarantines artifacts until policy checks pass.
- Downloads use short-lived entitlement-bound URLs and append-only audit records.
- Install counters derive from deduplicated install events rather than a mutable public counter.

### Marketplace trust

- Listing detail shows publisher history, verification level, scan status, source availability, release age, compatibility, required permissions, support policy, and reports policy.
- Reviews require an acquired entitlement; creators cannot review their own listings.
- Users can report listings, releases, creators, and reviews.
- Moderators can suspend access immediately without destroying evidence.

### Payments and entitlements

- Release B prices products in USDC.
- The server creates a payment intent that freezes buyer, seller, listing, release, mint, amount, fee, recipient accounts, memo/reference, cluster, and expiry.
- Submission accepts one transaction signature per intent and enqueues verification.
- The verifier parses exact token instructions, account ownership, mint, amount, recipients, fee split, memo/reference, signer, cluster, error state, and finality.
- Only the verifier grants a paid entitlement.
- Replays, duplicate signatures, concurrent submissions, RPC disagreement, timeouts, expiry, and reorg/fork outcomes have explicit state transitions.

### Operations

- Operators can replay failed verification jobs and rebuild entitlements from confirmed records.
- Health endpoints distinguish liveness, readiness, and dependency health.
- Logs use request, user, intent, purchase, and job correlation IDs without storing secrets.
- Metrics cover request errors, authentication failures, queue lag, RPC latency/failover, intent expiry, verification failures, and entitlement drift.

## 9. Non-functional requirements

- Accessibility: WCAG 2.2 AA; automated checks plus keyboard and screen-reader review.
- Performance: p75 LCP under 2.5 seconds on production mobile; no layout shift from wallet controls.
- Security: no unresolved critical or high dependency findings; threat model and independent payment review complete before Release B.
- Reliability: repeatable deploy and rollback; daily encrypted off-site database backups; quarterly restore exercise.
- Privacy: collect the minimum personal data; document retention for IP and user-agent hashes.
- Browser support: current Chrome, Edge, Firefox, Safari, Phantom mobile browser, and Solana Mobile Wallet Adapter path.

## 10. Success metrics

Release A measures approved creators, approved listings, successful artifact validations, listing-detail-to-install conversion, installation success, report rate, and seven-day buyer return rate.

Release B adds checkout start-to-finality conversion, median confirmation time, intent expiry rate, verification failure rate, entitlement drift, seller revenue, and reconciliation age.

Public metric cards must query measured values and display their time window. The interface must never substitute aspirational values.

## 11. Launch gates

### Release A gate

- At least ten legitimate, reviewed listings from at least three approved creators.
- All public listings have installable releases and passing scans.
- Terms, Privacy, Acceptable Use, Security, and reporting flows are live.
- Production dependency and container scans have no unresolved critical or high findings.
- Backup restore and deploy rollback succeed on staging.
- Desktop, mobile, keyboard, and accessibility test suites pass.

### Release B gate

- Payment state-machine, semantic verifier, replay, and chaos tests pass.
- Staging completes at least 100 successful devnet purchase simulations.
- A 24-hour production-like soak has no unresolved P0 or P1 incident.
- An independent reviewer signs off on payment, entitlement, auth, and operational threat controls.
- Refund, dispute, reconciliation, and incident runbooks are approved.

## 12. Target architecture

```text
Internet
  -> single TLS edge proxy
     -> Next.js web
     -> FastAPI API
        -> PostgreSQL
        -> Redis queue/rate-limit store
        -> private object storage
     -> chain verification worker
     -> artifact scanning worker
     -> metrics, logs, and alerts
```

Only ports 80 and 443 reach the public network. PostgreSQL, Redis, workers, and administrative tools remain on private container networks. Staging uses a separate database, object prefix, Redis namespace, Solana devnet configuration, and hostname.

