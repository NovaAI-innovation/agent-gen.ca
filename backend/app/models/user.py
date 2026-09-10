import uuid
import app.db.database as db
from sqlalchemy import Boolean, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(db.Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_address = Column(String(44), nullable=False, unique=True)  # Solana base58 pubkey
    username = Column(String(50), unique=True, nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    reputation_score = Column(Integer, nullable=False, default=0)
    is_verified = Column(Boolean, nullable=False, default=False)

    # v2: creator trust state — controls whether the user can publish listings
    creator_state = Column(String(30), nullable=False, default="pending_approval")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    listings = relationship("Listing", back_populates="owner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="reviewer", cascade="all, delete-orphan")
