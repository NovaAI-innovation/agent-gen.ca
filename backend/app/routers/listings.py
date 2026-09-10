from datetime import datetime, timezone
from typing import Optional

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.deps import AuthContext, get_current_user, get_optional_auth_context
from ..core.security import hash_request_value
from ..crud.listing import (
    get_listings, get_listing_by_slug, create_listing,
    update_listing, create_listing_version, get_listing_versions,
)
from ..db.database import get_db
from ..models.listing import ListingType, ListingVersion, Listing
from ..models.user import User
from ..schemas.listing import (
    ListingOut, ListingCreate, ListingUpdate,
    ListingVersionOut, ListingVersionCreate, ListingInstallOut,
)
from ..services.catalog import (
    validate_listing_create,
    validate_listing_update,
    validate_release_create,
)

router = APIRouter(prefix="/listings", tags=["listings"])


def _client_ip_hash(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    client_ip = (
        forwarded_for.split(",")[0].strip()
        if forwarded_for
        else (request.client.host if request.client else None)
    )
    return hash_request_value(client_ip)


def _validation_error(errors) -> HTTPException:
    """Convert a tuple of ValidationError into a stable HTTP 422."""
    return HTTPException(
        status_code=422,
        detail=[{"code": e.code, "message": e.message, "field": e.field} for e in errors],
    )


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
    result = validate_listing_create(
        title=data.title,
        description=data.description,
        long_description=data.long_description,
        price_sol=data.price_sol,
        category_ids=data.category_ids,
        tag_ids=data.tag_ids,
    )
    if not result.is_valid:
        raise _validation_error(result.errors)
    listing = await create_listing(db, current_user.id, data, state="draft")
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
    result = validate_listing_update(
        title=data.title,
        description=data.description,
        long_description=data.long_description,
        price_sol=data.price_sol,
        category_ids=data.category_ids,
        tag_ids=data.tag_ids,
    )
    if not result.is_valid:
        raise _validation_error(result.errors)
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
    result = validate_release_create(
        version=data.version,
        changelog=data.changelog,
        config_json=data.config_json,
        install_instructions=data.install_instructions,
    )
    if not result.is_valid:
        raise _validation_error(result.errors)
    version = await create_listing_version(db, listing, data)
    await db.commit()
    return version


@router.post("/{slug}/install", response_model=ListingInstallOut, status_code=201)
async def install_listing(
    slug: str,
    request: Request,
    auth: AuthContext | None = Depends(get_optional_auth_context),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing or listing.state != "published":
        raise HTTPException(status_code=404, detail="Listing not found")

    version_result = await db.execute(
        select(ListingVersion).where(
            ListingVersion.listing_id == listing.id,
            ListingVersion.is_latest == True,
        )
    )
    latest_version = version_result.scalar_one_or_none()
    if latest_version is None:
        raise HTTPException(
            status_code=409,
            detail="No installable listing version available",
        )

    installed_at = datetime.now(timezone.utc)
    ip_hash = _client_ip_hash(request)
    user_id = str(auth.user.id) if auth is not None else None

    await db.execute(
        sqlalchemy.text(
            """
            INSERT INTO downloads (listing_id, version_id, user_id, ip_hash, created_at)
            VALUES (:listing_id, :version_id, :user_id, :ip_hash, :created_at)
            """
        ),
        {
            "listing_id": str(listing.id),
            "version_id": str(latest_version.id),
            "user_id": user_id,
            "ip_hash": ip_hash,
            "created_at": installed_at,
        },
    )

    if auth is not None:
        await db.execute(
            sqlalchemy.text(
                """
                INSERT INTO install_history (user_id, listing_id, version_id, installed_at)
                VALUES (:user_id, :listing_id, :version_id, :installed_at)
                """
            ),
            {
                "user_id": str(auth.user.id),
                "listing_id": str(listing.id),
                "version_id": str(latest_version.id),
                "installed_at": installed_at,
            },
        )

    await db.execute(
        update(Listing)
        .where(Listing.id == listing.id)
        .values(download_count=Listing.download_count + 1)
    )
    await db.commit()
    await db.refresh(listing)

    return ListingInstallOut(
        listing_id=listing.id,
        slug=listing.slug,
        version_id=latest_version.id,
        download_count=listing.download_count,
        installed_at=installed_at,
    )


@router.post("/{slug}/save", status_code=204)
async def save_listing(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
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
    await db.execute(
        sqlalchemy.text("DELETE FROM user_saves WHERE user_id = :u AND listing_id = :l"),
        {"u": str(current_user.id), "l": str(listing.id)},
    )
    await db.commit()