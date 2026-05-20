# Web3 Security, Testing, and Rollout Tasks

```yaml
owner: backend_security_and_qe
scope:
  - payment_integrity
  - entitlement_integrity
  - operational_readiness
```

## Security Tasks

```yaml
tasks:
  - id: W3-SEC-001
    priority: P0
    title: "Remove client-trust confirmation path"
    requirements:
      - "No endpoint may set Purchase.status=confirmed from raw client input only."
      - "All confirmation flows route through verifier outcomes."

  - id: W3-SEC-002
    priority: P0
    title: "Replay and duplication protection"
    requirements:
      - "Enforce uniqueness of submitted_signature + idempotency key."
      - "Guard against intent hijack (signature submitted to wrong intent)."
      - "Lock status transitions with transactional checks."

  - id: W3-SEC-003
    priority: P1
    title: "AuthZ hardening for payment and admin surfaces"
    requirements:
      - "Buyer-only access to buyer intent endpoints."
      - "Owner-only payment config management."
      - "Admin-only reconciliation and replay endpoints."
```

## Test Tasks

```yaml
tasks:
  - id: W3-TEST-001
    priority: P0
    title: "Unit tests for payment intent state machine"
    cases:
      - "pending -> submitted -> confirmed"
      - "pending -> expired"
      - "submitted -> failed"
      - "duplicate submit handling"

  - id: W3-TEST-002
    priority: P0
    title: "Verifier semantic tests"
    cases:
      - "recipient mismatch"
      - "mint mismatch"
      - "amount mismatch"
      - "memo mismatch"
      - "cluster mismatch"

  - id: W3-TEST-003
    priority: P1
    title: "Integration tests for API + worker flow"
    flow:
      - "create purchase"
      - "create intent"
      - "submit signature"
      - "worker verifies"
      - "purchase + entitlement become confirmed/granted"

  - id: W3-TEST-004
    priority: P1
    title: "Chaos/failure tests"
    cases:
      - "RPC timeout and fallback success"
      - "worker retry exhaustion"
      - "DB deadlock retry safety"
```

## Rollout Tasks

```yaml
tasks:
  - id: W3-OPS-001
    priority: P0
    title: "Environment and secrets readiness"
    requirements:
      - "Finalize SOLANA_RPC_HTTP/WS/FALLBACK values per environment."
      - "Set ENFORCE_ALEMBIC_VERSION and expected revision in production."
      - "Validate REDIS_URL and worker deployment topology."

  - id: W3-OPS-002
    priority: P1
    title: "Monitoring and alerting"
    alerts:
      - "intent_verification_failure_rate_high"
      - "intent_expiry_spike"
      - "worker_queue_lag_high"
      - "rpc_failover_rate_high"

  - id: W3-OPS-003
    priority: P1
    title: "Runbook and backfill procedures"
    runbooks:
      - "manual_intent_replay"
      - "stuck_submitted_reconciliation"
      - "entitlement_rebuild_from_purchases"
```

## Go-Live Criteria

```yaml
go_live:
  required:
    - "All P0 security and test tasks completed."
    - "Intent flow enabled for 100% paid listing purchases."
    - "24h soak in staging with no unresolved critical incidents."
  post_launch:
    - "Enable reconciliation dashboards."
    - "Schedule periodic integrity audit across purchases/intents/entitlements."
```

