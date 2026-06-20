"""Database access layer for the User model."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from schedule_builder.models.user import User


class UserRepository:
    """Encapsulates all DB queries for User records."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.strip().lower())
        return self._db.scalar(stmt)

    def exists_by_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(self, email: str, full_name: str, password_hash: str) -> User:
        user = User(
            email=email.strip().lower(),
            full_name=full_name.strip(),
            password_hash=password_hash,
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update(self, user: User, **fields: object) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        self._db.commit()
        self._db.refresh(user)
        return user

    def deactivate(self, user: User) -> User:
        return self.update(user, is_active=False)
