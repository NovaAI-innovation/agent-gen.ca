from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.models.listing import ListingType


class DashboardOverviewOut(BaseModel):
    listings_count: int
    published_listings: int
    draft_listings: int
    total_installs: int
    avg_rating: Decimal | None
    reputation_score: int


class DashboardEarningsOut(BaseModel):
    confirmed_revenue_sol: Decimal
    pending_revenue_sol: Decimal
    confirmed_purchases: int
    pending_purchases: int


class DashboardInstallItemOut(BaseModel):
    listing_id: UUID
    slug: str
    title: str
    version_id: UUID
    installed_at: datetime


class DashboardInstallFeedOut(BaseModel):
    items: list[DashboardInstallItemOut]
    total: int
    page: int
    page_size: int


class DashboardSavedListingItemOut(BaseModel):
    listing_id: UUID
    slug: str
    title: str
    listing_type: ListingType
    price_sol: Decimal
    saved_at: datetime


class DashboardSavedListingsOut(BaseModel):
    items: list[DashboardSavedListingItemOut]
    total: int
    page: int
    page_size: int

