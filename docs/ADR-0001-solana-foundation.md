# ADR-0001: Solana Integration Foundation

## Status
Accepted - 2026-04-03

## Context
The marketplace currently supports wallet-based authentication but does not verify on-chain payments.
Sprint 1 establishes the baseline required for secure Solana payment integration.

## Decision
1. Use native Solana programs first for MVP payment flows.
2. Defer custom on-chain program development to a later sprint unless escrow/dispute logic is required.
3. Standardize runtime configuration for cluster/RPC/token/payment parameters across frontend and backend.

## Program Scope (MVP)
1. System Program (`11111111111111111111111111111111`) for SOL transfer.
2. SPL Token Program (`TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`) for SPL transfers.
3. Token-2022 Program (`TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`) for extension-ready token support.
4. Associated Token Account Program (`ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL`) for wallet ATA creation/lookup.
5. Memo Program (`MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr`) to bind purchase intents to transactions.
6. Compute Budget Program (`ComputeBudget111111111111111111111111111111`) for compute/priority fee controls.

## Config Contract
Backend:
1. `SOLANA_CLUSTER`
2. `SOLANA_RPC_HTTP`
3. `SOLANA_RPC_WS`
4. `SOLANA_RPC_FALLBACK`
5. `USDC_MINT`
6. `PLATFORM_FEE_BPS`

Frontend:
1. `NEXT_PUBLIC_SOLANA_CLUSTER`
2. `NEXT_PUBLIC_SOLANA_RPC_HTTP`
3. `NEXT_PUBLIC_SOLANA_RPC_WS`
4. `NEXT_PUBLIC_SOLANA_RPC_FALLBACK`
5. `NEXT_PUBLIC_USDC_MINT`
6. `NEXT_PUBLIC_PLATFORM_FEE_BPS`

## Consequences
1. Payment verification remains off-chain server validated in Sprint 2.
2. Marketplace can support SOL and SPL payment flows without introducing custom program risk early.
3. If trust-minimized escrow/royalty settlement becomes a hard requirement, add an Anchor program in a later sprint.
