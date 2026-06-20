"""SQLAlchemy engine and session management."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from schedule_builder.config.settings import settings


def _build_engine():
    """Create a database engine from application settings."""

    if settings.database_url.startswith("sqlite"):
        return create_engine(
            settings.database_url,
            echo=settings.database_echo,
            connect_args={"check_same_thread": False},
        )

    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        pool_recycle=settings.database_pool_recycle,
    )


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a transactional DB session for request-scoped dependencies."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
