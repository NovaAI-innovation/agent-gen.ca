from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException, status
from ..models.user import User

async def get_user_by_wallet(db: AsyncSession, wallet_address: str) -> User:
    result = await db.execute(select(User).where(User.wallet_address == wallet_address))
    return result.scalar_one_or_none()

async def create_update_user(db: AsyncSession, wallet_address: str) -> User:
    user = await get_user_by_wallet(db, wallet_address)
    if not user:
        user = User(wallet_address=wallet_address)
        db.add(user)
        await db.flush()
    return user
