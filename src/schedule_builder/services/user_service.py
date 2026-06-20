"""User business logic — used by auth and user-facing routes."""

from __future__ import annotations

from schedule_builder.auth.schemas import UserPublic
from schedule_builder.core.exceptions import ConflictError, NotFoundError
from schedule_builder.models.user import User
from schedule_builder.repositories.user_repository import UserRepository
from schedule_builder.utils.hashing import hash_password


class UserService:
    """Orchestrates user operations on top of UserRepository."""

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def create_user(self, email: str, full_name: str, password: str) -> User:
        if self._repo.exists_by_email(email):
            raise ConflictError(message="An account with this email already exists")
        return self._repo.create(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
        )

    def get_by_id(self, user_id: str) -> User:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(message="User not found", details={"user_id": user_id})
        return user

    def get_by_email(self, email: str) -> User | None:
        return self._repo.get_by_email(email)

    @staticmethod
    def to_public(user: User) -> UserPublic:
        return UserPublic(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )
