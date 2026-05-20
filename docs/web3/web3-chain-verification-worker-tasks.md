# Web3 Chain Verification and Worker Tasks

```yaml
owner: backend_platform
runtime:
  queue: arq
  worker_entrypoint: app.workers.chain_jobs.verify_transaction_job
  solana_config_source: app.core.solana.get_solana_config
```

## P0 - Implement Real Verifier

```yaml
tasks:
  - id: W3-WORKER-001
    priority: P0
    title: "Replace placeholder verify_transaction_job with Solana RPC verification"
    requirements:
      - "Fetch transaction by signature from primary RPC."
      - "Failover to rpc_fallback endpoints on transient errors."
      - "Capture slot, status, logs, and meta payload."
      - "Persist to onchain_transactions table (upsert by signature)."

  - id: W3-WORKER-002
    priority: P0
    title: "Transfer semantic validation"
    requirements:
      - "Match expected recipient wallet from payment_intents."
      - "Match expected mint and expected amount_lamports."
      - "Validate memo binding for purchase/intent identity."
      - "Reject mismatched token program or malformed transfers."

  - id: W3-WORKER-003
    priority: P0
    title: "Deterministic state transitions"
    requirements:
      - "submitted -> confirmed only after semantic validation success."
      - "submitted -> failed with structured failure_reason on mismatch."
      - "pending/submitted -> expired by TTL sweeper."
      - "Write status updates for both payment_intents and purchases."
```

## P1 - Recovery, Retries, and Scheduling

```yaml
tasks:
  - id: W3-WORKER-004
    priority: P1
    title: "Retry strategy and dead-letter behavior"
    requirements:
      - "Exponential backoff for RPC/network failures."
      - "Max retry cap and terminal failed status."
      - "Preserve failure classification for operator triage."

  - id: W3-WORKER-005
    priority: P1
    title: "Background sweeper jobs"
    jobs:
      - "expire_stale_payment_intents"
      - "reconcile_submitted_unconfirmed"
      - "backfill_onchain_observations"
    requirements:
      - "Schedule with clear cadence and lock strategy."

  - id: W3-WORKER-006
    priority: P1
    title: "Idempotent job contracts"
    requirements:
      - "Re-running verifier on same signature is safe."
      - "No duplicate entitlements or duplicate purchase transitions."
```

## P2 - Performance and Reliability

```yaml
tasks:
  - id: W3-WORKER-007
    priority: P2
    title: "RPC client abstraction"
    requirements:
      - "Centralized client module with timeout, retries, and instrumentation."
      - "Support websocket subscription path for faster confirmations (optional)."

  - id: W3-WORKER-008
    priority: P2
    title: "Operational metrics"
    metrics:
      - "verification_latency_seconds"
      - "verification_success_total"
      - "verification_failure_total"
      - "rpc_failover_total"
      - "intent_expired_total"
```

## Acceptance Checklist

```yaml
acceptance:
  - "Given valid tx signature, verifier transitions intent/purchase to confirmed."
  - "Given wrong recipient or amount, verifier transitions to failed with reason."
  - "Worker restart does not corrupt or duplicate state."
  - "Replay of same signature is safe and auditable."
```

