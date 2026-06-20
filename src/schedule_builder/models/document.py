"""Document ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schedule_builder.db.base import Base
from schedule_builder.models.base import TimestampedUUIDMixin


class Document(TimestampedUUIDMixin, Base):
    """Uploaded source file tied to a project."""

    __tablename__ = "documents"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="uploaded", server_default="uploaded", index=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Project", back_populates="documents"
    )
    scope_analysis: Mapped["ScopeAnalysis | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "ScopeAnalysis", back_populates="document", uselist=False, cascade="all, delete-orphan"
    )
    wbs_runs: Mapped[list["WbsRun"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "WbsRun", back_populates="source_document"
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id!r} filename={self.filename!r} status={self.processing_status!r}>"
