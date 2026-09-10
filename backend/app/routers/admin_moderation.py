"""Admin moderation router.

Moderators can approve, reject, suspend, or restore creators and listings/
releases. Every action produces an immutable audit event through the
moderation state machine.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.deps import get_current_user
from ..db.database import get_db
from ..models.listing import Listing
from ..models.user import User
from ..models.moderation import (
    ListingState,
    ListingModerationEvent,
    CreatorState,
    CreatorModerationEvent,
    transition_listing,
    transition_creator,
)

router = APIRouter(prefix="/admin/moderation", tags=["moderation"])


def _require_moderator(user: User) -> None:
    """Gate admin endpoints behind verified status (standing in for a
    dedicated moderator role until RBAC is implemented)."""
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Moderator access required.")


# ── Queue: pending_review listings ───────────────────────────────────────────


@router.get("/queue", response_model=dict)
async def moderation_queue(
    scope: str = Query("listings", enum=["listings", "creators"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)

    if scope == "listings":
        q = (
            select(Listing)
            .options(selectinload(Listing.owner))
            .where(Listing.state == ListingState.PENDING_REVIEW.value)
            .order_by(Listing.created_at)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(q)
        items = [
            {
                "id": str(l.id),
                "title": l.title,
                "slug": l.slug,
                "type": l.type,
                "state": l.state,
                "owner_wallet": l.owner.wallet_address if l.owner else None,
                "created_at": l.created_at.isoformat(),
            }
            for l in result.scalars().all()
        ]
        count_q = select(func.count(Listing.id)).where(Listing.state == ListingState.PENDING_REVIEW.value)
        total = (await db.execute(count_q)).scalar_one()
        return {"items": items, "total": total, "page": page, "page_size": page_size}
    else:
        q = (
            select(User)
            .where(User.creator_state == CreatorState.PENDING_APPROVAL.value)
            .order_by(User.created_at)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(q)
        items = [
            {
                "id": str(u.id),
                "wallet_address": u.wallet_address,
                "username": u.username,
                "creator_state": u.creator_state,
                "created_at": u.created_at.isoformat(),
            }
            for u in result.scalars().all()
        ]
        count_q = select(func.count(User.id)).where(User.creator_state == CreatorState.PENDING_APPROVAL.value)
        total = (await db.execute(count_q)).scalar_one()
        return {"items": items, "total": total, "page": page, "page_size": page_size}


# ── Approve listing ─────────────────────────────────────────────────────────


@router.post("/listings/{listing_id}/approve", response_model=dict)
async def approve_listing(
    listing_id: uuid.UUID,
    reason: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = select(Listing).options(selectinload(Listing.owner)).where(Listing.id == listing_id)
    listing = (await db.execute(q)).scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.state not in (ListingState.PENDING_REVIEW.value,):
        raise HTTPException(status_code=400, detail=f"Cannot approve a listing in state '{listing.state}'.")

    await transition_listing(db, listing, ListingState.APPROVED.value,
                             actor_id=current_user.id, reason=reason or "Approved by moderator")
    await db.flush()
    await db.commit()
    return {"ok": True, "state": listing.state}


# ── Reject listing ───────────────────────────────────────────────────────────


@router.post("/listings/{listing_id}/reject", response_model=dict)
async def reject_listing(
    listing_id: uuid.UUID,
    reason: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = select(Listing).options(selectinload(Listing.owner)).where(Listing.id == listing_id)
    listing = (await db.execute(q)).scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.state != ListingState.PENDING_REVIEW.value:
        raise HTTPException(status_code=400, detail=f"Cannot reject a listing in state '{listing.state}'.")

    await transition_listing(db, listing, ListingState.REJECTED.value,
                             actor_id=current_user.id, reason=reason or "Rejected by moderator")
    await db.flush()
    await db.commit()
    return {"ok": True, "state": listing.state}


# ── Publish listing (approve → published) — called after moderation approval ─


@router.post("/listings/{listing_id}/publish", response_model=dict)
async def publish_listing_admin(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = select(Listing).options(selectinload(Listing.owner)).where(Listing.id == listing_id)
    listing = (await db.execute(q)).scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.state != ListingState.APPROVED.value:
        raise HTTPException(status_code=400, detail=f"Cannot publish a listing in state '{listing.state}'.")

    await transition_listing(db, listing, ListingState.PUBLISHED.value,
                             actor_id=current_user.id, reason="Published by moderator")
    await db.flush()
    await db.commit()
    return {"ok": True, "state": listing.state}


# ── Suspend listing ──────────────────────────────────────────────────────────


@router.post("/listings/{listing_id}/suspend", response_model=dict)
async def suspend_listing(
    listing_id: uuid.UUID,
    reason: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = select(Listing).options(selectinload(Listing.owner)).where(Listing.id == listing_id)
    listing = (await db.execute(q)).scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.state != ListingState.PUBLISHED.value:
        raise HTTPException(status_code=400, detail=f"Cannot suspend a listing in state '{listing.state}'.")

    await transition_listing(db, listing, ListingState.SUSPENDED.value,
                             actor_id=current_user.id, reason=reason or "Suspended by moderator")
    await db.flush()
    await db.commit()
    return {"ok": True, "state": listing.state}


# ── Restore listing (suspended → draft) ─────────────────────────────────────


@router.post("/listings/{listing_id}/restore", response_model=dict)
async def restore_listing(
    listing_id: uuid.UUID,
    reason: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = select(Listing).options(selectinload(Listing.owner)).where(Listing.id == listing_id)
    listing = (await db.execute(q)).scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.state != ListingState.SUSPENDED.value:
        raise HTTPException(status_code=400, detail=f"Cannot restore a listing in state '{listing.state}'.")

    await transition_listing(db, listing, ListingState.DRAFT.value,
                             actor_id=current_user.id, reason=reason or "Restored by moderator")
    await db.flush()
    await db.commit()
    return {"ok": True, "state": listing.state}


# ── Approve creator ─────────────────────────────────────────────────────────


@router.post("/creators/{creator_id}/approve", response_model=dict)
async def approve_creator(
    creator_id: uuid.UUID,
    reason: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = select(User).where(User.id == creator_id)
    creator = (await db.execute(q)).scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="User not found")

    if creator.creator_state != CreatorState.PENDING_APPROVAL.value:
        raise HTTPException(status_code=400, detail=f"Cannot approve a creator in state '{creator.creator_state}'.")

    await transition_creator(db, creator, CreatorState.APPROVED.value,
                             actor_id=current_user.id, reason=reason or "Creator approved by moderator")
    await db.flush()
    await db.commit()
    return {"ok": True, "creator_state": creator.creator_state}


# ── Suspend creator ──────────────────────────────────────────────────────────


@router.post("/creators/{creator_id}/suspend", response_model=dict)
async def suspend_creator(
    creator_id: uuid.UUID,
    reason: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = select(User).where(User.id == creator_id)
    creator = (await db.execute(q)).scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="User not found")

    if creator.creator_state != CreatorState.APPROVED.value:
        raise HTTPException(status_code=400, detail=f"Cannot suspend a creator in state '{creator.creator_state}'.")

    await transition_creator(db, creator, CreatorState.SUSPENDED.value,
                             actor_id=current_user.id, reason=reason or "Creator suspended by moderator")
    await db.flush()
    await db.commit()
    return {"ok": True, "creator_state": creator.creator_state}


# ── Audit log for a listing ─────────────────────────────────────────────────


@router.get("/listings/{listing_id}/audit", response_model=list[dict])
async def listing_audit(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_moderator(current_user)
    q = (
        select(ListingModerationEvent)
        .where(ListingModerationEvent.listing_id == listing_id)
        .order_by(ListingModerationEvent.created_at.desc())
    )
    result = await db.execute(q)
    return [
        {
            "id": str(e.id),
            "from_state": e.from_state,
            "to_state": e.to_state,
            "reason": e.reason,
            "actor_id": str(e.actor_id) if e.actor_id else None,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars().all()
    ]