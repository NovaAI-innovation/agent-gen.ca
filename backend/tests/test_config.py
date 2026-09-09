"""Tests for backend configuration validation.

These tests exercise the Settings class without requiring a running database
or Redis instance — they only test validation logic.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

# All tests manipulate ENVIRONMENT via env vars, so import must happen after
# the patch context. We import the module once to access Settings.


def _make_settings(**overrides: str):
    """Build a Settings instance with controlled env vars."""
    env = {
        "ENVIRONMENT": "development",
        "SECRET_KEY": "test-secret-key-32-chars-long!!",
        "DATABASE_URL": "postgresql+asyncpg://agentgen:pass@localhost:5432/agentgen",
        "REDIS_URL": "redis://localhost:6379",
        "SOLANA_CLUSTER": "mainnet-beta",
        "SOLANA_RPC_HTTP": "https://api.mainnet-beta.solana.com",
        "SOLANA_RPC_WS": "wss://api.mainnet-beta.solana.com",
        **overrides,
    }
    with patch.dict(os.environ, env, clear=False):
        from app.core.config import Settings
        return Settings()


# ── Placeholder secrets ──────────────────────────────────────────────────


class TestPlaceholderSecrets:
    def test_development_allows_placeholder(self):
        settings = _make_settings(ENVIRONMENT="development", SECRET_KEY="change-in-production")
        assert settings.SECRET_KEY == "change-in-production"

    def test_production_rejects_placeholder(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(ENVIRONMENT="production", SECRET_KEY="change-in-production")
        assert "SECRET_KEY" in str(exc_info.value)

    def test_production_rejects_change_me(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(ENVIRONMENT="production", SECRET_KEY="change-me")
        assert "SECRET_KEY" in str(exc_info.value)

    def test_production_accepts_real_secret(self):
        settings = _make_settings(
            ENVIRONMENT="production",
            SECRET_KEY="a-real-production-secret-that-is-long-enough-32chars",
            DATABASE_URL="postgresql+asyncpg://user:pass@db.prod.internal:5432/agentgen",
            REDIS_URL="redis://redis.prod.internal:6379",
            SOLANA_RPC_HTTP="https://api.mainnet-beta.solana.com",
            SOLANA_CLUSTER="mainnet-beta",
        )
        assert settings.SECRET_KEY == "a-real-production-secret-that-is-long-enough-32chars"


# ── Loopback URLs in production ──────────────────────────────────────────


class TestLoopbackUrls:
    def test_production_rejects_localhost_database(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(
                ENVIRONMENT="production",
                SECRET_KEY="real-secret-32-chars-long-enough-ok",
                DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/agentgen",
                REDIS_URL="redis://redis.prod.internal:6379",
                SOLANA_RPC_HTTP="https://api.mainnet-beta.solana.com",
            )
        assert "DATABASE_URL" in str(exc_info.value)

    def test_production_rejects_127_redis(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(
                ENVIRONMENT="production",
                SECRET_KEY="real-secret-32-chars-long-enough-ok",
                DATABASE_URL="postgresql+asyncpg://user:pass@db.prod.internal:5432/agentgen",
                REDIS_URL="redis://127.0.0.1:6379",
                SOLANA_RPC_HTTP="https://api.mainnet-beta.solana.com",
            )
        assert "REDIS_URL" in str(exc_info.value)

    def test_production_rejects_loopback_rpc(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(
                ENVIRONMENT="production",
                SECRET_KEY="real-secret-32-chars-long-enough-ok",
                DATABASE_URL="postgresql+asyncpg://user:pass@db.prod.internal:5432/agentgen",
                REDIS_URL="redis://redis.prod.internal:6379",
                SOLANA_RPC_HTTP="http://localhost:8899",
            )
        assert "SOLANA_RPC_HTTP" in str(exc_info.value)

    def test_development_allows_loopback(self):
        settings = _make_settings(
            ENVIRONMENT="development",
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/agentgen",
            REDIS_URL="redis://localhost:6379",
            SOLANA_RPC_HTTP="http://localhost:8899",
        )
        assert "localhost" in settings.DATABASE_URL


# ── Cluster validation ───────────────────────────────────────────────────


class TestClusterValidation:
    def test_valid_clusters_accepted(self):
        for cluster in ("localnet", "devnet", "mainnet-beta"):
            settings = _make_settings(SOLANA_CLUSTER=cluster)
            assert settings.SOLANA_CLUSTER == cluster

    def test_invalid_cluster_rejected(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(SOLANA_CLUSTER="testnet")
        assert "SOLANA_CLUSTER" in str(exc_info.value)

    def test_production_rejects_localnet(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(
                ENVIRONMENT="production",
                SECRET_KEY="real-secret-32-chars-long-enough-ok",
                DATABASE_URL="postgresql+asyncpg://user:pass@db.prod.internal:5432/agentgen",
                REDIS_URL="redis://redis.prod.internal:6379",
                SOLANA_RPC_HTTP="https://api.mainnet-beta.solana.com",
                SOLANA_CLUSTER="localnet",
            )
        assert "localnet" in str(exc_info.value).lower()


# ── SameSite validation ──────────────────────────────────────────────────


class TestSameSiteValidation:
    def test_valid_samesite_values(self):
        for value in ("lax", "strict", "none"):
            settings = _make_settings(REFRESH_COOKIE_SAMESITE=value)
            assert settings.REFRESH_COOKIE_SAMESITE == value

    def test_invalid_samesite_rejected(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(REFRESH_COOKIE_SAMESITE="invalid")
        assert "REFRESH_COOKIE_SAMESITE" in str(exc_info.value)

    def test_samesite_case_normalized(self):
        settings = _make_settings(REFRESH_COOKIE_SAMESITE="Strict")
        assert settings.REFRESH_COOKIE_SAMESITE == "strict"


# ── Fee BPS validation ───────────────────────────────────────────────────


class TestFeeBpsValidation:
    def test_valid_fee_bps(self):
        settings = _make_settings(PLATFORM_FEE_BPS="500")
        assert settings.PLATFORM_FEE_BPS == 500

    def test_negative_fee_rejected(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(PLATFORM_FEE_BPS="-1")
        assert "PLATFORM_FEE_BPS" in str(exc_info.value)

    def test_excessive_fee_rejected(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(PLATFORM_FEE_BPS="10001")
        assert "PLATFORM_FEE_BPS" in str(exc_info.value)


# ── Production model-level guards ────────────────────────────────────────


class TestProductionModelGuards:
    def test_production_requires_secure_cookies(self):
        with pytest.raises(Exception) as exc_info:
            _make_settings(
                ENVIRONMENT="production",
                SECRET_KEY="real-secret-32-chars-long-enough-ok",
                DATABASE_URL="postgresql+asyncpg://user:pass@db.prod.internal:5432/agentgen",
                REDIS_URL="redis://redis.prod.internal:6379",
                SOLANA_RPC_HTTP="https://api.mainnet-beta.solana.com",
                REFRESH_COOKIE_SECURE="false",
            )
        assert "REFRESH_COOKIE_SECURE" in str(exc_info.value)

    def test_production_passes_all_valid(self):
        settings = _make_settings(
            ENVIRONMENT="production",
            SECRET_KEY="real-secret-32-chars-long-enough-ok",
            DATABASE_URL="postgresql+asyncpg://user:pass@db.prod.internal:5432/agentgen",
            REDIS_URL="redis://redis.prod.internal:6379",
            SOLANA_RPC_HTTP="https://api.mainnet-beta.solana.com",
            SOLANA_CLUSTER="mainnet-beta",
            REFRESH_COOKIE_SECURE="true",
        )
        assert settings.ENVIRONMENT == "production"
