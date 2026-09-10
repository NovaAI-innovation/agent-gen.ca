"""Approved-creator onboarding and authorization for the Identity context.

A user submits a creator profile (handle, display name, bio, support link,
terms acceptance, payout address). An admin approves or rejects it. Only
approved creators may create listing drafts.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import CreatorProfileIn

CREATOR_STATUSES = {"none", "pending", "approved", "rejected"}


def require_approved_creator(user: User) -> User:
    """Raise 403 unless the user is an approved creator."""
    if user.creator_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only approved creators can create listings. "
                "Submit a creator profile and wait for approval "
                "at /studio/onboarding."
            ),
        )
    return user


async def get_creator_profile(user: User) -> User:
    """Return the user's current creator profile (for display)."""
    return user


async def submit_creator_profile(
    db: AsyncSession,
    user: User,
    data: CreatorProfileIn,
) -> User:
    """Submit or update a creator profile application.

    Sets creator_status to 'pending' (or keeps 'approved' so an approved
    creator can edit profile details without re-entering the queue).
    """
    now = datetime.now(timezone.utc)

    # Handle uniqueness is enforced by the DB unique constraint; check here
    # to return a friendly error when the handle collides with another user.
    if data.handle != user.handle and data.handle:
        result = await db.execute(select(User).where(User.handle == data.handle))
        other = result.scalar_one_or_none()
        if other is not None and other.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That handle is already taken",
            )

    user.handle = data.handle
    user.display_name = data.display_name
    user.bio = data.bio
    user.support_link = data.support_link
    user.payout_address = data.payout_address

    if data.terms_accepted:
        user.terms_accepted_at = now

    if user.creator_status not in ("approved", "pending"):
        user.creator_status = "pending"
        user.creator_status_at = now
        user.reviewer_notes = None

    await db.flush()
    await db.refresh(user)
    return user


async def review_creator(
    db: AsyncSession,
    user: User,
    *,
    approve: bool,
    notes: str | None = None,
) -> User:
    """Approve or reject a creator application (admin action).

    Used by moderation tooling; there is no public self-serve approval.
    """
    now = datetime.now(timezone.utc)
    user.creator_status = "approved" if approve else "rejected"
    user.creator_status_at = now
    user.reviewer_notes = notes
    await db.flush()
    await db.refresh(user)
    return user