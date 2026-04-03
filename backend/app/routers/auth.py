import secrets
import base64
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import nacl.signing
import nacl.exceptions

from ..core.config import settings
from ..core.security import create_access_token
from ..crud.user import upsert_user
from ..db.database import get_db
from ..models.nonce import AuthNonce
from ..schemas.user import Token

router = APIRouter(prefix="/auth", tags=["auth"])


class ChallengeResponse(BaseModel):
    nonce: str
    expires_at: datetime
    message: str


class VerifyRequest(BaseModel):
    wallet: str       # Solana base58 public key
    signature: str    # base64-encoded ed25519 signature


@router.get("/challenge", response_model=ChallengeResponse)
async def get_challenge(wallet: str, db: AsyncSession = Depends(get_db)):
    """Issue a one-time nonce for the wallet to sign with Phantom."""
    nonce = secrets.token_hex(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.NONCE_EXPIRE_MINUTES)
    message = f"Sign in to agent-gen.ca\n\nWallet: {wallet}\nNonce: {nonce}"

    record = AuthNonce(wallet_address=wallet, nonce=nonce, expires_at=expires_at)
    db.add(record)
    await db.commit()

    return ChallengeResponse(nonce=nonce, expires_at=expires_at, message=message)


@router.post("/verify", response_model=Token)
async def verify_signature(body: VerifyRequest, db: AsyncSession = Depends(get_db)):
    """Verify ed25519 Phantom signature and issue a JWT."""
    # Find a valid, unused nonce for this wallet
    result = await db.execute(
        select(AuthNonce)
        .where(AuthNonce.wallet_address == body.wallet)
        .where(AuthNonce.used == False)
        .where(AuthNonce.expires_at > datetime.now(timezone.utc))
        .order_by(AuthNonce.created_at.desc())
        .limit(1)
    )
    nonce_record = result.scalar_one_or_none()
    if not nonce_record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired challenge")

    message = f"Sign in to agent-gen.ca\n\nWallet: {body.wallet}\nNonce: {nonce_record.nonce}"

    try:
        public_key_bytes = base64.b58decode_check(body.wallet)
    except Exception:
        # Fallback: standard base58 without checksum (Solana pubkeys have no checksum)
        import base58
        try:
            public_key_bytes = base58.b58decode(body.wallet)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid wallet address")

    try:
        sig_bytes = base64.b64decode(body.signature)
        verify_key = nacl.signing.VerifyKey(public_key_bytes)
        verify_key.verify(message.encode("utf-8"), sig_bytes)
    except nacl.exceptions.BadSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature verification failed")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature format")

    # Mark nonce as used
    nonce_record.used = True
    await db.flush()

    user = await upsert_user(db, body.wallet)
    await db.commit()

    access_token = create_access_token(data={"sub": user.wallet_address})
    return Token(access_token=access_token)
