from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: UUID
    wallet_address: str
    username: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    reputation_score: int
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
