"""Atomic nonce and session operations for the Identity bounded context.

Provides single-use nonce consumption with FOR UPDATE locking,
optimistic-locking-based session rotation, and SIWS signature verification.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from uuid import UUID

import base58
import nacl.exceptions
import nacl.signing
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
from app.schemas.identity import _iso_z, build_siws_message


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


# ── SIWS signature verification ──────────────────────────────────────────────


async def verify_siws_signature(
    wallet: str,
    challenge_id: UUID,
    nonce: str,
    signature: str,
    domain: str,
    uri: str,
    chain_id: str,
    issued_at: datetime,
    ip_hash: str | None,
    user_agent_hash: str | None,
    *,
    db: AsyncSession,
    statement: str | None = None,
) -> tuple[AuthSession, str, str, datetime, datetime]:
    """Verify a SIWS (Sign-In With Solana) signature with independent field checks.

    Steps:
    1. Atomically consume the nonce (SELECT FOR UPDATE + mark used).
    2. Reconstruct the SIWS message from the submitted fields.
    3. Verify each field independently matches the nonce record.
    4. Verify the ed25519 signature against the reconstructed message.
    5. Create a session and issue JWTs.

    Raises HTTPException on any mismatch with a descriptive detail message.
    Returns (session, refresh_token, access_token, access_exp, refresh_exp).
    """
    # 1. Consume nonce atomically
    nonce_record = await consume_nonce(db, challenge_id, wallet, nonce)
    if nonce_record is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired challenge",
        )

    # 2. Verify the reconstructed message matches the stored one
    expected_message = build_siws_message(
        domain=domain,
        address=wallet,
        statement=statement or "Sign in to agent-gen.ca",
        uri=uri,
        chain_id=chain_id,
        nonce=nonce,
        issued_at=issued_at,
        expires_at=nonce_record.expires_at,
    )

    if expected_message != nonce_record.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SIWS message mismatch: submitted fields do not match the challenge",
        )

    # 3. Verify each field independently against the nonce record
    errors: list[str] = []
    if domain != nonce_record.domain:
        errors.append("domain")
    if uri != nonce_record.uri:
        errors.append("uri")
    if chain_id != nonce_record.chain_id:
        errors.append("chain_id")
    if nonce != nonce_record.nonce:
        errors.append("nonce")
    if _iso_z(issued_at) != _iso_z(nonce_record.issued_at):
        errors.append("issued_at")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SIWS field mismatch: {', '.join(errors)}",
        )

    # 4. Verify the ed25519 signature
    try:
        wallet_bytes = base58.b58decode(wallet)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid wallet address")
    if len(wallet_bytes) != 32:
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    try:
        sig_bytes = base64.b64decode(signature)
        verify_key = nacl.signing.VerifyKey(wallet_bytes)
        verify_key.verify(expected_message.encode("utf-8"), sig_bytes)
    except nacl.exceptions.BadSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature verification failed",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature format",
        )

    # 5. Create session and issue tokens
    session, rt, at, at_exp, rt_exp = await create_session(
        db, wallet, ip_hash, user_agent_hash
    )

    return session, rt, at, at_exp, rt_exp