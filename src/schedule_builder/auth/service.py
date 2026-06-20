"""Authentication service layer."""

from __future__ import annotations

from schedule_builder.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from schedule_builder.auth.tokens import create_access_token, create_refresh_token, decode_token
from schedule_builder.core.exceptions import UnauthorizedError
from schedule_builder.core.security import ACCESS_TOKEN_TYPE
from schedule_builder.services.user_service import UserService
from schedule_builder.utils.hashing import verify_password


class AuthService:
    """Manages user authentication workflows."""

    def __init__(self, user_service: UserService) -> None:
        self._users = user_service

    def register_user(self, payload: RegisterRequest) -> UserPublic:
        user = self._users.create_user(
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
        )
        return self._users.to_public(user)

    def login_user(self, payload: LoginRequest) -> AuthResponse:
        user = self._users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError(message="Invalid email or password")

        tokens = TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
        return AuthResponse(user=self._users.to_public(user), tokens=tokens)

    def get_current_user(self, access_token: str) -> UserPublic:
        token_payload = decode_token(access_token, expected_type=ACCESS_TOKEN_TYPE)
        user = self._users.get_by_id(token_payload.sub)
        if not user.is_active:
            raise UnauthorizedError(message="Account is inactive")
        return self._users.to_public(user)
