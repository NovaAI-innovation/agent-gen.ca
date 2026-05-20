from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.solana_rpc import get_transaction, verify_sol_transfer
from app.models.purchase import Entitlement, OnchainTransaction, Purchase, PurchaseStatus

logger = logging.getLogger(__name__)

LAMPORTS_PER_SOL = 1_000_000_000


async def verify_purchase_on_chain(purchase_id: UUID, db: AsyncSession) -> bool:
    """
    Fetch the on-chain transaction for a purchase and confirm it is valid.

    On success:
      - Sets purchase.status = confirmed, records slot + finalized_at
      - Stores the raw transaction in onchain_transactions
      - Creates an Entitlement for the buyer

    On failure:
      - Sets purchase.status = failed, records failure_reason

    Returns True if verification succeeded, False otherwise.
    Raises httpx.HTTPError if the Solana RPC is unreachable (caller decides retry policy).
    """
    result = await db.execute(
        select(Purchase)
        .where(Purchase.id == purchase_id)
        .options(selectinload(Purchase.buyer), selectinload(Purchase.seller))
    )
    purchase = result.scalar_one_or_none()
    if not purchase:
        raise ValueError(f"Purchase {purchase_id} not found")

    if not purchase.tx_signature:
        purchase.status = PurchaseStatus.failed
        purchase.failure_reason = "No transaction signature on record"
        await db.commit()
        return False

    # Propagate RPC errors to the caller — they can decide to retry or mark pending.
    tx = await get_transaction(purchase.tx_signature, commitment="finalized")

    if tx is None:
        purchase.status = PurchaseStatus.failed
        purchase.failure_reason = "Transaction not found on-chain (may not be finalized yet)"
        await db.commit()
        return False

    expected_lamports = purchase.amount_lamports or int(purchase.price_sol * LAMPORTS_PER_SOL)
    ok, reason = verify_sol_transfer(
        tx,
        expected_sender=purchase.buyer.wallet_address,
        expected_recipient=purchase.seller.wallet_address,
        expected_lamports=expected_lamports,
    )

    now = datetime.now(timezone.utc)

    # Store raw transaction for audit regardless of outcome.
    meta = tx.get("meta", {}) or {}
    existing_tx = await db.execute(
        select(OnchainTransaction).where(OnchainTransaction.signature == purchase.tx_signature)
    )
    if not existing_tx.scalar_one_or_none():
        db.add(
            OnchainTransaction(
                signature=purchase.tx_signature,
                cluster=purchase.cluster,
                slot=tx.get("slot"),
                confirmation_status="finalized",
                err_json=meta.get("err"),
                logs_json=meta.get("logMessages"),
                raw_meta_json=meta,
                finalized_at=now if not meta.get("err") else None,
            )
        )

    if not ok:
        purchase.status = PurchaseStatus.failed
        purchase.failure_reason = reason
        await db.commit()
        return False

    purchase.status = PurchaseStatus.confirmed
    purchase.confirmed_slot = tx.get("slot")
    purchase.finalized_at = now

    # Grant the buyer an entitlement.
    db.add(
        Entitlement(
            user_id=purchase.buyer_id,
            listing_id=purchase.listing_id,
            purchase_id=purchase.id,
            source="purchase",
        )
    )

    await db.commit()
    return True


class WorkerSettings:
    functions = [verify_purchase_on_chain]
    from .settings import redis_settings
