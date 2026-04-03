import uuid
import app.db.database as db
from sqlalchemy import Boolean, Column, Integer, SmallInteger, String, Text, TIMESTAMP, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

review_helpful = Table(
    "review_helpful",
    db.Base.metadata,
    Column("review_id", ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Review(db.Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    is_verified_purchase = Column(Boolean, nullable=False, default=False)
    helpful_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    listing = relationship("Listing", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
