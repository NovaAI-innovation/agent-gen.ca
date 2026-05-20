import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import AuthContext, get_current_user, get_optional_auth_context
from ..crud.user import get_user_by_wallet, update_user
from ..crud.listing import get_listings_by_owner
from ..db.database import get_db
from ..models.user import User
from ..schemas.user import UserPublic, UserUpdate
from ..schemas.listing import ListingOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_user(db, current_user, data)


@router.get("/{wallet}", response_model=UserPublic)
async def get_user_profile(wallet: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_wallet(db, wallet)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{wallet}/listings", response_model=list[ListingOut])
async def get_user_listings(
    wallet: str,
    include_drafts: bool = Query(False),
    auth: AuthContext | None = Depends(get_optional_auth_context),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_wallet(db, wallet)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    include_unpublished = bool(
        include_drafts and auth is not None and auth.user.id == user.id
    )
    return await get_listings_by_owner(
        db,
        owner_id=user.id,
        include_unpublished=include_unpublished,
    )


@router.post("/{wallet}/follow", status_code=204)
async def follow_user(
    wallet: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target = await get_user_by_wallet(db, wallet)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    await db.execute(
        sqlalchemy.text(
            "INSERT INTO user_follows (follower_id, following_id) VALUES (:f, :t) ON CONFLICT DO NOTHING"
        ),
        {"f": str(current_user.id), "t": str(target.id)},
    )
    await db.commit()


@router.delete("/{wallet}/follow", status_code=204)
async def unfollow_user(
    wallet: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target = await get_user_by_wallet(db, wallet)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    await db.execute(
        sqlalchemy.text(
            "DELETE FROM user_follows WHERE follower_id = :f AND following_id = :t"
        ),
        {"f": str(current_user.id), "t": str(target.id)},
    )
    await db.commit()
