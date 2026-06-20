"""JWT token utilities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError

from schedule_builder.auth.schemas import TokenPayload
from schedule_builder.config.settings import settings
from schedule_builder.core.exceptions import UnauthorizedError
from schedule_builder.core.security import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE


def _build_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expires_at = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str) -> str:
    """Create a signed JWT access token for a subject."""
    return _build_token(
        subject=subject,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    """Create a signed JWT refresh token for a subject."""
    return _build_token(
        subject=subject,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> TokenPayload:
    """Decode and validate a JWT token payload."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        data = TokenPayload.model_validate(payload)
    except (InvalidTokenError, ValueError) as exc:
        raise UnauthorizedError(message="Invalid authentication token") from exc

    if data.type != expected_type:
        raise UnauthorizedError(message="Invalid token type")

    return data
