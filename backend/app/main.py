from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

import app.db.database as db
from app.core import config
from app.core.rate_limit import limiter


async def _assert_migration_state() -> None:
    if not config.settings.ENFORCE_ALEMBIC_VERSION:
        return

    async with db.engine.connect() as conn:
        try:
            result = await conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            current = result.scalar_one()
        except Exception as exc:
            raise RuntimeError(
                "Database is not migration-managed yet. Run `alembic upgrade head` before starting the API."
            ) from exc

    expected = config.settings.ALEMBIC_EXPECTED_REVISION
    if expected and current != expected:
        raise RuntimeError(
            f"Database revision mismatch: expected {expected}, got {current}. "
            "Run `alembic upgrade head` to reconcile schema."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.settings.SECRET_KEY == "change-in-production":
        raise RuntimeError(
            "SECRET_KEY is set to the default placeholder value. "
            "Set a strong SECRET_KEY environment variable before starting the server."
        )
    await _assert_migration_state()
    yield


app = FastAPI(title="agent-gen.ca API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = [
    origin.strip()
    for origin in config.settings.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "agent-gen.ca Marketplace API v1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


from app.routers import auth, marketplace, listings, reviews, purchases, users, dashboard

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(reviews.router)
app.include_router(marketplace.router)
app.include_router(purchases.router)
app.include_router(dashboard.router)
