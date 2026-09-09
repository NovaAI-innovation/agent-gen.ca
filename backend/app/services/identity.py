"""Atomic nonce and session operations for the Identity bounded context.

Provides single-use nonce consumption with FOR UPDATE locking and
optimistic-locking-based session rotation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.crud.user import upsert_user
from app.models.nonce import AuthNonce
from app.models.session import AuthSession
from app.models.user import User


async def consume_nonce(
    db: AsyncSession,
    challenge_id: UUID,
    wallet: str,
    nonce: str,
) -> AuthNonce | None:
    """Atomically consume a nonce row (SELECT FOR UPDATE + mark used).

    Returns the nonce record when found and still fresh, or None when the
    nonce does not exist, is already used, or is expired.  The caller must
    decide whether to commit or roll back the enclosing transaction.
    """
    result = await db.execute(
        select(AuthNonce)
        .where(AuthNonce.id == challenge_id)
        .where(AuthNonce.wallet_address == wallet)
        .where(AuthNonce.nonce == nonce)
        .where(AuthNonce.used.is_(False))
        .where(AuthNonce.expires_at > datetime.now(timezone.utc))
        .with_for_update()
    )
    nonce_record = result.scalar_one_or_none()
    if nonce_record is not None:
        nonce_record.used = True
    return nonce_record


async def create_session(
    db: AsyncSession,
    wallet: str,
    ip_hash: str | None,
    user_agent_hash: str | None,
    *,
    max_active_sessions: int = 3,
) -> tuple[AuthSession, str, str, datetime, datetime]:
    """Create a new session, enforce the session limit, and issue fresh JWTs.

    Returns (session, refresh_token, access_token, access_exp, refresh_exp).
    The oldest active sessions beyond *max_active_sessions* are revoked.
    """
    user = await upsert_user(db, wallet)
    now = datetime.now(timezone.utc)

    # Enforce active-session limit
    result = await db.execute(
        select(AuthSession)
        .where(AuthSession.user_id == user.id)
        .where(AuthSession.status == "active")
        .where(AuthSession.revoked_at.is_(None))
        .where(AuthSession.expires_at > now)
        .order_by(AuthSession.created_at.asc())
    )
    active_sessions = list(result.scalars().all())
    excess = len(active_sessions) - max_active_sessions + 1
    if excess > 0:
        for session in active_sessions[:excess]:
            session.status = "revoked"
            session.revoked_at = now

    refresh_token, refresh_exp = create_refresh_token(
        data={"sub": wallet, "uid": str(user.id), "sid": str(UUID(int=0))}
    )
    access_token, access_exp = create_access_token(
        data={"sub": wallet, "uid": str(user.id), "sid": str(UUID(int=0))}
    )

    session = AuthSession(
        user_id=user.id,
        wallet_address=wallet,
        refresh_token_hash=hash_token(refresh_token),
        rotation_counter=0,
        status="active",
        expires_at=refresh_exp,
        last_used_at=now,
        ip_hash=ip_hash,
        user_agent_hash=user_agent_hash,
    )
    db.add(session)
    await db.flush()

    # Patch session id into the tokens now that the row has a real id
    refresh_token, _ = create_refresh_token(
        data={"sub": wallet, "uid": str(user.id), "sid": str(session.id)}
    )
    access_token, access_exp = create_access_token(
        data={"sub": wallet, "uid": str(user.id), "sid": str(session.id)}
    )
    session.refresh_token_hash = hash_token(refresh_token)

    return session, refresh_token, access_token, access_exp, refresh_exp


async def rotate_session(
    db: AsyncSession,
    session: AuthSession,
    wallet: str,
    user_id: UUID,
    expected_counter: int,
) -> tuple[str, datetime, str, datetime]:
    """Atomically rotate a session's refresh token via optimistic locking.

    Returns (new_refresh_token, new_refresh_exp, new_access_token, new_access_exp).
    Raises 409 Conflict when the rotation_counter has changed (concurrent
    update detected).
    """
    now = datetime.now(timezone.utc)

    new_refresh_token, new_refresh_exp = create_refresh_token(
        data={"sub": wallet, "uid": str(user_id), "sid": str(session.id)}
    )
    new_access_token, new_access_exp = create_access_token(
        data={"sub": wallet, "uid": str(user_id), "sid": str(session.id)}
    )

    new_hash = hash_token(new_refresh_token)
    new_counter = expected_counter + 1

    result = await db.execute(
        update(AuthSession)
        .where(AuthSession.id == session.id)
        .where(AuthSession.rotation_counter == expected_counter)
        .where(AuthSession.status == "active")
        .where(AuthSession.user_id == user_id)
        .where(AuthSession.wallet_address == wallet)
        .values(
            refresh_token_hash=new_hash,
            rotation_counter=new_counter,
            expires_at=new_refresh_exp,
            last_used_at=now,
        )
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session was rotated by another request; please re-authenticate",
        )

    await db.refresh(session)
    return new_refresh_token, new_refresh_exp, new_access_token, new_access_exp


async def revoke_session(session: AuthSession) -> None:
    """Mark a session as revoked in-memory.  The caller must commit."""
    session.status = "revoked"
    session.revoked_at = datetime.now(timezone.utc)