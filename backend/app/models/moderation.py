"""Listing lifecycle state machine with constrained transitions and audit records.

State machine for creator, listing, and release states as defined by the v2
catalog bounded context.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import app.db.database as db
from sqlalchemy import Column, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# ── Listing State Machine ─────────────────────────────────────────────────────


class ListingState(str):
    """Constrained listing lifecycle states."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    ARCHIVED = "archived"

    @classmethod
    def transitions(cls, from_state: str) -> list[str]:
        """Return valid next states given the current state."""
        _transitions = {
            cls.DRAFT: [cls.PENDING_REVIEW],
            cls.PENDING_REVIEW: [cls.APPROVED, cls.REJECTED, cls.DRAFT],
            cls.APPROVED: [cls.PUBLISHED, cls.DRAFT],
            cls.PUBLISHED: [cls.DRAFT, cls.ARCHIVED],
            cls.REJECTED: [cls.DRAFT],
            cls.ARCHIVED: [cls.DRAFT],
        }
        return _transitions.get(from_state, [])

    @classmethod
    def can_transition(cls, from_state: str, to_state: str) -> bool:
        """Return True when the requested transition is valid."""
        return to_state in cls.transitions(from_state)

    @classmethod
    def publicly_visible_states(cls) -> set[str]:
        """States that appear in public marketplace queries."""
        return {cls.PUBLISHED}

    @classmethod
    def editable_states(cls) -> set[str]:
        """States that allow the creator to edit the listing."""
        return {cls.DRAFT, cls.REJECTED}

    @classmethod
    def initial_state(cls) -> str:
        return cls.DRAFT


# ── Moderation Audit Event ────────────────────────────────────────────────────


class ModerationEvent(db.Base):
    """Immutable audit record for every listing state transition.

    Includes both automated transitions (creator submit, system publish)
    and manual moderator actions.
    """

    __tablename__ = "moderation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUID(int=0))
    listing_id = Column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    from_state = Column(String(20), nullable=False)
    to_state = Column(String(20), nullable=False)
    reason = Column(Text, nullable=True)  # Moderator notes or automated trigger
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    listing = relationship("Listing", foreign_keys=[listing_id])
    actor = relationship("User", foreign_keys=[actor_id])


# ── State transition helper ────────────────────────────────────────────────────


async def record_transition(
    db_session,
    listing_id: UUID,
    from_state: str,
    to_state: str,
    *,
    actor_id: UUID | None = None,
    reason: str | None = None,
) -> ModerationEvent:
    """Create an immutable audit record for a listing state transition."""
    event = ModerationEvent(
        id=UUID(int=0),
        listing_id=listing_id,
        actor_id=actor_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
    )
    db_session.add(event)
    return event