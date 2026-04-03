from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..db.database import get_db
from ..models.listing import Listing
from ..models.category import Category
from ..schemas.listing import ListingOut, CategoryOut

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/featured", response_model=list[ListingOut])
async def get_featured(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Listing)
        .options(selectinload(Listing.tags), selectinload(Listing.categories))
        .where(Listing.is_featured == True, Listing.is_published == True)
        .order_by(Listing.download_count.desc())
        .limit(12)
    )
    return result.scalars().all()


@router.get("/trending", response_model=list[ListingOut])
async def get_trending(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Listing)
        .options(selectinload(Listing.tags), selectinload(Listing.categories))
        .where(Listing.is_published == True)
        .order_by(Listing.download_count.desc(), Listing.avg_rating.desc().nulls_last())
        .limit(20)
    )
    return result.scalars().all()


@router.get("/categories", response_model=list[CategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.get("/search", response_model=list[ListingOut])
async def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    from ..crud.listing import get_listings
    items, _ = await get_listings(db, q=q, page=page, page_size=page_size)
    return items
