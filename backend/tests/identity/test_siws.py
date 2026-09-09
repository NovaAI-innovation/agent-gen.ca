"""Tests for SIWS (Sign-In With Solana) verification — message building,
parsing, and signature verification with per-field independent checks.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.models.session import AuthSession
from app.schemas.identity import (
    SIWSVerifyRequest,
    build_siws_message,
    parse_siws_message,
    _iso_z,
)
from app.services import identity as svc
from app.routers import auth


# ── Helpers ──────────────────────────────────────────────────────────────────

_TEST_WALLET = "6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73"
_TEST_NONCE = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1"


def _make_nonce_record(**kw) -> SimpleNamespace:
    """Build a fake nonce record matching AuthNonce structure."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid4(),
        wallet_address=_TEST_WALLET,
        nonce=_TEST_NONCE,
        message=build_siws_message(
            domain="agent-gen.ca",
            address=_TEST_WALLET,
            statement="Sign in to agent-gen.ca",
            uri="https://agent-gen.ca",
            chain_id="solana:mainnet",
            nonce=_TEST_NONCE,
            issued_at=now,
            expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
        ),
        domain="agent-gen.ca",
        uri="https://agent-gen.ca",
        chain_id="solana:mainnet",
        issued_at=now,
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
        used=False,
    )
    defaults.update(kw)
    return SimpleNamespace(**defaults)


def _make_sig_bytes() -> bytes:
    """Return dummy 64-byte signature bytes."""
    return b"\x01" * 64


# ── Message building / parsing ────────────────────────────────────────────────


class TestBuildSIWSMessage:
    def test_build_matches_get_challenge_format(self):
        """The built message should match the format produced by the
        existing /auth/challenge endpoint."""
        now = datetime(2026, 9, 9, 16, 30, 0, tzinfo=timezone.utc)
        expires = datetime(2026, 9, 9, 16, 35, 0, tzinfo=timezone.utc)
        msg = build_siws_message(
            domain="agent-gen.ca",
            address=_TEST_WALLET,
            statement="Sign in to agent-gen.ca",
            uri="https://agent-gen.ca",
            chain_id="solana:mainnet",
            nonce=_TEST_NONCE,
            issued_at=now,
            expires_at=expires,
        )
        assert msg.startswith("agent-gen.ca wants you to sign in with your Solana account:")
        assert _TEST_WALLET in msg
        assert "Chain ID: solana:mainnet" in msg
        assert f"Nonce: {_TEST_NONCE}" in msg
        assert "Issued At: 2026-09-09T16:30:00Z" in msg
        assert "Expiration Time: 2026-09-09T16:35:00Z" in msg

    def test_two_builds_same_input_produce_same_output(self):
        now = datetime(2026, 9, 9, 16, 30, 0, tzinfo=timezone.utc)
        expires = datetime(2026, 9, 9, 16, 35, 0, tzinfo=timezone.utc)
        msg1 = build_siws_message(
            domain="agent-gen.ca", address=_TEST_WALLET, statement="Sign in",
            uri="https://agent-gen.ca", chain_id="solana:mainnet",
            nonce=_TEST_NONCE, issued_at=now, expires_at=expires,
        )
        msg2 = build_siws_message(
            domain="agent-gen.ca", address=_TEST_WALLET, statement="Sign in",
            uri="https://agent-gen.ca", chain_id="solana:mainnet",
            nonce=_TEST_NONCE, issued_at=now, expires_at=expires,
        )
        assert msg1 == msg2


class TestParseSIWSMessage:
    def test_parse_valid_message(self):
        msg = build_siws_message(
            domain="agent-gen.ca",
            address=_TEST_WALLET,
            statement="Sign in to agent-gen.ca",
            uri="https://agent-gen.ca",
            chain_id="solana:mainnet",
            nonce=_TEST_NONCE,
            issued_at=datetime(2026, 9, 9, 16, 30, 0, tzinfo=timezone.utc),
            expires_at=datetime(2026, 9, 9, 16, 35, 0, tzinfo=timezone.utc),
        )
        parsed = parse_siws_message(msg)
        assert parsed is not None
        assert parsed["domain"] == "agent-gen.ca"
        assert parsed["address"] == _TEST_WALLET
        assert parsed["chain_id"] == "solana:mainnet"
        assert parsed["nonce"] == _TEST_NONCE
        assert parsed["version"] == "1"

    def test_parse_bad_format_returns_none(self):
        assert parse_siws_message("not a siws message") is None
        assert parse_siws_message("") is None


# ── SIWS verify_siws_signature ────────────────────────────────────────────────


class TestVerifySIWSSignature:
    @pytest.mark.asyncio
    async def test_success_path(self, monkeypatch):
        """Full happy path: correct nonce, matching fields, valid sig."""
        now = datetime.now(timezone.utc)
        nonce_record = _make_nonce_record(
            issued_at=now,
            message=build_siws_message(
                domain="agent-gen.ca",
                address=_TEST_WALLET,
                statement="Sign in to agent-gen.ca",
                uri="https://agent-gen.ca",
                chain_id="solana:mainnet",
                nonce=_TEST_NONCE,
                issued_at=now,
                expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
            ),
        )

        # consume_nonce returns the nonce record
        monkeypatch.setattr(svc, "consume_nonce", AsyncMock(return_value=nonce_record))

        # Fake ed25519 verify — always succeeding
        class _FakeVerifyKey:
            def __init__(self, pk_bytes):
                pass
            def verify(self, msg, sig):
                return None

        monkeypatch.setattr(svc.nacl.signing, "VerifyKey", _FakeVerifyKey)
        monkeypatch.setattr(svc.base64, "b64decode", lambda v: _make_sig_bytes())
        monkeypatch.setattr(svc.base58, "b58decode", lambda v: b"\x01" * 32)

        # create_session returns a fake session
        class _FakeSession:
            pass

        fake_session = _FakeSession()
        fake_session.id = uuid4()
        fake_session.expires_at = datetime(2099, 1, 1, tzinfo=timezone.utc)
        fake_session.user_id = uuid4()

        monkeypatch.setattr(
            svc, "create_session",
            AsyncMock(return_value=(fake_session, "rt", "at", datetime(2099, 1, 1, 1, tzinfo=timezone.utc), datetime(2099, 1, 2, tzinfo=timezone.utc)))
        )

        db = AsyncMock()

        session, rt, at, at_exp, _ = await svc.verify_siws_signature(
            wallet=_TEST_WALLET,
            challenge_id=nonce_record.id,
            nonce=_TEST_NONCE,
            signature=base64.b64encode(_make_sig_bytes()).decode(),
            domain="agent-gen.ca",
            uri="https://agent-gen.ca",
            chain_id="solana:mainnet",
            issued_at=now,
            ip_hash="ip-hash",
            user_agent_hash="ua-hash",
            db=db,
        )

        assert rt == "rt"
        assert at == "at"
        assert session is fake_session

    @pytest.mark.asyncio
    async def test_fails_wrong_domain(self, monkeypatch):
        """Field-level check: wrong domain is rejected."""
        now = datetime.now(timezone.utc)
        nonce_record = _make_nonce_record(
            domain="agent-gen.ca",
            issued_at=now,
        )
        monkeypatch.setattr(svc, "consume_nonce", AsyncMock(return_value=nonce_record))

        # Create a message with the *correct* domain so message reconstruction
        # also fails, but the field-level check is the specific test.
        # Actually, if the message doesn't match, it fails earlier at message check.
        # To test field-level check independently, make the message match but field differ.
        # Build message with the WRONG domain so message check fails.
        msg_wrong_domain = build_siws_message(
            domain="evil.com",
            address=_TEST_WALLET,
            statement="Sign in to agent-gen.ca",
            uri="https://agent-gen.ca",
            chain_id="solana:mainnet",
            nonce=_TEST_NONCE,
            issued_at=now,
            expires_at=nonce_record.expires_at,
        )
        nonce_record_w_msg = _make_nonce_record(
            domain="agent-gen.ca",
            message=msg_wrong_domain,
            issued_at=now,
        )
        monkeypatch.setattr(svc, "consume_nonce", AsyncMock(return_value=nonce_record_w_msg))

        with pytest.raises(Exception) as exc:
            await svc.verify_siws_signature(
                wallet=_TEST_WALLET,
                challenge_id=nonce_record.id,
                nonce=_TEST_NONCE,
                signature=base64.b64encode(_make_sig_bytes()).decode(),
                domain="evil.com",
                uri="https://agent-gen.ca",
                chain_id="solana:mainnet",
                issued_at=now,
                ip_hash="ip-hash",
                user_agent_hash="ua-hash",
                db=AsyncMock(),
            )

        # Field-level domain check catches this
        assert exc.typename == "HTTPException"
        assert "domain" in str(exc.value.detail)

    @pytest.mark.asyncio
    async def test_fails_expired_nonce(self, monkeypatch):
        """Nonce is expired — consume_nonce returns None."""
        monkeypatch.setattr(svc, "consume_nonce", AsyncMock(return_value=None))
        db = AsyncMock()

        with pytest.raises(Exception) as exc:
            await svc.verify_siws_signature(
                wallet=_TEST_WALLET,
                challenge_id=uuid4(),
                nonce=_TEST_NONCE,
                signature="",
                domain="agent-gen.ca",
                uri="https://agent-gen.ca",
                chain_id="solana:mainnet",
                issued_at=datetime.now(timezone.utc),
                ip_hash="ip-hash",
                user_agent_hash="ua-hash",
                db=db,
            )

        assert exc.typename == "HTTPException"
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_fails_bad_signature(self, monkeypatch):
        """Ed25519 signature verification fails."""
        now = datetime.now(timezone.utc)
        nonce_record = _make_nonce_record(issued_at=now)
        monkeypatch.setattr(svc, "consume_nonce", AsyncMock(return_value=nonce_record))
        monkeypatch.setattr(svc.base58, "b58decode", lambda v: b"\x01" * 32)
        monkeypatch.setattr(svc.base64, "b64decode", lambda v: _make_sig_bytes())

        # Make nacl sign reject the signature
        class _BadVerifyKey:
            def __init__(self, pk_bytes):
                pass
            def verify(self, msg, sig):
                import nacl.exceptions
                raise nacl.exceptions.BadSignatureError("bad sig")

        monkeypatch.setattr(svc.nacl.signing, "VerifyKey", _BadVerifyKey)

        with pytest.raises(Exception) as exc:
            await svc.verify_siws_signature(
                wallet=_TEST_WALLET,
                challenge_id=nonce_record.id,
                nonce=_TEST_NONCE,
                signature=base64.b64encode(_make_sig_bytes()).decode(),
                domain="agent-gen.ca",
                uri="https://agent-gen.ca",
                chain_id="solana:mainnet",
                issued_at=now,
                ip_hash="ip-hash",
                user_agent_hash="ua-hash",
                db=AsyncMock(),
            )

        assert exc.typename == "HTTPException"
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_fails_on_wallet_public_key_bytes(self, monkeypatch):
        """Invalid wallet address (not base58 or wrong length) is rejected."""
        now = datetime.now(timezone.utc)
        nonce_record = _make_nonce_record(issued_at=now)
        monkeypatch.setattr(svc, "consume_nonce", AsyncMock(return_value=nonce_record))
        monkeypatch.setattr(svc.base58, "b58decode", lambda v: b"short")

        with pytest.raises(Exception) as exc:
            await svc.verify_siws_signature(
                wallet="invalid",
                challenge_id=nonce_record.id,
                nonce=_TEST_NONCE,
                signature="bad-sig",
                domain="agent-gen.ca",
                uri="https://agent-gen.ca",
                chain_id="solana:mainnet",
                issued_at=now,
                ip_hash="ip-hash",
                user_agent_hash="ua-hash",
                db=AsyncMock(),
            )

        assert exc.typename == "HTTPException"
        assert exc.value.status_code == 400


# ── Legacy fallback (existing /auth/verify still works) ────────────────────────


class TestLegacyVerify:
    def test_challenge_response_model(self):
        """The existing challenge response still validates as expected."""
        now = datetime.now(timezone.utc)
        body = auth.ChallengeResponse(
            challenge_id=uuid4(),
            nonce=_TEST_NONCE,
            domain="agent-gen.ca",
            uri="https://agent-gen.ca",
            chain_id="solana:mainnet",
            issued_at=now,
            expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
            message="test message",
        )
        assert body.nonce == _TEST_NONCE

    def test_verify_request_model(self):
        """The existing verify request model still validates."""
        body = auth.VerifyRequest(
            wallet=_TEST_WALLET,
            challenge_id=uuid4(),
            nonce=_TEST_NONCE,
            signature="c2lnbmF0dXJl",
        )
        assert body.wallet == _TEST_WALLET