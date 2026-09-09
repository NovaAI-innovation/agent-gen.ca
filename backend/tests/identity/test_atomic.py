"""Tests for the Identity service — atomic nonce consumption, session
rotation with optimistic locking, and revocation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.services import identity as svc


# ── Test helpers ─────────────────────────────────────────────────────────────


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return self

    def all(self):
        if self._value is None:
            return []
        if isinstance(self._value, list):
            return self._value
        return [self._value]


class _FakeDb:
    """Minimal fake AsyncSession for unit tests."""

    def __init__(self):
        self.added: list = []
        self.flushed = False
        self._result = None

    def set_result(self, value):
        self._result = value

    async def execute(self, _query):
        r = self._result
        self._result = None
        return _ScalarResult(r)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True


def _make_nonce(**kw):
    d = dict(
        id=uuid4(),
        wallet_address="6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73",
        nonce="test-nonce-001",
        used=False,
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )
    d.update(kw)
    return SimpleNamespace(**d)


def _make_session(**kw):
    d = dict(
        id=uuid4(),
        user_id=uuid4(),
        wallet_address="6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73",
        refresh_token_hash="old-hash",
        rotation_counter=0,
        status="active",
        revoked_at=None,
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )
    d.update(kw)
    return SimpleNamespace(**d)


# ── consume_nonce ────────────────────────────────────────────────────────────


class TestConsumeNonce:
    @pytest.mark.asyncio
    async def test_marks_used(self):
        nonce = _make_nonce()
        db = _FakeDb()
        db.set_result(nonce)

        result = await svc.consume_nonce(db, nonce.id, nonce.wallet_address, nonce.nonce)

        assert result is not None
        assert result.used is True

    @pytest.mark.asyncio
    async def test_expired_returns_none(self):
        expired = datetime(2020, 1, 1, tzinfo=timezone.utc)
        nonce = _make_nonce(expires_at=expired)
        db = _FakeDb()
        db.set_result(None)

        result = await svc.consume_nonce(db, nonce.id, nonce.wallet_address, nonce.nonce)
        assert result is None

    @pytest.mark.asyncio
    async def test_already_used_returns_none(self):
        nonce = _make_nonce(used=True)
        db = _FakeDb()
        db.set_result(None)

        result = await svc.consume_nonce(db, nonce.id, nonce.wallet_address, nonce.nonce)
        assert result is None

    @pytest.mark.asyncio
    async def test_wrong_wallet_returns_none(self):
        nonce = _make_nonce()
        db = _FakeDb()
        db.set_result(None)

        result = await svc.consume_nonce(
            db, nonce.id, "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", nonce.nonce
        )
        assert result is None


# ── create_session ────────────────────────────────────────────────────────────


class TestCreateSession:
    @pytest.mark.asyncio
    async def test_issues_tokens(self, monkeypatch):
        wallet = "6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73"
        user = _make_nonce(id=uuid4(), wallet_address=wallet)

        monkeypatch.setattr(svc, "upsert_user", AsyncMock(return_value=user))
        monkeypatch.setattr(
            svc, "create_refresh_token",
            lambda data: ("rt-" + data.get("sid", "none"), datetime(2099, 1, 2, tzinfo=timezone.utc)),
        )
        monkeypatch.setattr(
            svc, "create_access_token",
            lambda data: ("at-" + data.get("sid", "none"), datetime(2099, 1, 1, 1, tzinfo=timezone.utc)),
        )
        monkeypatch.setattr(svc, "hash_token", lambda t: "hashed-" + t)

        db = _FakeDb()
        db.set_result([])

        session, rt, at, _, _ = await svc.create_session(db, wallet, "ip-hash", "ua-hash")

        assert len(db.added) == 1
        assert db.added[0].wallet_address == wallet
        assert db.added[0].rotation_counter == 0
        assert at.startswith("at-")
        assert rt.startswith("rt-")

    @pytest.mark.asyncio
    async def test_revokes_oldest_when_over_limit(self, monkeypatch):
        wallet = "6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73"
        user = _make_nonce(id=uuid4(), wallet_address=wallet)
        old = _make_session(
            user_id=user.id,
            wallet_address=wallet,
            created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )

        monkeypatch.setattr(svc, "upsert_user", AsyncMock(return_value=user))
        monkeypatch.setattr(svc, "create_refresh_token", lambda data: ("rt", datetime(2099, 1, 2, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "create_access_token", lambda data: ("at", datetime(2099, 1, 1, 1, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "hash_token", lambda t: "hashed-" + t)

        db = _FakeDb()
        db.set_result([old])

        await svc.create_session(db, wallet, "ip-hash", "ua-hash", max_active_sessions=1)

        assert old.status == "revoked"
        assert old.revoked_at is not None


# ── rotate_session ────────────────────────────────────────────────────────────


class TestRotateSession:
    @pytest.mark.asyncio
    async def test_success(self, monkeypatch):
        session = _make_session(rotation_counter=0)

        monkeypatch.setattr(svc, "create_refresh_token", lambda data: ("rt-new", datetime(2099, 1, 2, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "create_access_token", lambda data: ("at-new", datetime(2099, 1, 1, 1, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "hash_token", lambda t: "hashed-" + t)

        db = _FakeDb()

        class _Rowcount:
            rowcount = 1

        db.execute = AsyncMock(return_value=_Rowcount())
        db.refresh = AsyncMock()

        new_rt, _, new_at, _ = await svc.rotate_session(
            db, session, session.wallet_address, session.user_id, expected_counter=0
        )

        assert new_rt == "rt-new"
        assert new_at == "at-new"

    @pytest.mark.asyncio
    async def test_raises_409_on_concurrent_rotation(self, monkeypatch):
        session = _make_session(rotation_counter=0)

        monkeypatch.setattr(svc, "create_refresh_token", lambda data: ("rt-new", datetime(2099, 1, 2, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "create_access_token", lambda data: ("at-new", datetime(2099, 1, 1, 1, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "hash_token", lambda t: "hashed-" + t)

        db = _FakeDb()

        class _ZeroRows:
            rowcount = 0

        db.execute = AsyncMock(return_value=_ZeroRows())

        with pytest.raises(Exception) as exc:
            await svc.rotate_session(db, session, session.wallet_address, session.user_id, expected_counter=0)

        assert exc.typename == "HTTPException"
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_wrong_counter_fails(self, monkeypatch):
        session = _make_session(rotation_counter=1)  # actual counter is 1

        monkeypatch.setattr(svc, "create_refresh_token", lambda data: ("rt-new", datetime(2099, 1, 2, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "create_access_token", lambda data: ("at-new", datetime(2099, 1, 1, 1, tzinfo=timezone.utc)))
        monkeypatch.setattr(svc, "hash_token", lambda t: "hashed-" + t)

        db = _FakeDb()

        class _ZeroRows:
            rowcount = 0

        db.execute = AsyncMock(return_value=_ZeroRows())

        with pytest.raises(Exception) as exc:
            await svc.rotate_session(db, session, session.wallet_address, session.user_id, expected_counter=0)  # expects 0

        assert exc.typename == "HTTPException"
        assert exc.value.status_code == 409


# ── revoke_session ───────────────────────────────────────────────────────────


class TestRevokeSession:
    @pytest.mark.asyncio
    async def test_sets_fields(self):
        session = _make_session(revoked_at=None, status="active")
        await svc.revoke_session(session)
        assert session.status == "revoked"
        assert session.revoked_at is not None