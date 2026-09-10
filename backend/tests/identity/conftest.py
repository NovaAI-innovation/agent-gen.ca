"""Shared test fakes for the Identity service."""

from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID, uuid4


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


class FakeSession:
    """Minimal fake mimicking AsyncSession for unit tests.

    Tracks added objects and flushes for assertion.
    """

    def __init__(self):
        self.added: list = []
        self.flushed = False
        self._execute_result = None

    def set_execute_result(self, value):
        """Seed the next execute() return value."""
        self._execute_result = value

    async def execute(self, _query):
        result = self._execute_result
        self._execute_result = None
        return _ScalarResult(result)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True


def make_nonce(**overrides) -> SimpleNamespace:
    """Build a fake AuthNonce-like object."""
    defaults = {
        "id": uuid4(),
        "wallet_address": "6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73",
        "nonce": "test-nonce-001",
        "used": False,
        "expires_at": __import__("datetime").datetime(2099, 1, 1, tzinfo=__import__("datetime").timezone.utc),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def make_session(**overrides) -> SimpleNamespace:
    """Build a fake AuthSession-like object."""
    defaults = {
        "id": uuid4(),
        "user_id": uuid4(),
        "wallet_address": "6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73",
        "refresh_token_hash": "old-hash",
        "rotation_counter": 0,
        "status": "active",
        "revoked_at": None,
        "expires_at": __import__("datetime").datetime(2099, 1, 1, tzinfo=__import__("datetime").timezone.utc),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)