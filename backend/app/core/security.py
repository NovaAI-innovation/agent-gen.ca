from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import uuid

from jose import jwt

import app.core.config as config

ALGORITHM = config.settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = config.settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "typ": "access",
            "iss": config.settings.PROJECT_NAME,
        }
    )
    return jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=ALGORITHM), expire


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
            "typ": "refresh",
            "iss": config.settings.PROJECT_NAME,
        }
    )
    return jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=ALGORITHM), expire


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, config.settings.SECRET_KEY, algorithms=[ALGORITHM])


def hash_token(token: str) -> str:
    # Pepper refresh tokens so DB leaks do not expose replayable refresh credentials.
    return hmac.new(
        config.settings.SECRET_KEY.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def hash_request_value(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
