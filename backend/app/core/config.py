from __future__ import annotations

import os
import re
from urllib.parse import urlparse

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
_PLACEHOLDER_SECRETS = {
    "change-in-production",
    "change-me",
    "secret",
    "changeme",
    "your-secret-here",
    "super-secret",
}
_VALID_CLUSTERS = {"localnet", "devnet", "mainnet-beta"}
_VALID_SAME_SITE = {"lax", "strict", "none"}


def _is_production() -> bool:
    return os.getenv("ENVIRONMENT", "development").lower() in {"production", "prod"}


def _is_loopback(url: str) -> bool:
    try:
        hostname = urlparse(url).hostname or ""
        return hostname in _LOOPBACK_HOSTS
    except Exception:
        return False


class Settings(BaseSettings):
    # ── Environment ───────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://agentgen:agentgen123@localhost:5432/agentgen"

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── Security ──────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MAX_ACTIVE_SESSIONS_PER_USER: int = 3
    NONCE_EXPIRE_MINUTES: int = 5

    # ── Cookies ───────────────────────────────────────────────────────────
    REFRESH_COOKIE_NAME: str = "refresh_token"
    REFRESH_COOKIE_SECURE: bool = True
    REFRESH_COOKIE_SAMESITE: str = "strict"
    REFRESH_COOKIE_DOMAIN: str | None = None

    # ── CORS ──────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ── Rate limits ───────────────────────────────────────────────────────
    AUTH_RATE_LIMIT_CHALLENGE: str = "20/minute"
    AUTH_RATE_LIMIT_VERIFY: str = "10/minute"
    AUTH_RATE_LIMIT_REFRESH: str = "30/minute"
    TRUST_PROXY_IP: str | None = None

    # ── JWT ───────────────────────────────────────────────────────────────
    JWT_ISSUER: str = "agent-gen.ca"
    JWT_AUDIENCE: str = "agent-gen.ca-web"
    JWT_LEEWAY_SECONDS: int = 30

    # ── SIWS auth ─────────────────────────────────────────────────────────
    AUTH_DOMAIN: str = "agent-gen.ca"
    AUTH_URI: str = "https://agent-gen.ca"
    AUTH_CHAIN_ID: str = "solana:mainnet"
    AUTH_STATEMENT: str = "Sign in to agent-gen.ca"

    # ── Solana ────────────────────────────────────────────────────────────
    SOLANA_CLUSTER: str = "mainnet-beta"
    SOLANA_RPC_HTTP: str = "https://api.mainnet-beta.solana.com"
    SOLANA_RPC_WS: str = "wss://api.mainnet-beta.solana.com"
    SOLANA_RPC_FALLBACK: str | None = None

    # ── Payments (Release B) ──────────────────────────────────────────────
    USDC_MINT: str = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    PLATFORM_FEE_BPS: int = 250

    # ── Migrations ────────────────────────────────────────────────────────
    ENFORCE_ALEMBIC_VERSION: bool = False
    ALEMBIC_EXPECTED_REVISION: str | None = None

    # ── Project ───────────────────────────────────────────────────────────
    PROJECT_NAME: str = "agent-gen.ca"

    class Config:
        env_file = ".env"

    # ── Validators ────────────────────────────────────────────────────────

    @field_validator("SECRET_KEY")
    @classmethod
    def reject_placeholder_secret(cls, v: str) -> str:
        if _is_production() and v.strip().lower() in _PLACEHOLDER_SECRETS:
            raise ValueError(
                "SECRET_KEY must be set to a real secret in production. "
                "Found a placeholder value."
            )
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def reject_loopback_database(cls, v: str) -> str:
        if _is_production() and _is_loopback(v):
            raise ValueError(
                "DATABASE_URL must not point to a loopback address in production."
            )
        return v

    @field_validator("REDIS_URL")
    @classmethod
    def reject_loopback_redis(cls, v: str) -> str:
        if _is_production() and _is_loopback(v):
            raise ValueError(
                "REDIS_URL must not point to a loopback address in production."
            )
        return v

    @field_validator("SOLANA_RPC_HTTP")
    @classmethod
    def reject_loopback_rpc(cls, v: str) -> str:
        if _is_production() and _is_loopback(v):
            raise ValueError(
                "SOLANA_RPC_HTTP must not point to a loopback address in production."
            )
        return v

    @field_validator("SOLANA_CLUSTER")
    @classmethod
    def validate_cluster(cls, v: str) -> str:
        if v not in _VALID_CLUSTERS:
            raise ValueError(
                f"SOLANA_CLUSTER must be one of {_VALID_CLUSTERS}, got '{v}'."
            )
        return v

    @field_validator("REFRESH_COOKIE_SAMESITE")
    @classmethod
    def validate_samesite(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in _VALID_SAME_SITE:
            raise ValueError(
                f"REFRESH_COOKIE_SAMESITE must be one of {_VALID_SAME_SITE}, got '{v}'."
            )
        return normalized

    @field_validator("PLATFORM_FEE_BPS")
    @classmethod
    def validate_fee_bps(cls, v: int) -> int:
        if v < 0 or v > 10_000:
            raise ValueError(
                f"PLATFORM_FEE_BPS must be between 0 and 10000, got {v}."
            )
        return v

    @model_validator(mode="after")
    def production_requires_all_secrets(self) -> "Settings":
        if not _is_production():
            return self

        errors: list[str] = []

        if self.REFRESH_COOKIE_SECURE is not True:
            errors.append("REFRESH_COOKIE_SECURE must be true in production.")

        if self.SOLANA_CLUSTER == "localnet":
            errors.append("SOLANA_CLUSTER must not be 'localnet' in production.")

        if self.SECRET_KEY.strip().lower() in _PLACEHOLDER_SECRETS:
            errors.append("SECRET_KEY is still a placeholder.")

        if errors:
            raise ValueError(
                "Production configuration errors:\n  - " + "\n  - ".join(errors)
            )

        return self


settings = Settings()
