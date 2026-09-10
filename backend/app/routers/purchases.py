from datetime import datetime, timezone
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.deps import get_current_user
from ..crud.listing import get_listing_by_slug
from ..db.database import get_db
from ..models.listing import Listing
from ..models.purchase import Entitlement, Purchase, PurchaseStatus, Tip
from ..models.user import User
from ..schemas.purchase import PurchaseOut, PurchaseCreate, PurchaseConfirm, TipCreate
from ..workers.chain_jobs import verify_purchase_on_chain


async def _get_seller_wallet(db: AsyncSession, seller_id: UUID) -> str | None:
    result = await db.execute(select(User).where(User.id == seller_id))
    user = result.scalar_one_or_none()
    return user.wallet_address if user else None


def _purchase_response(purchase: Purchase, seller_wallet: str | None) -> dict:
    """Build a PurchaseOut-compatible dict including seller wallet for client-side payments."""
    return {
        "id": purchase.id,
        "listing_id": purchase.listing_id,
        "buyer_id": purchase.buyer_id,
        "seller_id": purchase.seller_id,
        "price_sol": purchase.price_sol,
        "amount_lamports": purchase.amount_lamports,
        "tx_signature": purchase.tx_signature,
        "status": purchase.status,
        "created_at": purchase.created_at,
        "seller_wallet_address": seller_wallet,
    }

router = APIRouter(tags=["purchases"])

LAMPORTS_PER_SOL = 1_000_000_000


async def _create_purchase_for_listing(
    listing: Listing,
    *,
    current_user: User,
    db: AsyncSession,
) -> Purchase:
    if listing.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot purchase your own listing")

    price_lamports = int(listing.price_sol * LAMPORTS_PER_SOL)

    if listing.price_sol == 0:
        # Free listing: confirm immediately and grant entitlement.
        purchase = Purchase(
            listing_id=listing.id,
            buyer_id=current_user.id,
            seller_id=listing.owner_id,
            price_sol=listing.price_sol,
            amount_lamports=0,
            status=PurchaseStatus.confirmed,
            finalized_at=datetime.now(timezone.utc),
        )
        db.add(purchase)
        await db.flush()  # populate purchase.id
        db.add(
            Entitlement(
                user_id=current_user.id,
                listing_id=listing.id,
                purchase_id=purchase.id,
                source="free",
            )
        )
        await db.commit()
        await db.refresh(purchase)
        return purchase

    purchase = Purchase(
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.owner_id,
        price_sol=listing.price_sol,
        amount_lamports=price_lamports,
        status=PurchaseStatus.pending,
    )
    db.add(purchase)
    await db.commit()
    await db.refresh(purchase)
    return purchase


@router.post("/purchases", response_model=PurchaseOut, status_code=201)
async def initiate_purchase(
    data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Listing).where(Listing.id == data.listing_id))
    listing = result.scalar_one_or_none()
    if not listing or listing.state != "published":
        raise HTTPException(status_code=404, detail="Listing not found")
    purchase = await _create_purchase_for_listing(listing, current_user=current_user, db=db)
    seller_wallet = await _get_seller_wallet(db, purchase.seller_id)
    return _purchase_response(purchase, seller_wallet)


@router.post("/listings/{slug}/purchase", response_model=PurchaseOut, status_code=201)
async def initiate_purchase_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing or listing.state != "published":
        raise HTTPException(status_code=404, detail="Listing not found")
    purchase = await _create_purchase_for_listing(listing, current_user=current_user, db=db)
    seller_wallet = await _get_seller_wallet(db, purchase.seller_id)
    return _purchase_response(purchase, seller_wallet)


@router.post("/purchases/{purchase_id}/confirm", response_model=PurchaseOut)
async def confirm_purchase(
    purchase_id: UUID,
    data: PurchaseConfirm,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Purchase).where(Purchase.id == purchase_id))
    purchase = result.scalar_one_or_none()
    if not purchase or purchase.buyer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if purchase.status != PurchaseStatus.pending:
        raise HTTPException(status_code=400, detail="Purchase already processed")

    purchase.tx_signature = data.tx_signature
    await db.flush()

    try:
        confirmed = await verify_purchase_on_chain(purchase.id, db)
    except httpx.HTTPError:
        # RPC unreachable — keep status pending, caller can retry later.
        await db.commit()
        await db.refresh(purchase)
        return purchase

    if not confirmed:
        await db.refresh(purchase)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=purchase.failure_reason or "On-chain verification failed",
        )

    await db.refresh(purchase)
    return purchase


@router.post("/tips", status_code=204)
async def send_tip(
    data: TipCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.to_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot tip yourself")
    tip = Tip(
        from_user_id=current_user.id,
        to_user_id=data.to_user_id,
        listing_id=data.listing_id,
        amount_sol=data.amount_sol,
        tx_signature=data.tx_signature,
        message=data.message,
    )
    db.add(tip)
    await db.commit()
