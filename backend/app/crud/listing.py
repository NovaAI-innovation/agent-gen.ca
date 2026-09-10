import re
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_, update
from ..models.listing import Listing, ListingVersion, ListingType
from ..models.category import Category, Tag
from ..schemas.listing import ListingCreate, ListingUpdate, ListingVersionCreate


def _slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = base
    counter = 1
    while True:
        result = await db.execute(select(Listing).where(Listing.slug == slug))
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base}-{counter}"
        counter += 1


def _listing_query():
    return select(Listing).options(
        selectinload(Listing.tags),
        selectinload(Listing.categories),
        selectinload(Listing.owner),
    )


async def get_listings(
    db: AsyncSession,
    *,
    listing_type: Optional[ListingType] = None,
    category_slug: Optional[str] = None,
    tag_name: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = "created_at",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Listing], int]:
    # v2: only published listings appear in public queries
    query = _listing_query().where(Listing.state == "published")

    if listing_type:
        query = query.where(Listing.type == listing_type)
    if category_slug:
        query = query.join(Listing.categories).where(Category.slug == category_slug)
    if tag_name:
        query = query.join(Listing.tags).where(func.lower(Tag.name) == tag_name.lower())
    if q:
        query = query.where(
            or_(
                Listing.title.op("%%")(q),
                Listing.description.op("%%")(q),
            )
        )

    sort_col = {
        "created_at": Listing.created_at.desc(),
        "downloads": Listing.download_count.desc(),
        "rating": Listing.avg_rating.desc().nulls_last(),
        "price_asc": Listing.price_sol.asc(),
        "price_desc": Listing.price_sol.desc(),
    }.get(sort, Listing.created_at.desc())

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(sort_col).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_listing_by_slug(db: AsyncSession, slug: str) -> Optional[Listing]:
    result = await db.execute(
        _listing_query().where(Listing.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_listings_by_owner(
    db: AsyncSession,
    *,
    owner_id: UUID,
    include_drafts: bool = False,
) -> list[Listing]:
    query = _listing_query().where(Listing.owner_id == owner_id)
    if not include_drafts:
        query = query.where(Listing.state == "published")

    result = await db.execute(query.order_by(Listing.created_at.desc()))
    return result.scalars().all()


async def create_listing(
    db: AsyncSession,
    owner_id: UUID,
    data: ListingCreate,
    *,
    state: str = "draft",
) -> Listing:
    slug = await _unique_slug(db, _slugify(data.title))
    listing = Listing(
        type=data.type,
        title=data.title,
        slug=slug,
        description=data.description,
        long_description=data.long_description,
        price_sol=data.price_sol,
        owner_id=owner_id,
        state=state,
    )
    if data.tag_ids:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))).scalars().all()
        listing.tags = tags
    if data.category_ids:
        cats = (await db.execute(select(Category).where(Category.id.in_(data.category_ids)))).scalars().all()
        listing.categories = cats
    db.add(listing)
    await db.flush()
    await db.refresh(listing)
    return listing


async def update_listing(db: AsyncSession, listing: Listing, data: ListingUpdate) -> Listing:
    for field, value in data.model_dump(exclude_unset=True, exclude={"tag_ids", "category_ids"}).items():
        setattr(listing, field, value)
    if data.tag_ids is not None:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))).scalars().all()
        listing.tags = tags
    if data.category_ids is not None:
        cats = (await db.execute(select(Category).where(Category.id.in_(data.category_ids)))).scalars().all()
        listing.categories = cats
    await db.flush()
    await db.refresh(listing)
    return listing


async def create_listing_version(db: AsyncSession, listing: Listing, data: ListingVersionCreate) -> ListingVersion:
    # Mark all previous versions as not latest
    await db.execute(
        update(ListingVersion)
        .where(ListingVersion.listing_id == listing.id)
        .values(is_latest=False)
    )
    version = ListingVersion(
        listing_id=listing.id,
        version=data.version,
        changelog=data.changelog,
        config_json=data.config_json,
        install_instructions=data.install_instructions,
        is_latest=True,
        state="draft",
    )
    db.add(version)
    await db.flush()
    await db.refresh(version)
    return version


async def get_listing_versions(db: AsyncSession, listing_id: UUID) -> list[ListingVersion]:
    result = await db.execute(
        select(ListingVersion)
        .where(ListingVersion.listing_id == listing_id)
        .order_by(ListingVersion.created_at.desc())
    )
    return result.scalars().all()
