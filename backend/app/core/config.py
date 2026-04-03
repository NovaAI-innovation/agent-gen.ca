from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://agentgen:agentgen123@localhost:5432/agentgen"
    SECRET_KEY: str = "change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MAX_ACTIVE_SESSIONS_PER_USER: int = 3
    PROJECT_NAME: str = "agent-gen.ca"
    NONCE_EXPIRE_MINUTES: int = 5  # Phantom sign-in challenge TTL
    REFRESH_COOKIE_NAME: str = "refresh_token"
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = "lax"

    class Config:
        env_file = ".env"


settings = Settings()
