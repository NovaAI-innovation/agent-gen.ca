from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_current_user
from ..crud.listing import (
    get_listings, get_listing_by_slug, create_listing,
    update_listing, create_listing_version, get_listing_versions,
)
from ..db.database import get_db
from ..models.listing import ListingType
from ..models.user import User
from ..schemas.listing import (
    ListingOut, ListingCreate, ListingUpdate,
    ListingVersionOut, ListingVersionCreate,
)

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=dict)
async def list_listings(
    type: Optional[ListingType] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = Query("created_at", enum=["created_at", "downloads", "rating", "price_asc", "price_desc"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_listings(
        db, listing_type=type, category_slug=category,
        tag_name=tag, q=q, sort=sort, page=page, page_size=page_size,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=ListingOut, status_code=201)
async def create(
    data: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await create_listing(db, current_user.id, data)
    await db.commit()
    return listing


@router.get("/{slug}", response_model=ListingOut)
async def get_listing(slug: str, db: AsyncSession = Depends(get_db)):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.patch("/{slug}", response_model=ListingOut)
async def update(
    slug: str,
    data: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the owner")
    listing = await update_listing(db, listing, data)
    await db.commit()
    return listing


@router.delete("/{slug}", status_code=204)
async def delete(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the owner")
    await db.delete(listing)
    await db.commit()


@router.get("/{slug}/versions", response_model=list[ListingVersionOut])
async def list_versions(slug: str, db: AsyncSession = Depends(get_db)):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return await get_listing_versions(db, listing.id)


@router.post("/{slug}/versions", response_model=ListingVersionOut, status_code=201)
async def publish_version(
    slug: str,
    data: ListingVersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the owner")
    version = await create_listing_version(db, listing, data)
    await db.commit()
    return version


@router.post("/{slug}/save", status_code=204)
async def save_listing(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    import sqlalchemy
    await db.execute(
        sqlalchemy.text(
            "INSERT INTO user_saves (user_id, listing_id) VALUES (:u, :l) ON CONFLICT DO NOTHING"
        ),
        {"u": str(current_user.id), "l": str(listing.id)},
    )
    await db.commit()


@router.delete("/{slug}/save", status_code=204)
async def unsave_listing(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    import sqlalchemy
    await db.execute(
        sqlalchemy.text("DELETE FROM user_saves WHERE user_id = :u AND listing_id = :l"),
        {"u": str(current_user.id), "l": str(listing.id)},
    )
    await db.commit()
