"""Async Solana JSON-RPC client for on-chain transaction verification."""
from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(timeout=10.0)
_SOL_NATIVE_MINT = "So11111111111111111111111111111111111111112"


def _rpc_endpoints() -> list[str]:
    primary = settings.SOLANA_RPC_HTTP
    fallbacks = [
        ep.strip()
        for ep in (settings.SOLANA_RPC_FALLBACK or "").split(",")
        if ep.strip()
    ]
    return [primary] + fallbacks


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
async def get_transaction(signature: str, *, commitment: str = "finalized") -> dict[str, Any] | None:
    """
    Fetch a transaction from Solana RPC by signature.

    Returns the result dict from the RPC response, or None if the transaction
    is not found. Tries primary RPC first, then falls back through SOLANA_RPC_FALLBACK.

    Raises httpx.HTTPError if all endpoints are unreachable.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "json",
                "commitment": commitment,
                "maxSupportedTransactionVersion": 0,
            },
        ],
    }

    last_error: Exception | None = None
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        for endpoint in _rpc_endpoints():
            try:
                resp = await client.post(endpoint, json=payload)
                resp.raise_for_status()
                data = resp.json()
                rpc_result = data.get("result")
                return rpc_result  # None means "not found / not yet finalized"
            except httpx.HTTPError as exc:
                logger.warning("Solana RPC request failed for %s: %s", endpoint, exc)
                last_error = exc

    raise last_error or httpx.RequestError("All Solana RPC endpoints unreachable")


def verify_sol_transfer(
    tx: dict[str, Any],
    *,
    expected_sender: str,
    expected_recipient: str,
    expected_lamports: int,
) -> tuple[bool, str]:
    """
    Inspect a fetched transaction and verify it represents a valid SOL payment.

    Returns (True, "") on success or (False, reason) on failure.
    """
    meta = tx.get("meta")
    if meta is None:
        return False, "Transaction meta is missing"

    if meta.get("err") is not None:
        return False, f"Transaction contains an error: {meta['err']}"

    transaction = tx.get("transaction")
    if not transaction:
        return False, "Transaction data is missing"

    message = transaction.get("message", {})
    account_keys: list[str] = message.get("accountKeys", [])
    pre_balances: list[int] = meta.get("preBalances", [])
    post_balances: list[int] = meta.get("postBalances", [])

    if not account_keys or not pre_balances or not post_balances:
        return False, "Transaction is missing account keys or balance data"

    # Fee payer (index 0) must be the buyer.
    if account_keys[0] != expected_sender:
        return False, f"Transaction sender {account_keys[0]} does not match buyer {expected_sender}"

    # Recipient must be in the account list.
    if expected_recipient not in account_keys:
        return False, f"Expected recipient {expected_recipient} not found in transaction accounts"

    recipient_index = account_keys.index(expected_recipient)
    if recipient_index >= len(pre_balances) or recipient_index >= len(post_balances):
        return False, "Balance array shorter than account keys"

    received_lamports = post_balances[recipient_index] - pre_balances[recipient_index]
    if received_lamports < expected_lamports:
        return False, (
            f"Recipient received {received_lamports} lamports, "
            f"expected at least {expected_lamports}"
        )

    return True, ""
