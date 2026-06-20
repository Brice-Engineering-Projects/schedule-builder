"""Authentication service layer."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from schedule_builder.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from schedule_builder.auth.tokens import create_access_token, create_refresh_token, decode_token
from schedule_builder.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from schedule_builder.core.security import ACCESS_TOKEN_TYPE
from schedule_builder.utils.hashing import hash_password, verify_password


@dataclass
class _UserRecord:
    id: str
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True


class AuthService:
    """Manages user authentication workflows for MVP."""

    def __init__(self) -> None:
        self._users_by_email: dict[str, _UserRecord] = {}
        self._users_by_id: dict[str, _UserRecord] = {}

    def register_user(self, payload: RegisterRequest) -> UserPublic:
        normalized_email = payload.email.strip().lower()
        if normalized_email in self._users_by_email:
            raise ConflictError(message="An account with this email already exists")

        user = _UserRecord(
            id=str(uuid4()),
            email=normalized_email,
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
        )
        self._users_by_email[user.email] = user
        self._users_by_id[user.id] = user
        return self._to_public_user(user)

    def login_user(self, payload: LoginRequest) -> AuthResponse:
        normalized_email = payload.email.strip().lower()
        user = self._users_by_email.get(normalized_email)
        if user is None:
            raise UnauthorizedError(message="Invalid email or password")

        if not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError(message="Invalid email or password")

        tokens = TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
        return AuthResponse(user=self._to_public_user(user), tokens=tokens)

    def get_current_user(self, access_token: str) -> UserPublic:
        token_payload = decode_token(access_token, expected_type=ACCESS_TOKEN_TYPE)
        user = self._users_by_id.get(token_payload.sub)
        if user is None:
            raise NotFoundError(message="Authenticated user no longer exists")

        return self._to_public_user(user)

    @staticmethod
    def _to_public_user(user: _UserRecord) -> UserPublic:
        return UserPublic(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )


auth_service = AuthService()
