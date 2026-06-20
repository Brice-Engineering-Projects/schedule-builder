"""Output / export routes for WBS runs."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from schedule_builder.auth.dependencies import get_current_user
from schedule_builder.core.exceptions import NotFoundError
from schedule_builder.db.session import get_db_session
from schedule_builder.repositories.project_repository import ProjectRepository
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.repositories.wbs_repository import WbsRepository
from schedule_builder.services.output_service import OutputFormat, OutputService

if TYPE_CHECKING:
    from schedule_builder.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/wbs/runs", tags=["export"])


def get_output_service(db: Session = Depends(get_db_session)) -> OutputService:
    """Inject OutputService with repositories."""
    return OutputService(
        wbs_repository=WbsRepository(db),
        scope_repository=ScopeRepository(db),
    )


@router.get(
    "/{wbs_run_id}/export",
    summary="Export WBS run as markdown, CSV, or JSON",
    response_class=Response,
)
def export_wbs(
    wbs_run_id: str,
    fmt: Annotated[OutputFormat, Query(alias="format")] = "json",
    output_service: OutputService = Depends(get_output_service),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Export a WBS run in the requested format.

    Args:
        wbs_run_id: WBS run ID to export
        fmt: Output format — markdown, csv, or json (default: json)

    Returns:
        Response with appropriate Content-Type header

    Raises:
        HTTPException 404: If WBS run not found
        HTTPException 403: If user does not own the associated project
    """
    # Verify ownership before exporting
    wbs_repo = WbsRepository(db)
    project_repo = ProjectRepository(db)

    wbs_run = wbs_repo.get_wbs_run(wbs_run_id)
    if not wbs_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WBS run {wbs_run_id} not found",
        )

    project = project_repo.get_by_id(wbs_run.project_id)
    if not project or project.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to WBS run",
        )

    try:
        content, content_type = output_service.export(wbs_run_id, fmt)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return PlainTextResponse(content=content, media_type=content_type)
