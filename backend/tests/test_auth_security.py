from datetime import datetime, timezone

from jose import JWTError
from jose import jwt

from app.core import config
from app.core.security import ALGORITHM, create_access_token, decode_access_token
from app.routers.auth import _build_signin_message


def test_siws_message_includes_required_fields():
    message = _build_signin_message(
        wallet="8f4fW8JoVx9P45d6caeQzvbqVvL9vCB4uF3P4GQvQy3e",
        nonce="abc123",
        issued_at=datetime(2026, 4, 3, 0, 0, tzinfo=timezone.utc),
        expires_at=datetime(2026, 4, 3, 0, 5, tzinfo=timezone.utc),
    )

    assert "Chain ID:" in message
    assert "Nonce: abc123" in message
    assert f"URI: {config.settings.AUTH_URI}" in message
    assert f"{config.settings.AUTH_DOMAIN} wants you to sign in with your Solana account" in message


def test_decode_access_token_enforces_audience():
    token, _ = create_access_token({"sub": "wallet", "uid": "user", "sid": "session"})
    payload = decode_access_token(token)
    assert payload["aud"] == config.settings.JWT_AUDIENCE
    assert payload["iss"] == config.settings.JWT_ISSUER

    bad_token = jwt.encode(
        {
            "sub": "wallet",
            "uid": "user",
            "sid": "session",
            "typ": "access",
            "aud": "wrong-aud",
            "iss": config.settings.JWT_ISSUER,
            "exp": datetime(2099, 1, 1, tzinfo=timezone.utc),
            "iat": datetime.now(timezone.utc),
        },
        config.settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    try:
        decode_access_token(bad_token)
    except JWTError:
        assert True
    else:
        raise AssertionError("Invalid audience token should fail decode")
