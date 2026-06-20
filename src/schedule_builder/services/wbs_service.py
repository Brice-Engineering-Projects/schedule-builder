"""Service for WBS (Work Breakdown Structure) generation from scope analysis."""

from __future__ import annotations

import logging
from typing import TypedDict, cast

from schedule_builder.core.exceptions import NotFoundError
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.repositories.wbs_repository import WbsRepository
from schedule_builder.schemas.scope import ScopeAnalysisPayload
from schedule_builder.schemas.wbs import WBSItemPayload, WBSPayload


class WbsItemDict(TypedDict):
    """Typed dict for a single WBS line item."""

    wbs_number: str
    title: str
    level: int
    parent_wbs_number: str | None


class WbsGenerationResult(TypedDict):
    """Return type of WbsService.generate_wbs_from_scope."""

    wbs_run_id: str
    project_id: str
    document_id: str
    item_count: int
    items: list[WbsItemDict]


logger = logging.getLogger(__name__)


class WbsService:
    """Generate and manage Work Breakdown Structure from scope analysis."""

    # Standard project phases for MVP
    STANDARD_PHASES = {
        "Project Management": "1.0",
        "Data Collection": "2.0",
        "Design": "3.0",
        "Environmental Services": "4.0",
    }

    def __init__(
        self,
        scope_repository: ScopeRepository,
        wbs_repository: WbsRepository,
    ) -> None:
        self.scope_repo = scope_repository
        self.wbs_repo = wbs_repository

    def generate_wbs_from_scope(self, document_id: str, project_id: str) -> WbsGenerationResult:
        """Generate WBS from persisted scope analysis.

        Args:
            document_id: Source document with analyzed scope
            project_id: Target project for WBS

        Returns:
            Dict with wbs_run_id, project_id, item_count, and items list

        Raises:
            NotFoundError: If scope analysis not found for document
        """
        # Fetch persisted scope analysis
        scope_analysis = self.scope_repo.get_by_document_id(document_id)
        if not scope_analysis:
            raise NotFoundError(
                f"No scope analysis found for document {document_id}. "
                "Run analysis before generating WBS."
            )

        logger.info(f"Generating WBS from scope analysis for document {document_id}")

        # Extract scope payload — scope_json is stored as a dict, parse into model
        scope_payload = ScopeAnalysisPayload(**scope_analysis.scope_json)

        # Build WBS phases
        wbs_items = self._build_wbs_structure(scope_payload)

        # Validate numbering
        WBSPayload(items=[WBSItemPayload.model_validate(item) for item in wbs_items])

        # Persist to database
        wbs_run = self.wbs_repo.create_wbs_run(
            project_id=project_id, source_document_id=document_id
        )
        self.wbs_repo.add_wbs_items(wbs_run.id, cast(list[dict[str, str | int | None]], wbs_items))

        logger.info(f"Generated {len(wbs_items)} WBS items in run {wbs_run.id}")

        return {
            "wbs_run_id": wbs_run.id,
            "project_id": project_id,
            "document_id": document_id,
            "item_count": len(wbs_items),
            "items": wbs_items,
        }

    def _build_wbs_structure(self, scope_payload: ScopeAnalysisPayload) -> list[WbsItemDict]:
        """Build hierarchical WBS structure from scope analysis payload.

        Args:
            scope_payload: ScopeAnalysisPayload with deliverables, disciplines, services

        Returns:
            List of WBS item dicts with wbs_number, title, level, parent_wbs_number
        """
        items: list[WbsItemDict] = []
        phase_counter = 1

        # 1. Project Management (always required)
        pm_phase = f"{phase_counter}.0"
        items.append(
            {
                "wbs_number": pm_phase,
                "title": "Project Management",
                "level": 1,
                "parent_wbs_number": None,
            }
        )
        phase_counter += 1

        # 2. Data Collection
        if scope_payload.disciplines or scope_payload.meetings:
            dc_phase = f"{phase_counter}.0"
            items.append(
                {
                    "wbs_number": dc_phase,
                    "title": "Data Collection & Site Reconnaissance",
                    "level": 1,
                    "parent_wbs_number": None,
                }
            )
            # Add tasks under Data Collection
            for idx, discipline in enumerate(scope_payload.disciplines[:5], 1):
                items.append(
                    {
                        "wbs_number": f"{dc_phase[:-2]}.{idx}",
                        "title": f"{discipline}",
                        "level": 2,
                        "parent_wbs_number": dc_phase,
                    }
                )
            phase_counter += 1

        # 3. Design phase
        design_phase = f"{phase_counter}.0"
        items.append(
            {
                "wbs_number": design_phase,
                "title": "Design",
                "level": 1,
                "parent_wbs_number": None,
            }
        )
        # Add deliverables as design tasks (max 5 per phase for MVP)
        for idx, deliverable in enumerate(scope_payload.deliverables[:5], 1):
            items.append(
                {
                    "wbs_number": f"{design_phase[:-2]}.{idx}",
                    "title": deliverable,
                    "level": 2,
                    "parent_wbs_number": design_phase,
                }
            )
        phase_counter += 1

        # 4. Environmental/Services phase (if applicable)
        if scope_payload.services or scope_payload.permits:
            services_phase = f"{phase_counter}.0"
            services_title = "Environmental Services & Permits"
            if "Environmental" in scope_payload.project_type:
                services_title = "Environmental Assessment & Permitting"

            items.append(
                {
                    "wbs_number": services_phase,
                    "title": services_title,
                    "level": 1,
                    "parent_wbs_number": None,
                }
            )
            # Add services as tasks
            combined_services = list(set(scope_payload.services + scope_payload.permits))[:5]
            for idx, service in enumerate(combined_services, 1):
                items.append(
                    {
                        "wbs_number": f"{services_phase[:-2]}.{idx}",
                        "title": service,
                        "level": 2,
                        "parent_wbs_number": services_phase,
                    }
                )

        return items
