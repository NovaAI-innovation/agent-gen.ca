# Web3 API Backlog (Backend Tasks)

```yaml
owner: backend
status: planned
priority_model: P0_P1_P2
```

## P0 - Payment Intent Lifecycle

```yaml
tasks:
  - id: W3-API-001
    priority: P0
    title: "Create payment intent endpoint"
    endpoint: "POST /purchases/{purchase_id}/intent"
    requirements:
      - "Validate purchase belongs to caller and is pending."
      - "Resolve listing_payment_config and expected recipient wallet."
      - "Compute expected amount_lamports and expected mint."
      - "Generate memo and idempotency key."
      - "Persist payment_intents row with expires_at."
    response_contract:
      - "intent_id"
      - "expected_recipient_wallet"
      - "expected_mint"
      - "expected_amount_lamports"
      - "memo"
      - "expires_at"
    acceptance:
      - "Duplicate client retries with same idempotency key return same logical intent."

  - id: W3-API-002
    priority: P0
    title: "Submit transaction signature for existing payment intent"
    endpoint: "POST /payment-intents/{intent_id}/submit"
    requirements:
      - "Validate intent status is pending and not expired."
      - "Store submitted_signature and set status=submitted atomically."
      - "Enqueue verify_transaction_job(signature, intent_id)."
      - "Prevent signature reuse across intents."
    acceptance:
      - "Second submit attempt is safe and idempotent."
      - "Status transitions are monotonic and audited."

  - id: W3-API-003
    priority: P0
    title: "Intent status polling endpoint"
    endpoint: "GET /payment-intents/{intent_id}"
    requirements:
      - "Return intent status, failure reason, and relevant purchase linkage."
      - "Return confirmed slot/finalized metadata when available."
```

## P1 - Purchase and Listing Flow Refactor

```yaml
tasks:
  - id: W3-API-004
    priority: P1
    title: "Refactor purchase confirm flow to intent-driven confirmation"
    impacted_endpoint: "POST /purchases/{purchase_id}/confirm"
    requirements:
      - "Deprecate direct trust path."
      - "Either remove endpoint or make it alias to intent submission semantics."
      - "Only mark purchase confirmed from verifier result."

  - id: W3-API-005
    priority: P1
    title: "Expose entitlement state to listing detail UI"
    endpoints:
      - "GET /listings/{slug}/entitlement"
      - "GET /users/me/entitlements?listing_id=..."
    requirements:
      - "Return can_install, source, granted_at, revoked_at."
      - "Include free-listing auto-entitlement behavior."

  - id: W3-API-006
    priority: P1
    title: "Add listing payment config management endpoints"
    endpoints:
      - "GET /listings/{slug}/payment-config"
      - "PUT /listings/{slug}/payment-config"
    requirements:
      - "Owner-only access."
      - "Validate wallet/mint formats."
      - "Track active flag and platform_fee_bps bounds."
```

## P2 - Admin and Reconciliation APIs

```yaml
tasks:
  - id: W3-API-007
    priority: P2
    title: "Admin replay endpoint for failed/expired intents"
    endpoint: "POST /admin/payment-intents/{intent_id}/replay"
    requirements:
      - "Restricted auth."
      - "Replay-safe and fully audited."

  - id: W3-API-008
    priority: P2
    title: "Reconciliation query endpoints"
    endpoints:
      - "GET /admin/onchain-transactions"
      - "GET /admin/purchases/reconciliation"
    requirements:
      - "Filter by status, slot range, signature, listing, buyer."
```

## Data Contract Tasks

```yaml
schemas_to_add:
  - "PaymentIntentCreateOut"
  - "PaymentIntentSubmitIn"
  - "PaymentIntentOut"
  - "EntitlementOut"
  - "ListingPaymentConfigIn/Out"
  - "OnchainVerificationResultOut"
```

