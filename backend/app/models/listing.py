import uuid
import app.db.database as db
from sqlalchemy import Boolean, Column, Numeric, String, Text, Integer, TIMESTAMP, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import enum


class ListingType(str, enum.Enum):
    mcp_server = "mcp_server"
    agent_skill = "agent_skill"
    custom_agent = "custom_agent"
    pack = "pack"


class Listing(db.Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(SAEnum(ListingType, name="listing_type"), nullable=False)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_published = Column(Boolean, nullable=False, default=False)
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


class ListingVersion(db.Base):
    __tablename__ = "listing_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(20), nullable=False)
    changelog = Column(Text, nullable=True)
    config_json = Column(JSONB, nullable=True)
    install_instructions = Column(Text, nullable=True)
    is_latest = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    listing = relationship("Listing", back_populates="versions")
