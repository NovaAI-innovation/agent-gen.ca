from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.purchase import PurchaseStatus


class PurchaseOut(BaseModel):
    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    price_sol: Decimal
    amount_lamports: Optional[int] = None
    tx_signature: Optional[str] = None
    status: PurchaseStatus
    created_at: datetime
    # Populated on creation for paid listings so the client can build the SOL transaction.
    seller_wallet_address: Optional[str] = None

    model_config = {"from_attributes": True}


class PurchaseCreate(BaseModel):
    listing_id: UUID


class PurchaseConfirm(BaseModel):
    tx_signature: str


class TipCreate(BaseModel):
    to_user_id: UUID
    listing_id: Optional[UUID] = None
    amount_sol: Decimal
    tx_signature: str
    message: Optional[str] = None
