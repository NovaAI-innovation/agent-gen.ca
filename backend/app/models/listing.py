import enum
import uuid

import app.db.database as db
from sqlalchemy import Boolean, Column, Numeric, String, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ListingType(str, enum.Enum):
    mcp_server = "mcp_server"
    agent_skill = "agent_skill"
    custom_agent = "custom_agent"
    pack = "pack"


class Listing(db.Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(30), nullable=False)  # ListingType values
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # v2: state replaces is_published; drafts never appear in public queries
    state = Column(String(30), nullable=False, default="draft")

    is_featured = Column(Boolean, nullable=False, default=False)
    price_sol = Column(Numeric(18, 9), nullable=False, default=0)
    download_count = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, nullable=False, default=0)
    avg_rating = Column(Numeric(3, 2), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner = relationship("User", back_populates="listings")
    versions = relationship("ListingVersion", back_populates="listing", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="listing", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="listing_tags", back_populates="listings")
    categories = relationship("Category", secondary="listing_categories", back_populates="listings")

    # Computed helpers for backward compat during migration
    @property
    def is_published(self) -> bool:
        """Backward-compat helper — True when state is 'published'."""
        return self.state == "published"


class ListingVersion(db.Base):
    __tablename__ = "listing_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(20), nullable=False)
    changelog = Column(Text, nullable=True)
    config_json = Column(JSONB, nullable=True)
    install_instructions = Column(Text, nullable=True)
    is_latest = Column(Boolean, nullable=False, default=True)

    # v2: release state tracks the version lifecycle independently
    state = Column(String(30), nullable=False, default="draft")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    listing = relationship("Listing", back_populates="versions")
