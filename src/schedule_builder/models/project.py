"""Project ORM model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schedule_builder.db.base import Base
from schedule_builder.models.base import TimestampedUUIDMixin


class Project(TimestampedUUIDMixin, Base):
    """Top-level container for documents and WBS runs."""

    __tablename__ = "projects"

    owner_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="draft", server_default="draft"
    )

    owner: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="projects"
    )
    documents: Mapped[list["Document"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Document", back_populates="project", cascade="all, delete-orphan"
    )
    wbs_runs: Mapped[list["WbsRun"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "WbsRun", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id!r} name={self.name!r} status={self.status!r}>"
