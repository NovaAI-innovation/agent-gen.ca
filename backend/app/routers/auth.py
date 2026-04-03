import base64
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

import base58
import nacl.exceptions
import nacl.signing
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.config import settings
from ..core.deps import AuthContext, get_current_auth_context
from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_request_value,
    hash_token,
)
from ..crud.user import get_user_by_id, upsert_user
from ..db.database import get_db
from ..models.nonce import AuthNonce
from ..models.session import AuthAuditEvent, AuthSession
from ..schemas.user import Token

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_signin_message(wallet: str, nonce: str) -> str:
    return f"Sign in to agent-gen.ca\n\nWallet: {wallet}\nNonce: {nonce}"


def _wallet_public_key_bytes(wallet: str) -> bytes:
    try:
        wallet_bytes = base58.b58decode(wallet)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid wallet address")
    if len(wallet_bytes) != 32:
        raise HTTPException(status_code=400, detail="Invalid wallet address")
    return wallet_bytes


def _request_metadata_hashes(request: Request) -> tuple[str | None, str | None]:
    forwarded_for = request.headers.get("x-forwarded-for")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else None)
    user_agent = request.headers.get("user-agent")
    return hash_request_value(client_ip), hash_request_value(user_agent)


def _set_refresh_cookie(response: Response, refresh_token: str, expires_at: datetime) -> None:
    max_age = max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        max_age=max_age,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path="/",
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


async def _record_auth_event(
    db: AsyncSession,
    event_type: str,
    ip_hash: str | None,
    user_agent_hash: str | None,
    *,
    user_id: UUID | None = None,
    wallet_address: str | None = None,
    session_id: UUID | None = None,
    details: str | None = None,
) -> None:
    db.add(
        AuthAuditEvent(
            user_id=user_id,
            wallet_address=wallet_address,
            session_id=session_id,
            event_type=event_type,
            details=details,
            ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
        )
    )


async def _enforce_session_limit(db: AsyncSession, user_id: UUID) -> None:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(AuthSession)
        .where(AuthSession.user_id == user_id)
        .where(AuthSession.status == "active")
        .where(AuthSession.revoked_at.is_(None))
        .where(AuthSession.expires_at > now)
        .order_by(AuthSession.created_at.asc())
    )
    active_sessions = list(result.scalars().all())
    excess = len(active_sessions) - settings.MAX_ACTIVE_SESSIONS_PER_USER + 1
    if excess <= 0:
        return

    for session in active_sessions[:excess]:
        session.status = "revoked"
        session.revoked_at = now


class ChallengeResponse(BaseModel):
    challenge_id: UUID
    nonce: str
    expires_at: datetime
    message: str


class VerifyRequest(BaseModel):
    wallet: str
    challenge_id: UUID
    nonce: str
    signature: str


class RefreshRequest(BaseModel):
    wallet: str


@router.get("/challenge", response_model=ChallengeResponse)
async def get_challenge(wallet: str, db: AsyncSession = Depends(get_db)):
    """Issue a one-time nonce for the wallet to sign with Phantom."""
    _wallet_public_key_bytes(wallet)

    nonce = secrets.token_hex(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.NONCE_EXPIRE_MINUTES)
    message = _build_signin_message(wallet, nonce)

    record = AuthNonce(wallet_address=wallet, nonce=nonce, expires_at=expires_at)
    db.add(record)
    await db.flush()

    return ChallengeResponse(
        challenge_id=record.id,
        nonce=nonce,
        expires_at=expires_at,
        message=message,
    )


@router.post("/verify", response_model=Token)
async def verify_signature(body: VerifyRequest, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    """Verify ed25519 Phantom signature and issue session-bound JWTs."""
    wallet_public_key = _wallet_public_key_bytes(body.wallet)
    ip_hash, user_agent_hash = _request_metadata_hashes(request)

    result = await db.execute(
        select(AuthNonce)
        .where(AuthNonce.id == body.challenge_id)
        .where(AuthNonce.wallet_address == body.wallet)
        .where(AuthNonce.nonce == body.nonce)
        .where(AuthNonce.used.is_(False))
        .where(AuthNonce.expires_at > datetime.now(timezone.utc))
        .with_for_update()
    )
    nonce_record = result.scalar_one_or_none()
    if not nonce_record:
        await _record_auth_event(
            db,
            event_type="login_failed",
            ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
            wallet_address=body.wallet,
            details="invalid_or_expired_challenge",
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired challenge")

    message = _build_signin_message(body.wallet, nonce_record.nonce)

    try:
        sig_bytes = base64.b64decode(body.signature)
        verify_key = nacl.signing.VerifyKey(wallet_public_key)
        verify_key.verify(message.encode("utf-8"), sig_bytes)
    except nacl.exceptions.BadSignatureError:
        await _record_auth_event(
            db,
            event_type="login_failed",
            ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
            wallet_address=body.wallet,
            details="signature_verification_failed",
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature verification failed")
    except Exception:
        await _record_auth_event(
            db,
            event_type="login_failed",
            ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
            wallet_address=body.wallet,
            details="invalid_signature_format",
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature format")

    nonce_record.used = True
    user = await upsert_user(db, body.wallet)

    await _enforce_session_limit(db, user.id)

    session_id = uuid.uuid4()
    refresh_token, refresh_exp = create_refresh_token(
        data={"sub": user.wallet_address, "uid": str(user.id), "sid": str(session_id)}
    )
    access_token, access_exp = create_access_token(
        data={"sub": user.wallet_address, "uid": str(user.id), "sid": str(session_id)}
    )

    db.add(
        AuthSession(
            id=session_id,
            user_id=user.id,
            wallet_address=user.wallet_address,
            refresh_token_hash=hash_token(refresh_token),
            status="active",
            expires_at=refresh_exp,
            last_used_at=datetime.now(timezone.utc),
            ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
        )
    )

    await _record_auth_event(
        db,
        event_type="login_success",
        ip_hash=ip_hash,
        user_agent_hash=user_agent_hash,
        user_id=user.id,
        wallet_address=user.wallet_address,
        session_id=session_id,
    )

    await db.commit()

    _set_refresh_cookie(response, refresh_token, refresh_exp)
    return Token(
        access_token=access_token,
        wallet_address=user.wallet_address,
        session_id=session_id,
        expires_at=access_exp,
    )


@router.post("/refresh", response_model=Token)
async def refresh_session(
    body: RefreshRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    ip_hash, user_agent_hash = _request_metadata_hashes(request)

    try:
        payload = decode_access_token(refresh_token)
        token_type: str | None = payload.get("typ")
        wallet: str | None = payload.get("sub")
        user_id_raw: str | None = payload.get("uid")
        session_id_raw: str | None = payload.get("sid")
        if token_type != "refresh" or not wallet or not user_id_raw or not session_id_raw:
            raise ValueError("Invalid refresh token claims")
        user_id = UUID(user_id_raw)
        session_id = UUID(session_id_raw)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if body.wallet != wallet:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wallet mismatch")

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
        or session.refresh_token_hash != hash_token(refresh_token)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is not active")

    user = await get_user_by_id(db, user_id)
    if not user or user.wallet_address != wallet:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_refresh_token, new_refresh_exp = create_refresh_token(
        data={"sub": wallet, "uid": str(user.id), "sid": str(session.id)}
    )
    new_access_token, new_access_exp = create_access_token(
        data={"sub": wallet, "uid": str(user.id), "sid": str(session.id)}
    )

    session.refresh_token_hash = hash_token(new_refresh_token)
    session.expires_at = new_refresh_exp
    session.last_used_at = now

    await _record_auth_event(
        db,
        event_type="refresh_success",
        ip_hash=ip_hash,
        user_agent_hash=user_agent_hash,
        user_id=user.id,
        wallet_address=wallet,
        session_id=session.id,
    )
    await db.commit()

    _set_refresh_cookie(response, new_refresh_token, new_refresh_exp)
    return Token(
        access_token=new_access_token,
        wallet_address=wallet,
        session_id=session.id,
        expires_at=new_access_exp,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    request: Request,
    auth: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    auth.session.status = "revoked"
    auth.session.revoked_at = now
    auth.session.last_used_at = now

    ip_hash, user_agent_hash = _request_metadata_hashes(request)
    await _record_auth_event(
        db,
        event_type="logout",
        ip_hash=ip_hash,
        user_agent_hash=user_agent_hash,
        user_id=auth.user.id,
        wallet_address=auth.user.wallet_address,
        session_id=auth.session.id,
    )
    await db.commit()

    _clear_refresh_cookie(response)
    return None


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    response: Response,
    request: Request,
    auth: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    await db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == auth.user.id)
        .where(AuthSession.status == "active")
        .values(status="revoked", revoked_at=now, last_used_at=now, updated_at=now)
    )

    ip_hash, user_agent_hash = _request_metadata_hashes(request)
    await _record_auth_event(
        db,
        event_type="logout_all",
        ip_hash=ip_hash,
        user_agent_hash=user_agent_hash,
        user_id=auth.user.id,
        wallet_address=auth.user.wallet_address,
        session_id=auth.session.id,
    )
    await db.commit()

    _clear_refresh_cookie(response)
    return None
