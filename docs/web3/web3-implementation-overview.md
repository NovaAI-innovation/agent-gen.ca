# Web3 Implementation - Remaining Work Overview

```yaml
snapshot:
  created_on: 2026-04-04
  scope: backend_web3
  current_state:
    foundation_present:
      - "Schema/migration: 0004_web3_foundation"
      - "Models: PaymentIntent, OnchainTransaction, ListingPaymentConfig, Entitlement"
      - "Config: SOLANA_* runtime settings and USDC/platform fee settings"
      - "Worker scaffold: verify_transaction_job placeholder"
    partially_implemented:
      - "Purchase initiation endpoints"
      - "Manual purchase confirm endpoint (currently trusts submitted tx signature)"
      - "Install/download tracking endpoint"
    missing_core_capabilities:
      - "Payment intent lifecycle API"
      - "On-chain transaction verification and reconciliation"
      - "Entitlement grant/revoke lifecycle wired to chain confirmation"
      - "Listing payment configuration management"
      - "Operational controls, observability, and replay-safe idempotency"
```

## Phase Plan

```yaml
phases:
  - id: W3-PHASE-1
    title: "Payment Intent API and Data Contracts"
    goal: "Stop directly trusting tx_signature from clients; move to intent-driven flow."
  - id: W3-PHASE-2
    title: "On-Chain Verification and Worker Processing"
    goal: "Verify signatures and transfer semantics against Solana RPC before confirmation."
  - id: W3-PHASE-3
    title: "Entitlements and Access Enforcement"
    goal: "Grant/revoke rights from confirmed chain outcomes and enforce install access."
  - id: W3-PHASE-4
    title: "Listing Payment Config and Multi-Asset Readiness"
    goal: "Per-listing payout wallet + accepted mint + fee policy support."
  - id: W3-PHASE-5
    title: "Security, Reliability, and Production Rollout"
    goal: "Harden replay protection, idempotency, metrics, alerts, and runbooks."
```

## Critical Path

```yaml
critical_path:
  - "1. Implement payment intents endpoints and schemas (W3-PHASE-1)"
  - "2. Wire worker queue and on-chain verifier (W3-PHASE-2)"
  - "3. Replace direct purchase confirm with intent submission + verifier callback"
  - "4. Issue entitlements only on verified confirmed/finalized transactions (W3-PHASE-3)"
  - "5. Add observability and failure recovery controls before production cutover (W3-PHASE-5)"
```

## Done Definition

```yaml
done_definition:
  - "Every paid install has a payment_intent record, verification trace, and deterministic status history."
  - "No purchase is marked confirmed solely from client-provided signature."
  - "Entitlements are granted only by verified on-chain success conditions."
  - "Ops can replay failed jobs safely and inspect status from API + logs + DB records."
```

