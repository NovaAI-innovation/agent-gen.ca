from fastapi import APIRouter, Depends, Query
import sqlalchemy
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_current_user
from ..db.database import get_db
from ..models.listing import Listing
from ..models.purchase import Purchase, PurchaseStatus
from ..models.user import User
from ..schemas.dashboard import (
    DashboardEarningsOut,
    DashboardInstallFeedOut,
    DashboardInstallItemOut,
    DashboardOverviewOut,
    DashboardSavedListingItemOut,
    DashboardSavedListingsOut,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewOut)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            func.count(Listing.id).label("listings_count"),
            func.coalesce(
                func.sum(case((Listing.is_published == True, 1), else_=0)),
                0,
            ).label("published_listings"),
            func.coalesce(
                func.sum(case((Listing.is_published == False, 1), else_=0)),
                0,
            ).label("draft_listings"),
            func.coalesce(func.sum(Listing.download_count), 0).label("total_installs"),
            func.avg(Listing.avg_rating).label("avg_rating"),
        ).where(Listing.owner_id == current_user.id)
    )
    metrics = result.one()

    return DashboardOverviewOut(
        listings_count=metrics.listings_count or 0,
        published_listings=metrics.published_listings or 0,
        draft_listings=metrics.draft_listings or 0,
        total_installs=metrics.total_installs or 0,
        avg_rating=metrics.avg_rating,
        reputation_score=current_user.reputation_score,
    )


@router.get("/earnings", response_model=DashboardEarningsOut)
async def get_dashboard_earnings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    confirmed_result = await db.execute(
        select(
            func.coalesce(func.sum(Purchase.price_sol), 0).label("confirmed_revenue_sol"),
            func.count(Purchase.id).label("confirmed_purchases"),
        ).where(
            Purchase.seller_id == current_user.id,
            Purchase.status == PurchaseStatus.confirmed,
        )
    )
    pending_result = await db.execute(
        select(
            func.coalesce(func.sum(Purchase.price_sol), 0).label("pending_revenue_sol"),
            func.count(Purchase.id).label("pending_purchases"),
        ).where(
            Purchase.seller_id == current_user.id,
            Purchase.status == PurchaseStatus.pending,
        )
    )
    confirmed = confirmed_result.one()
    pending = pending_result.one()

    return DashboardEarningsOut(
        confirmed_revenue_sol=confirmed.confirmed_revenue_sol,
        pending_revenue_sol=pending.pending_revenue_sol,
        confirmed_purchases=confirmed.confirmed_purchases,
        pending_purchases=pending.pending_purchases,
    )


@router.get("/installs", response_model=DashboardInstallFeedOut)
async def get_dashboard_installs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(
        sqlalchemy.text(
            """
            SELECT COUNT(*)
            FROM install_history ih
            JOIN listings l ON l.id = ih.listing_id
            WHERE l.owner_id = :owner_id
            """
        ),
        {"owner_id": str(current_user.id)},
    )
    total = total_result.scalar_one()

    result = await db.execute(
        sqlalchemy.text(
            """
            SELECT
              ih.listing_id,
              l.slug,
              l.title,
              ih.version_id,
              ih.installed_at
            FROM install_history ih
            JOIN listings l ON l.id = ih.listing_id
            WHERE l.owner_id = :owner_id
            ORDER BY ih.installed_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        {
            "owner_id": str(current_user.id),
            "limit": page_size,
            "offset": (page - 1) * page_size,
        },
    )

    items = [
        DashboardInstallItemOut(
            listing_id=row.listing_id,
            slug=row.slug,
            title=row.title,
            version_id=row.version_id,
            installed_at=row.installed_at,
        )
        for row in result
    ]

    return DashboardInstallFeedOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/saves", response_model=DashboardSavedListingsOut)
async def get_dashboard_saves(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(
        sqlalchemy.text(
            """
            SELECT COUNT(*)
            FROM user_saves
            WHERE user_id = :user_id
            """
        ),
        {"user_id": str(current_user.id)},
    )
    total = total_result.scalar_one()

    result = await db.execute(
        sqlalchemy.text(
            """
            SELECT
              us.listing_id,
              l.slug,
              l.title,
              l.type AS listing_type,
              l.price_sol,
              us.created_at AS saved_at
            FROM user_saves us
            JOIN listings l ON l.id = us.listing_id
            WHERE us.user_id = :user_id
            ORDER BY us.created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        {
            "user_id": str(current_user.id),
            "limit": page_size,
            "offset": (page - 1) * page_size,
        },
    )

    items = [
        DashboardSavedListingItemOut(
            listing_id=row.listing_id,
            slug=row.slug,
            title=row.title,
            listing_type=row.listing_type,
            price_sol=row.price_sol,
            saved_at=row.saved_at,
        )
        for row in result
    ]

    return DashboardSavedListingsOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
