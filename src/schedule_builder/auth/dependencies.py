"""Dependency providers for auth routes."""

from fastapi import Depends
from sqlalchemy.orm import Session

from schedule_builder.auth.schemas import UserPublic
from schedule_builder.auth.service import AuthService
from schedule_builder.core.security import oauth2_scheme
from schedule_builder.db.session import get_db_session
from schedule_builder.repositories.user_repository import UserRepository
from schedule_builder.services.user_service import UserService


def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    """Resolve authenticated user from bearer token."""
    return service.get_current_user(token)
