"""ScopeAnalysis ORM model — AI scope extraction output."""

from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schedule_builder.db.base import Base
from schedule_builder.models.base import TimestampedUUIDMixin


class ScopeAnalysis(TimestampedUUIDMixin, Base):
    """Stores the structured JSON output from an AI scope extraction run."""

    __tablename__ = "scope_analyses"
    __table_args__ = (UniqueConstraint("document_id", name="uq_scope_analyses_document_id"),)

    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    scope_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped["Document"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Document", back_populates="scope_analysis"
    )

    def __repr__(self) -> str:
        return f"<ScopeAnalysis id={self.id!r} document_id={self.document_id!r} provider={self.provider!r}>"
