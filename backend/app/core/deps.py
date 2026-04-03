from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.security import decode_access_token
from ..crud.user import get_user_by_id
from ..db.database import get_db
from ..models.session import AuthSession
from ..models.user import User

bearer = HTTPBearer()


@dataclass
class AuthContext:
    user: User
    session: AuthSession
    payload: dict


async def get_current_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    try:
        payload = decode_access_token(credentials.credentials)
        token_type: str | None = payload.get("typ")
        wallet: str = payload.get("sub")
        user_id_raw: str | None = payload.get("uid")
        session_id_raw: str | None = payload.get("sid")
        if token_type != "access" or not wallet or not user_id_raw or not session_id_raw:
            raise ValueError("no sub")
        user_id = UUID(user_id_raw)
        session_id = UUID(session_id_raw)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(AuthSession).where(AuthSession.id == session_id))
    session = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if (
        not session
        or session.user_id != user_id
        or session.wallet_address != wallet
        or session.status != "active"
        or session.revoked_at is not None
        or session.expires_at <= now
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user = await get_user_by_id(db, user_id)
    if not user or user.wallet_address != wallet:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return AuthContext(user=user, session=session, payload=payload)


async def get_current_user(context: AuthContext = Depends(get_current_auth_context)) -> User:
    return context.user
