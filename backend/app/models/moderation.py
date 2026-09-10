"""Listing lifecycle state machine with constrained transitions and audit records.

State machines for creator, listing, and release (listing version) states
as defined by the v2 catalog bounded context.  Every state transition
produces an immutable audit record.
"""

from __future__ import annotations

import enum
import uuid

import app.db.database as db
from sqlalchemy import Column, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# ── Transition maps (module-level to avoid enum metaclass interference) ───────

_LISTING_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["pending_review"],
    "pending_review": ["approved", "rejected", "draft"],
    "approved": ["published", "draft"],
    "rejected": ["draft"],
    "published": ["draft", "suspended", "archived"],
    "suspended": ["draft", "archived"],
    "archived": ["draft"],
}

_CREATOR_TRANSITIONS: dict[str, list[str]] = {
    "pending_approval": ["approved"],
    "approved": ["suspended"],
    "suspended": ["approved", "banned"],
    "banned": [],
}

_RELEASE_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["pending_review"],
    "pending_review": ["approved", "rejected", "draft"],
    "approved": ["published", "draft"],
    "rejected": ["draft"],
    "published": ["suspended", "archived"],
    "suspended": ["draft", "archived"],
    "archived": ["draft"],
}


# ── Listing State Machine ─────────────────────────────────────────────────────


class ListingState(str, enum.Enum):
    """Constrained listing lifecycle states."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

    @classmethod
    def transitions(cls, from_state: str) -> list[str]:
        """Return valid next states given the current state."""
        return list(_LISTING_TRANSITIONS.get(from_state, []))

    @classmethod
    def can_transition(cls, from_state: str, to_state: str) -> bool:
        """Return True when the requested transition is valid."""
        return to_state in cls.transitions(from_state)

    @classmethod
    def publicly_visible_states(cls) -> set[str]:
        """States that appear in public marketplace queries."""
        return {cls.PUBLISHED.value}

    @classmethod
    def editable_states(cls) -> set[str]:
        """States that allow the creator to edit the listing."""
        return {cls.DRAFT.value, cls.REJECTED.value}

    @classmethod
    def initial_state(cls) -> str:
        return cls.DRAFT.value


# ── Creator State Machine ─────────────────────────────────────────────────────


class CreatorState(str, enum.Enum):
    """Creator trust lifecycle states."""

    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    BANNED = "banned"

    @classmethod
    def transitions(cls, from_state: str) -> list[str]:
        return list(_CREATOR_TRANSITIONS.get(from_state, []))

    @classmethod
    def can_transition(cls, from_state: str, to_state: str) -> bool:
        return to_state in cls.transitions(from_state)

    @classmethod
    def can_publish(cls, state: str) -> bool:
        """Only approved creators can create or submit listings."""
        return state == cls.APPROVED.value

    @classmethod
    def initial_state(cls) -> str:
        return cls.PENDING_APPROVAL.value


# ── Release (Listing Version) State Machine ───────────────────────────────────


class ReleaseState(str, enum.Enum):
    """Release lifecycle states — mirrors listing states but scoped to a
    specific version / artifact."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

    @classmethod
    def transitions(cls, from_state: str) -> list[str]:
        return list(_RELEASE_TRANSITIONS.get(from_state, []))

    @classmethod
    def can_transition(cls, from_state: str, to_state: str) -> bool:
        return to_state in cls.transitions(from_state)

    @classmethod
    def initial_state(cls) -> str:
        return cls.DRAFT.value


# ── Moderation Audit Events ───────────────────────────────────────────────────


class ListingModerationEvent(db.Base):
    """Immutable audit record for every listing state transition."""

    __tablename__ = "listing_moderation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    from_state = Column(String(30), nullable=False)
    to_state = Column(String(30), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    listing = relationship("Listing", foreign_keys=[listing_id])
    actor = relationship("User", foreign_keys=[actor_id])


class CreatorModerationEvent(db.Base):
    """Immutable audit record for every creator state transition."""

    __tablename__ = "creator_moderation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    from_state = Column(String(30), nullable=False)
    to_state = Column(String(30), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    creator = relationship("User", foreign_keys=[creator_id])
    actor = relationship("User", foreign_keys=[actor_id])


class ReleaseModerationEvent(db.Base):
    """Immutable audit record for every release (listing version) state transition."""

    __tablename__ = "release_moderation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_id = Column(
        UUID(as_uuid=True),
        ForeignKey("listing_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    listing_id = Column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    from_state = Column(String(30), nullable=False)
    to_state = Column(String(30), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    release = relationship("ListingVersion", foreign_keys=[release_id])
    listing = relationship("Listing", foreign_keys=[listing_id])
    actor = relationship("User", foreign_keys=[actor_id])


# ── State transition helpers ──────────────────────────────────────────────────


async def record_listing_transition(
    db_session,
    listing_id,
    from_state: str,
    to_state: str,
    *,
    actor_id=None,
    reason: str | None = None,
) -> ListingModerationEvent:
    """Create an immutable audit record for a listing state transition."""
    event = ListingModerationEvent(
        listing_id=listing_id,
        actor_id=actor_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
    )
    db_session.add(event)
    return event


async def record_creator_transition(
    db_session,
    creator_id,
    from_state: str,
    to_state: str,
    *,
    actor_id=None,
    reason: str | None = None,
) -> CreatorModerationEvent:
    """Create an immutable audit record for a creator state transition."""
    event = CreatorModerationEvent(
        creator_id=creator_id,
        actor_id=actor_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
    )
    db_session.add(event)
    return event


async def record_release_transition(
    db_session,
    release_id,
    listing_id,
    from_state: str,
    to_state: str,
    *,
    actor_id=None,
    reason: str | None = None,
) -> ReleaseModerationEvent:
    """Create an immutable audit record for a release state transition."""
    event = ReleaseModerationEvent(
        release_id=release_id,
        listing_id=listing_id,
        actor_id=actor_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
    )
    db_session.add(event)
    return event


async def transition_listing(
    db_session,
    listing,
    to_state: str,
    *,
    actor_id=None,
    reason: str | None = None,
):
    """Validate and apply a listing state transition, recording the audit event."""
    from_state = listing.state
    if not ListingState.can_transition(from_state, to_state):
        raise ValueError(
            f"Invalid listing transition: {from_state!r} -> {to_state!r}. "
            f"Allowed: {ListingState.transitions(from_state)}"
        )
    listing.state = to_state
    await record_listing_transition(
        db_session, listing.id, from_state, to_state,
        actor_id=actor_id, reason=reason,
    )
    return listing


async def transition_creator(
    db_session,
    user,
    to_state: str,
    *,
    actor_id=None,
    reason: str | None = None,
):
    """Validate and apply a creator state transition, recording the audit event."""
    from_state = user.creator_state
    if not CreatorState.can_transition(from_state, to_state):
        raise ValueError(
            f"Invalid creator transition: {from_state!r} -> {to_state!r}. "
            f"Allowed: {CreatorState.transitions(from_state)}"
        )
    user.creator_state = to_state
    await record_creator_transition(
        db_session, user.id, from_state, to_state,
        actor_id=actor_id, reason=reason,
    )
    return user


async def transition_release(
    db_session,
    release,
    to_state: str,
    *,
    actor_id=None,
    reason: str | None = None,
):
    """Validate and apply a release state transition, recording the audit event."""
    from_state = release.state
    if not ReleaseState.can_transition(from_state, to_state):
        raise ValueError(
            f"Invalid release transition: {from_state!r} -> {to_state!r}. "
            f"Allowed: {ReleaseState.transitions(from_state)}"
        )
    release.state = to_state
    await record_release_transition(
        db_session, release.id, release.listing_id, from_state, to_state,
        actor_id=actor_id, reason=reason,
    )
    return release