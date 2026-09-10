from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import Response
from starlette.requests import Request

from app.models.session import AuthSession
from app.routers import auth


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class _FakeDbSession:
    def __init__(self, nonce_record):
        self.nonce_record = nonce_record
        self.added = []
        self.flushed = False
        self.committed = False

    async def execute(self, _query):
        return _ScalarResult(self.nonce_record)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_verify_signature_flushes_session_before_login_audit(monkeypatch):
    nonce_record = SimpleNamespace(
        id=uuid4(),
        wallet_address="6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73",
        nonce="nonce-123",
        message="signed-message",
        used=False,
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )
    db = _FakeDbSession(nonce_record)
    user = SimpleNamespace(id=uuid4(), wallet_address=nonce_record.wallet_address)

    monkeypatch.setattr(auth, "_wallet_public_key_bytes", lambda wallet: b"\x01" * 32)
    monkeypatch.setattr(auth, "_request_metadata_hashes", lambda request: ("ip-hash", "ua-hash"))
    monkeypatch.setattr(auth, "upsert_user", lambda db, wallet: user)
    monkeypatch.setattr(auth, "_enforce_session_limit", lambda db, user_id: None)
    monkeypatch.setattr(auth, "create_refresh_token", lambda data: ("refresh-token", datetime(2099, 1, 2, tzinfo=timezone.utc)))
    monkeypatch.setattr(auth, "create_access_token", lambda data: ("access-token", datetime(2099, 1, 1, 1, tzinfo=timezone.utc)))
    monkeypatch.setattr(auth, "_set_refresh_cookie", lambda response, token, expires_at: None)

    class _FakeVerifyKey:
        def __init__(self, _wallet_public_key):
            pass

        def verify(self, message, sig_bytes):
            return None

    monkeypatch.setattr(auth.nacl.signing, "VerifyKey", _FakeVerifyKey)
    monkeypatch.setattr(auth.base64, "b64decode", lambda value: b"signature")

    async def _fake_record_auth_event(db_session, event_type, ip_hash, user_agent_hash, **kwargs):
        assert event_type == "login_success"
        assert db_session.flushed is True
        assert any(isinstance(obj, AuthSession) for obj in db_session.added)

    monkeypatch.setattr(auth, "_record_auth_event", _fake_record_auth_event)

    async def _fake_upsert_user(db_session, wallet):
        return user

    async def _fake_enforce_session_limit(db_session, user_id):
        return None

    monkeypatch.setattr(auth, "upsert_user", _fake_upsert_user)
    monkeypatch.setattr(auth, "_enforce_session_limit", _fake_enforce_session_limit)

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/auth/verify",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "scheme": "http",
            "server": ("testserver", 80),
        }
    )
    response = Response()
    body = auth.VerifyRequest(
        wallet=nonce_record.wallet_address,
        challenge_id=nonce_record.id,
        nonce=nonce_record.nonce,
        signature="c2lnbmF0dXJl",
    )

    result = await auth.verify_signature(body=body, response=response, request=request, db=db)

    assert result.access_token == "access-token"
    assert nonce_record.used is True
    assert db.flushed is True
    assert db.committed is True
