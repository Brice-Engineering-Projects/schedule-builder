"""Repository for WBS (Work Breakdown Structure) database access."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from schedule_builder.models.wbs import WbsItem, WbsRun


class WbsRepository:
    """Database access for WBS runs and items."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_wbs_run(self, project_id: str, source_document_id: str | None = None) -> WbsRun:
        """Create new WBS run for a project."""
        wbs_run = WbsRun(project_id=project_id, source_document_id=source_document_id)
        self._db.add(wbs_run)
        self._db.flush()
        return wbs_run

    def add_wbs_items(
        self, wbs_run_id: str, items: list[dict[str, str | int | None]]
    ) -> list[WbsItem]:
        """Add WBS items to a run."""
        wbs_items = [
            WbsItem(
                wbs_run_id=wbs_run_id,
                wbs_number=item["wbs_number"],
                title=item["title"],
                level=item["level"],
                parent_wbs_number=item.get("parent_wbs_number"),
                sort_order=idx,
            )
            for idx, item in enumerate(items)
        ]
        self._db.add_all(wbs_items)
        self._db.flush()
        return wbs_items

    def get_wbs_run(self, wbs_run_id: str) -> WbsRun | None:
        """Retrieve WBS run by ID."""
        result = self._db.scalar(select(WbsRun).where(WbsRun.id == wbs_run_id))
        return result

    def get_wbs_run_by_document(self, document_id: str) -> WbsRun | None:
        """Retrieve most recent WBS run for a document."""
        result = self._db.scalar(
            select(WbsRun)
            .where(WbsRun.source_document_id == document_id)
            .order_by(WbsRun.created_at.desc())
        )
        return result

    def get_latest_by_project(self, project_id: str) -> WbsRun | None:
        """Retrieve the most recent WBS run for a project."""
        return self._db.scalar(
            select(WbsRun).where(WbsRun.project_id == project_id).order_by(WbsRun.created_at.desc())
        )

    def get_wbs_items(self, wbs_run_id: str) -> list[WbsItem]:
        """Get all items for a WBS run."""
        result = self._db.scalars(
            select(WbsItem).where(WbsItem.wbs_run_id == wbs_run_id).order_by(WbsItem.sort_order)
        )
        return list(result.all())
