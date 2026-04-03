from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ReviewOut(BaseModel):
    id: UUID
    listing_id: UUID
    reviewer_id: UUID
    rating: int
    title: Optional[str]
    body: Optional[str]
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    body: Optional[str] = None
