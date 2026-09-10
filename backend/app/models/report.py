"""Abuse report model for user-submitted content reports.

Users can report listings, listing versions, or other users.  Each report
produces an immutable record that moderators review through the moderation
queue.
"""

from __future__ import annotations

import enum
import uuid

import app.db.database as db
from sqlalchemy import Column, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ReportStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportEntityType(str, enum.Enum):
    LISTING = "listing"
    RELEASE = "release"
    USER = "user"


class Report(db.Base):
    """User-submitted abuse report."""

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    entity_type = Column(String(20), nullable=False)  # ReportEntityType values
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    reason = Column(String(50), nullable=False)  # e.g. "spam", "malware", "fraud"
    details = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=ReportStatus.OPEN.value)
    resolution_note = Column(Text, nullable=True)
    resolved_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    reporter = relationship("User", foreign_keys=[reporter_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
