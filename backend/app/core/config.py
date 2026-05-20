from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://agentgen:agentgen123@localhost:5432/agentgen"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "change-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MAX_ACTIVE_SESSIONS_PER_USER: int = 3
    PROJECT_NAME: str = "agent-gen.ca"
    NONCE_EXPIRE_MINUTES: int = 5  # Phantom sign-in challenge TTL
    REFRESH_COOKIE_NAME: str = "refresh_token"
    REFRESH_COOKIE_SECURE: bool = True
    REFRESH_COOKIE_SAMESITE: str = "strict"
    REFRESH_COOKIE_DOMAIN: str | None = None
    AUTH_RATE_LIMIT_CHALLENGE: str = "20/minute"
    AUTH_RATE_LIMIT_VERIFY: str = "10/minute"
    AUTH_RATE_LIMIT_REFRESH: str = "30/minute"
    JWT_ISSUER: str = "agent-gen.ca"
    JWT_AUDIENCE: str = "agent-gen.ca-web"
    JWT_LEEWAY_SECONDS: int = 30
    AUTH_DOMAIN: str = "agent-gen.ca"
    AUTH_URI: str = "https://agent-gen.ca"
    AUTH_CHAIN_ID: str = "solana:mainnet"
    AUTH_STATEMENT: str = "Sign in to agent-gen.ca"
    SOLANA_CLUSTER: str = "mainnet-beta"
    SOLANA_RPC_HTTP: str = "https://api.mainnet-beta.solana.com"
    SOLANA_RPC_WS: str = "wss://api.mainnet-beta.solana.com"
    SOLANA_RPC_FALLBACK: str | None = None
    USDC_MINT: str = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    PLATFORM_FEE_BPS: int = 250
    ENFORCE_ALEMBIC_VERSION: bool = False
    ALEMBIC_EXPECTED_REVISION: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
