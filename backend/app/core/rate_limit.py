"""Shared authentication abuse controls.

The limiter uses Redis-backed storage when REDIS_URL is configured so
limits are shared across API workers. When Redis is unavailable (local
development / tests), it falls back to in-memory storage.

Client IPs are only trusted from the configured edge proxy. If a request
arrives from an unexpected source, the limiter keys on the direct peer
address instead of the X-Forwarded-For header.
"""

from __future__ import annotations

from fastapi import Request
from slowapi import Limiter

from app.core.config import settings


def _is_trusted_proxy(peer: str | None) -> bool:
    """Return True when the immediate peer is the known edge proxy.

    In production the only proxy in front of the API is nginx. When
    TRUST_PROXY_IP is unset (local dev / tests), any peer is trusted so
    X-Forwarded-For still works locally.
    """
    trusted = settings.TRUST_PROXY_IP
    if not trusted:
        return True
    return bool(peer) and peer == trusted


def _client_ip(request: Request) -> str:
    """Extract the real client IP, trusting X-Forwarded-For only from the proxy."""
    peer = request.client.host if request.client else None
    if _is_trusted_proxy(peer):
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return peer or "unknown"


def get_client_ip_key(request: Request) -> str:
    """slowapi key_func — returns the trusted client IP."""
    return _client_ip(request)


def _storage_uri() -> str:
    """Pick Redis storage for production, in-memory for local dev."""
    url = settings.REDIS_URL
    if url.startswith(("redis://localhost", "redis://127.0.0.1", "redis://::1")):
        return "memory://"
    return url


limiter = Limiter(
    key_func=get_client_ip_key,
    storage_uri=_storage_uri(),
    headers_enabled=True,
    default_limits=[],
)


def rate_limit_headers() -> dict[str, str]:
    """Documentation helper describing the rate limit response headers."""
    return {
        "X-RateLimit-Limit": "Maximum number of requests per window",
        "X-RateLimit-Remaining": "Requests remaining in the current window",
        "X-RateLimit-Reset": "Seconds until the window resets",
        "Retry-After": "Seconds to wait before retrying after a 429",
    }