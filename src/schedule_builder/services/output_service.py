"""Output generation service — formats WBS and scope analysis for export."""

from __future__ import annotations

import csv
import io
import json
import logging
from typing import Literal

from schedule_builder.core.exceptions import NotFoundError
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.repositories.wbs_repository import WbsRepository
from schedule_builder.schemas.scope import ScopeAnalysisPayload
from schedule_builder.services.wbs_service import WbsItemDict

logger = logging.getLogger(__name__)

OutputFormat = Literal["markdown", "csv", "json"]


class OutputService:
    """Generate formatted exports from a WBS run and its scope analysis."""

    def __init__(
        self,
        wbs_repository: WbsRepository,
        scope_repository: ScopeRepository,
    ) -> None:
        self.wbs_repo = wbs_repository
        self.scope_repo = scope_repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def export(self, wbs_run_id: str, fmt: OutputFormat) -> tuple[str, str]:
        """Generate export content for a WBS run.

        Args:
            wbs_run_id: ID of the WBS run to export
            fmt: Output format — "markdown", "csv", or "json"

        Returns:
            Tuple of (content: str, content_type: str)

        Raises:
            NotFoundError: If WBS run not found
        """
        wbs_run = self.wbs_repo.get_wbs_run(wbs_run_id)
        if not wbs_run:
            raise NotFoundError(f"WBS run {wbs_run_id} not found")

        items = self.wbs_repo.get_wbs_items(wbs_run_id)
        item_dicts: list[WbsItemDict] = [
            {
                "wbs_number": i.wbs_number,
                "title": i.title,
                "level": i.level,
                "parent_wbs_number": i.parent_wbs_number,
            }
            for i in items
        ]

        # Load scope analysis if available
        scope_payload: ScopeAnalysisPayload | None = None
        if wbs_run.source_document_id:
            scope = self.scope_repo.get_by_document_id(wbs_run.source_document_id)
            if scope:
                scope_payload = ScopeAnalysisPayload(**scope.scope_json)

        if fmt == "markdown":
            return self._to_markdown(item_dicts, scope_payload), "text/markdown; charset=utf-8"
        if fmt == "csv":
            return self._to_csv(item_dicts), "text/csv; charset=utf-8"
        # json
        return (
            self._to_json(wbs_run_id, wbs_run.project_id, item_dicts, scope_payload),
            "application/json",
        )

    # ------------------------------------------------------------------
    # Format generators
    # ------------------------------------------------------------------

    def _to_markdown(
        self,
        items: list[WbsItemDict],
        scope_payload: ScopeAnalysisPayload | None,
    ) -> str:
        """Render WBS and optional scope summary as Markdown."""
        lines: list[str] = []

        # Scope summary section
        if scope_payload:
            lines.append("## Scope Summary\n")
            lines.append(f"{scope_payload.scope_summary}\n")

            if scope_payload.disciplines:
                lines.append("\n## Disciplines\n")
                for d in sorted(scope_payload.disciplines):
                    lines.append(f"- {d}")
                lines.append("")

            if scope_payload.deliverables:
                lines.append("\n## Deliverables\n")
                for d in scope_payload.deliverables:
                    lines.append(f"- {d}")
                lines.append("")

        # WBS section
        lines.append("## Work Breakdown Structure\n")
        for item in items:
            if item["level"] == 1:
                lines.append(f"### {item['wbs_number']} {item['title']}")
            else:
                lines.append(f"- **{item['wbs_number']}** {item['title']}")

        return "\n".join(lines)

    def _to_csv(self, items: list[WbsItemDict]) -> str:
        """Render WBS items as UTF-8 CSV."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["wbs_number", "title", "level", "parent_wbs_number"],
            lineterminator="\n",
        )
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "wbs_number": item["wbs_number"],
                    "title": item["title"],
                    "level": item["level"],
                    "parent_wbs_number": item["parent_wbs_number"] or "",
                }
            )
        return output.getvalue()

    def _to_json(
        self,
        wbs_run_id: str,
        project_id: str,
        items: list[WbsItemDict],
        scope_payload: ScopeAnalysisPayload | None,
    ) -> str:
        """Render WBS and scope as structured JSON."""
        payload: dict = {
            "wbs_run_id": wbs_run_id,
            "project_id": project_id,
            "wbs": [
                {
                    "wbs_number": i["wbs_number"],
                    "title": i["title"],
                    "level": i["level"],
                    "parent_wbs_number": i["parent_wbs_number"],
                }
                for i in items
            ],
        }

        if scope_payload:
            payload["scope"] = {
                "project_type": scope_payload.project_type,
                "scope_summary": scope_payload.scope_summary,
                "disciplines": sorted(scope_payload.disciplines),
                "deliverables": scope_payload.deliverables,
                "meetings": scope_payload.meetings,
                "permits": scope_payload.permits,
                "services": scope_payload.services,
            }

        return json.dumps(payload, indent=2, ensure_ascii=False)
