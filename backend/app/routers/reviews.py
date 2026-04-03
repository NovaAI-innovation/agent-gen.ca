from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.deps import get_current_user
from ..crud.listing import get_listing_by_slug
from ..db.database import get_db
from ..models.review import Review
from ..models.user import User
from ..schemas.review import ReviewOut, ReviewCreate

router = APIRouter(tags=["reviews"])


@router.get("/listings/{slug}/reviews", response_model=list[ReviewOut])
async def list_reviews(slug: str, db: AsyncSession = Depends(get_db)):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    result = await db.execute(
        select(Review).where(Review.listing_id == listing.id).order_by(Review.created_at.desc())
    )
    return result.scalars().all()


@router.post("/listings/{slug}/reviews", response_model=ReviewOut, status_code=201)
async def create_review(
    slug: str,
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_listing_by_slug(db, slug)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    existing = await db.execute(
        select(Review)
        .where(Review.listing_id == listing.id)
        .where(Review.reviewer_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="You have already reviewed this listing")

    review = Review(
        listing_id=listing.id,
        reviewer_id=current_user.id,
        rating=data.rating,
        title=data.title,
        body=data.body,
    )
    db.add(review)
    await db.flush()

    # Update listing avg_rating
    from sqlalchemy import func
    avg = await db.execute(
        select(func.avg(Review.rating)).where(Review.listing_id == listing.id)
    )
    listing.avg_rating = avg.scalar_one()
    await db.commit()
    await db.refresh(review)
    return review


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your review")
    await db.delete(review)
    await db.commit()


@router.post("/reviews/{review_id}/helpful", status_code=204)
async def mark_helpful(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    import sqlalchemy
    await db.execute(
        sqlalchemy.text(
            "INSERT INTO review_helpful (review_id, user_id) VALUES (:r, :u) ON CONFLICT DO NOTHING"
        ),
        {"r": str(review_id), "u": str(current_user.id)},
    )
    # Update count
    from sqlalchemy import func
    count = await db.execute(
        sqlalchemy.text("SELECT COUNT(*) FROM review_helpful WHERE review_id = :r"),
        {"r": str(review_id)},
    )
    review.helpful_count = count.scalar_one()
    await db.commit()
