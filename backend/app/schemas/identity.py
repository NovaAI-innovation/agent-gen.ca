"""SIWS (Sign-In With Solana) Pydantic schemas and message parser.

Follows the SIWS message format derived from EIP-4361, adapted for
Solana ed25519 signatures.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.core.config import settings


# ── SIWS message parsing ─────────────────────────────────────────────────────

_SIWS_LINE_RE = re.compile(
    r"^(?P<domain>.+)\s+wants you to sign in with your Solana account:\n"
    r"(?P<address>[1-9A-HJ-NP-Za-km-z]{32,44})\n\n"
    r"(?P<statement>.*?)\n\n"
    r"URI: (?P<uri>\S+)\n"
    r"Version: (?P<version>\S+)\n"
    r"Chain ID: (?P<chain_id>\S+)\n"
    r"Nonce: (?P<nonce>\S+)\n"
    r"Issued At: (?P<issued_at>.+?)\n"
    r"Expiration Time: (?P<expiration_time>.+?)\s*$",
    re.DOTALL,
)


def parse_siws_message(message: str) -> dict[str, str] | None:
    """Parse a SIWS message string into its constituent fields.

    Returns a dict with keys: domain, address, statement, uri, version,
    chain_id, nonce, issued_at, expiration_time.
    Returns None if the message does not match the expected format.
    """
    m = _SIWS_LINE_RE.match(message.strip())
    if not m:
        return None
    return m.groupdict()


def _iso_z(dt: datetime) -> str:
    """Format a datetime as UTC ISO 8601 with Z suffix, matching auth.py."""
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_siws_message(
    *,
    domain: str,
    address: str,
    statement: str,
    uri: str,
    chain_id: str,
    nonce: str,
    issued_at: datetime,
    expires_at: datetime,
    version: str = "1",
) -> str:
    """Build a standards-compliant SIWS message string with UTC Z-suffixed timestamps."""
    return (
        f"{domain} wants you to sign in with your Solana account:\n"
        f"{address}\n\n"
        f"{statement}\n\n"
        f"URI: {uri}\n"
        f"Version: {version}\n"
        f"Chain ID: {chain_id}\n"
        f"Nonce: {nonce}\n"
        f"Issued At: {_iso_z(issued_at)}\n"
        f"Expiration Time: {_iso_z(expires_at)}"
    )


# ── Request / Response schemas ────────────────────────────────────────────────


class SIWSChallengeResponse(BaseModel):
    """Response from the SIWS challenge endpoint (same as legacy)."""

    challenge_id: UUID
    nonce: str
    domain: str
    uri: str
    chain_id: str
    issued_at: datetime
    expires_at: datetime
    message: str


class SIWSVerifyRequest(BaseModel):
    """SIWS verify request — client submits individual fields for independent
    verification alongside the signature."""

    wallet: str
    challenge_id: UUID
    nonce: str
    signature: str
    domain: str
    uri: str
    chain_id: str
    issued_at: datetime


class SIWSVerifyResponse(BaseModel):
    """Response from the SIWS verify endpoint (same token shape as legacy)."""

    access_token: str
    token_type: str = "bearer"
    wallet_address: str
    session_id: UUID
    expires_at: datetime