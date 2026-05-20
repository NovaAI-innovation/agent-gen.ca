from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.listing import ListingType


class ListingVersionOut(BaseModel):
    id: UUID
    version: str
    changelog: Optional[str]
    config_json: Optional[Any]
    install_instructions: Optional[str]
    is_latest: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ListingInstallOut(BaseModel):
    listing_id: UUID
    slug: str
    version_id: UUID
    download_count: int
    installed_at: datetime


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str]

    model_config = {"from_attributes": True}


class ListingOut(BaseModel):
    id: UUID
    type: ListingType
    title: str
    slug: str
    description: Optional[str]
    long_description: Optional[str]
    owner_id: UUID
    is_published: bool
    is_featured: bool
    price_sol: Decimal
    download_count: int
    view_count: int
    avg_rating: Optional[Decimal]
    tags: List[TagOut] = []
    categories: List[CategoryOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ListingCreate(BaseModel):
    type: ListingType
    title: str
    description: Optional[str] = None
    long_description: Optional[str] = None
    price_sol: Decimal = Decimal("0")
    tag_ids: List[int] = []
    category_ids: List[int] = []


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    price_sol: Optional[Decimal] = None
    is_published: Optional[bool] = None
    tag_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None


class ListingVersionCreate(BaseModel):
    version: str
    changelog: Optional[str] = None
    config_json: Optional[Any] = None
    install_instructions: Optional[str] = None
