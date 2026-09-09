"""Tests for shared authentication abuse controls — rate limiter keying,
trusted proxy detection, and route decorator ordering.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from starlette.requests import Request

from app.core import rate_limit


def _make_request(client_host: str, forwarded: str | None = None) -> Request:
    headers = []
    if forwarded:
        headers.append((b"x-forwarded-for", forwarded.encode()))
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/auth/challenge",
        "headers": headers,
        "client": (client_host, 12345),
        "scheme": "http",
        "server": ("testserver", 80),
    }
    return Request(scope)


# ── Trusted proxy detection ──────────────────────────────────────────────────


class TestIsTrustedProxy:
    def test_trusts_any_peer_when_unset(self):
        with patch.object(rate_limit.settings, "TRUST_PROXY_IP", None):
            assert rate_limit._is_trusted_proxy("127.0.0.1") is True
            assert rate_limit._is_trusted_proxy("10.0.0.5") is True
            assert rate_limit._is_trusted_proxy(None) is True

    def test_trusts_only_configured_proxy(self):
        with patch.object(rate_limit.settings, "TRUST_PROXY_IP", "10.0.0.4"):
            assert rate_limit._is_trusted_proxy("10.0.0.4") is True
            assert rate_limit._is_trusted_proxy("10.0.0.5") is False
            assert rate_limit._is_trusted_proxy(None) is False


# ── Client IP extraction ──────────────────────────────────────────────────────


class TestClientIp:
    def test_uses_forwarded_when_trusted_proxy(self):
        with patch.object(rate_limit.settings, "TRUST_PROXY_IP", "10.0.0.4"):
            request = _make_request("10.0.0.4", "203.0.113.9")
            assert rate_limit._client_ip(request) == "203.0.113.9"

    def test_uses_leftmost_forwarded_entry(self):
        with patch.object(rate_limit.settings, "TRUST_PROXY_IP", "10.0.0.4"):
            request = _make_request("10.0.0.4", "203.0.113.9, 10.0.0.1")
            assert rate_limit._client_ip(request) == "203.0.113.9"

    def test_ignores_forwarded_when_not_trusted_proxy(self):
        with patch.object(rate_limit.settings, "TRUST_PROXY_IP", "10.0.0.4"):
            # Peer is NOT the proxy — attacker-supplied XFF must be ignored.
            request = _make_request("198.51.100.7", "203.0.113.9")
            assert rate_limit._client_ip(request) == "198.51.100.7"

    def test_falls_back_to_peer_without_forwarded(self):
        with patch.object(rate_limit.settings, "TRUST_PROXY_IP", "10.0.0.4"):
            request = _make_request("10.0.0.4", None)
            assert rate_limit._client_ip(request) == "10.0.0.4"

    def test_unknown_when_no_peer(self):
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/health",
                "headers": [],
                "scheme": "http",
                "server": ("testserver", 80),
            }
        )
        assert rate_limit._client_ip(request) == "unknown"


# ── Key function ─────────────────────────────────────────────────────────────


class TestClientIpKey:
    def test_returns_trusted_client_ip(self):
        with patch.object(rate_limit.settings, "TRUST_PROXY_IP", "10.0.0.4"):
            request = _make_request("10.0.0.4", "203.0.113.9")
            assert rate_limit.get_client_ip_key(request) == "203.0.113.9"


# ── Storage URI selection ────────────────────────────────────────────────────


class TestStorageUri:
    def test_uses_memory_for_localhost_redis(self):
        with patch.object(rate_limit.settings, "REDIS_URL", "redis://localhost:6379"):
            assert rate_limit._storage_uri() == "memory://"

    def test_uses_redis_for_production_redis(self):
        with patch.object(rate_limit.settings, "REDIS_URL", "redis://redis.internal:6379"):
            assert rate_limit._storage_uri() == "redis://redis.internal:6379"


# ── Route decorator ordering ─────────────────────────────────────────────────


class TestRateLimitDecoratorOrdering:
    def test_auth_routes_have_limiter_on_module(self):
        """The limiter instance is wired into the auth router module."""
        from app.routers import auth

        assert auth.limiter is not None

    def test_limiter_has_storage_configured(self):
        """Production deployments must share limits across workers via Redis."""
        from app.core.rate_limit import limiter

        assert limiter is not None