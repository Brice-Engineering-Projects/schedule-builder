"""WBS ORM models — WbsRun and WbsItem."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schedule_builder.db.base import Base
from schedule_builder.models.base import TimestampedUUIDMixin


class WbsRun(TimestampedUUIDMixin, Base):
    """A single WBS generation event for a project."""

    __tablename__ = "wbs_runs"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    generation_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="generated", server_default="generated", index=True
    )

    project: Mapped["Project"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Project", back_populates="wbs_runs"
    )
    source_document: Mapped["Document | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Document", back_populates="wbs_runs"
    )
    items: Mapped[list["WbsItem"]] = relationship(
        "WbsItem",
        back_populates="wbs_run",
        cascade="all, delete-orphan",
        order_by="WbsItem.sort_order",
    )

    def __repr__(self) -> str:
        return f"<WbsRun id={self.id!r} project_id={self.project_id!r} status={self.generation_status!r}>"


class WbsItem(TimestampedUUIDMixin, Base):
    """A single line item within a WBS run."""

    __tablename__ = "wbs_items"
    __table_args__ = (
        UniqueConstraint("wbs_run_id", "wbs_number", name="uq_wbs_items_run_number"),
        CheckConstraint("level IN (1, 2)", name="level_mvp"),
    )

    wbs_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("wbs_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    wbs_number: Mapped[str] = mapped_column(String(24), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_wbs_number: Mapped[str | None] = mapped_column(String(24), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    wbs_run: Mapped["WbsRun"] = relationship("WbsRun", back_populates="items")

    def __repr__(self) -> str:
        return f"<WbsItem wbs_number={self.wbs_number!r} title={self.title!r} level={self.level}>"
