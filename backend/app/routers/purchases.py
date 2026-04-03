from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.deps import get_current_user
from ..db.database import get_db
from ..models.listing import Listing
from ..models.purchase import Purchase, PurchaseStatus, Tip
from ..models.user import User
from ..schemas.purchase import PurchaseOut, PurchaseCreate, PurchaseConfirm, TipCreate

router = APIRouter(tags=["purchases"])


@router.post("/purchases", response_model=PurchaseOut, status_code=201)
async def initiate_purchase(
    data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Listing).where(Listing.id == data.listing_id))
    listing = result.scalar_one_or_none()
    if not listing or not listing.is_published:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.price_sol == 0:
        raise HTTPException(status_code=400, detail="This listing is free — no purchase required")
    if listing.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot purchase your own listing")

    purchase = Purchase(
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.owner_id,
        price_sol=listing.price_sol,
        status=PurchaseStatus.pending,
    )
    db.add(purchase)
    await db.commit()
    await db.refresh(purchase)
    return purchase


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
    purchase.status = PurchaseStatus.confirmed
    await db.commit()
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
