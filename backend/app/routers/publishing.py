"""Draft-first publishing router.

Replaces the old immediate-publish flow with a draft → review → publish
lifecycle.  Listing creation goes through these endpoints in the Studio
context:
  POST   /studio/listings          — create a draft
  PATCH  /studio/listings/{id}     — update a draft
  POST   /studio/listings/{id}/submit — submit for review (draft → pending_review)
  POST   /studio/listings/{id}/withdraw — withdraw from review (pending_review → draft)
  DELETE /studio/listings/{id}     — delete a draft
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.deps import get_current_user
from ..crud.listing import (
    create_listing,
    get_listing_by_slug,
    update_listing,
)
from ..db.database import get_db
from ..models.listing import Listing
from ..models.moderation import ListingState, record_listing_transition
from ..models.user import User
from ..schemas.listing import ListingCreate, ListingOut, ListingUpdate
from ..services.catalog import (
    validate_listing_create,
    validate_listing_update,
)

router = APIRouter(prefix="/studio/listings", tags=["studio"])


def _listing_err(errors) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail=[{"code": e.code, "message": e.message, "field": e.field} for e in errors],
    )


def _owns_or_404(listing: Listing, user: User) -> Listing:
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not the owner")
    return listing


def _editable_or_400(listing: Listing) -> None:
    if listing.state not in ListingState.editable_states():
        raise HTTPException(
            status_code=400,
            detail=f"Cannot edit a listing in state '{listing.state}'. "
                   f"Editable states: {sorted(ListingState.editable_states())}",
        )


# ── Create new draft ────────────────────────────────────────────────────────


@router.post("", response_model=ListingOut, status_code=201)
async def studio_create_draft(
    data: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = validate_listing_create(
        title=data.title,
        description=data.description,
        long_description=data.long_description,
        price_sol=data.price_sol,
        category_ids=data.category_ids,
        tag_ids=data.tag_ids,
    )
    if not result.is_valid:
        raise _listing_err(result.errors)

    listing = await create_listing(db, current_user.id, data, state="draft")

    # Record the initial transition from the implicit pre-state to draft
    await record_listing_transition(
        db, listing.id, "(created)", "draft",
        actor_id=current_user.id, reason="Listing created",
    )
    await db.commit()
    return listing


# ── List own listings (any state) ───────────────────────────────────────────


@router.get("", response_model=list[ListingOut])
async def studio_list_mine(
    state: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Listing)
        .options(selectinload(Listing.tags), selectinload(Listing.categories), selectinload(Listing.owner))
        .where(Listing.owner_id == current_user.id)
    )
    if state:
        q = q.where(Listing.state == state)
    q = q.order_by(Listing.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    return result.scalars().all()


# ── Get single own listing by id ────────────────────────────────────────────


@router.get("/{listing_id}", response_model=ListingOut)
async def studio_get_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Listing)
        .options(selectinload(Listing.tags), selectinload(Listing.categories), selectinload(Listing.owner))
        .where(Listing.id == listing_id)
    )
    result = await db.execute(q)
    listing = _owns_or_404(result.scalar_one_or_none(), current_user)
    return listing


# ── Update draft ────────────────────────────────────────────────────────────


@router.patch("/{listing_id}", response_model=ListingOut)
async def studio_update_draft(
    listing_id: uuid.UUID,
    data: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Listing)
        .options(selectinload(Listing.tags), selectinload(Listing.categories), selectinload(Listing.owner))
        .where(Listing.id == listing_id)
    )
    result = await db.execute(q)
    listing = _owns_or_404(result.scalar_one_or_none(), current_user)
    _editable_or_400(listing)

    # Validate only the fields present in the update
    validation = validate_listing_update(
        title=data.title,
        description=data.description,
        long_description=data.long_description,
        price_sol=data.price_sol,
        category_ids=data.category_ids,
        tag_ids=data.tag_ids,
    )
    if not validation.is_valid:
        raise _listing_err(validation.errors)

    listing = await update_listing(db, listing, data)
    await db.commit()
    return listing


# ── Submit for review ───────────────────────────────────────────────────────


@router.post("/{listing_id}/submit", response_model=ListingOut)
async def studio_submit_for_review(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Listing)
        .options(selectinload(Listing.tags), selectinload(Listing.categories), selectinload(Listing.owner))
        .where(Listing.id == listing_id)
    )
    result = await db.execute(q)
    listing = _owns_or_404(result.scalar_one_or_none(), current_user)

    if listing.state not in (ListingState.DRAFT.value, ListingState.REJECTED.value):
        raise HTTPException(
            status_code=400,
            detail="Only draft or rejected listings can be submitted for review.",
        )

    # Run final validation before submission
    validation = validate_listing_create(
        title=listing.title,
        description=listing.description,
        long_description=listing.long_description,
        price_sol=listing.price_sol,
    )
    if not validation.is_valid:
        raise _listing_err(validation.errors)

    from_state = listing.state
    listing.state = ListingState.PENDING_REVIEW.value
    await record_listing_transition(
        db, listing.id, from_state, listing.state,
        actor_id=current_user.id, reason="Creator submitted for review",
    )
    await db.flush()
    await db.refresh(listing)
    await db.commit()
    return listing


# ── Withdraw from review ───────────────────────────────────────────────────


@router.post("/{listing_id}/withdraw", response_model=ListingOut)
async def studio_withdraw(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Listing)
        .options(selectinload(Listing.tags), selectinload(Listing.categories), selectinload(Listing.owner))
        .where(Listing.id == listing_id)
    )
    result = await db.execute(q)
    listing = _owns_or_404(result.scalar_one_or_none(), current_user)

    if listing.state != ListingState.PENDING_REVIEW.value:
        raise HTTPException(status_code=400, detail="Only pending_review listings can be withdrawn.")

    from_state = listing.state
    listing.state = ListingState.DRAFT.value
    await record_listing_transition(
        db, listing.id, from_state, listing.state,
        actor_id=current_user.id, reason="Creator withdrew from review",
    )
    await db.flush()
    await db.refresh(listing)
    await db.commit()
    return listing


# ── Delete draft ────────────────────────────────────────────────────────────


@router.delete("/{listing_id}", status_code=204)
async def studio_delete_draft(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Listing).where(Listing.id == listing_id)
    result = await db.execute(q)
    listing = _owns_or_404(result.scalar_one_or_none(), current_user)

    if listing.state not in (ListingState.DRAFT.value, ListingState.REJECTED.value):
        raise HTTPException(status_code=400, detail="Only draft or rejected listings can be deleted.")

    # Record terminal transition before deletion
    await record_listing_transition(
        db, listing.id, listing.state, "(deleted)",
        actor_id=current_user.id, reason="Creator deleted listing",
    )
    await db.delete(listing)
    await db.commit()