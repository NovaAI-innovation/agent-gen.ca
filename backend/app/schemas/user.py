from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    wallet_address: str
    session_id: UUID
    expires_at: datetime


class UserPublic(BaseModel):
    id: UUID
    wallet_address: str
    username: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    reputation_score: int
    is_verified: bool
    # Creator profile fields (public)
    handle: Optional[str] = None
    display_name: Optional[str] = None
    support_link: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CreatorProfileIn(BaseModel):
    handle: str
    display_name: str
    bio: Optional[str] = None
    support_link: Optional[str] = None
    payout_address: Optional[str] = None
    terms_accepted: bool = False


class CreatorProfileOut(BaseModel):
    handle: Optional[str]
    display_name: Optional[str]
    bio: Optional[str]
    support_link: Optional[str]
    payout_address: Optional[str]
    terms_accepted_at: Optional[datetime]
    creator_status: str
    creator_status_at: Optional[datetime]
    reviewer_notes: Optional[str]

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
