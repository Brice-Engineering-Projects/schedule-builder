"""Dependency providers for auth routes."""

from fastapi import Depends

from schedule_builder.auth.schemas import UserPublic
from schedule_builder.auth.service import AuthService, auth_service
from schedule_builder.core.security import oauth2_scheme


def get_auth_service() -> AuthService:
    """Provide auth service instance."""
    return auth_service


def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    """Resolve authenticated user from bearer token."""
    return service.get_current_user(token)
