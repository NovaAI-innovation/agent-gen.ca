from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.user import User
from ..schemas.user import UserUpdate


async def get_user_by_wallet(db: AsyncSession, wallet_address: str) -> User | None:
    result = await db.execute(select(User).where(User.wallet_address == wallet_address))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def upsert_user(db: AsyncSession, wallet_address: str) -> User:
    user = await get_user_by_wallet(db, wallet_address)
    if not user:
        user = User(wallet_address=wallet_address)
        db.add(user)
        await db.flush()
        await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user
