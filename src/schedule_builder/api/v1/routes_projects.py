"""Project, WBS-by-project, and analysis routes."""

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
from schedule_builder.schemas.project import ProjectCreate, ProjectPublic
from schedule_builder.schemas.scope import ScopeAnalysisPayload
from schedule_builder.schemas.wbs import WBSItemPublic, WBSPublic
from schedule_builder.services.output_service import OutputFormat, OutputService

if TYPE_CHECKING:
    from schedule_builder.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/projects", tags=["projects"])


# ---------------------------------------------------------------------------
# 6.2  Project CRUD
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=ProjectPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ProjectPublic:
    """Create a project owned by the authenticated user."""
    repo = ProjectRepository(db)
    project = repo.create(
        owner_user_id=current_user.id,
        name=body.name,
        description=body.description,
    )
    db.commit()
    return ProjectPublic.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectPublic],
    summary="List projects for the authenticated user",
)
def list_projects(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[ProjectPublic]:
    """Return all projects owned by the authenticated user."""
    repo = ProjectRepository(db)
    return [ProjectPublic.model_validate(p) for p in repo.list_by_owner(current_user.id)]


@router.get(
    "/{project_id}",
    response_model=ProjectPublic,
    summary="Retrieve project details",
)
def get_project(
    project_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ProjectPublic:
    """Return a single project. User must be the owner."""
    project = _get_owned_project(project_id, current_user.id, db)
    return ProjectPublic.model_validate(project)


# ---------------------------------------------------------------------------
# 6.3  WBS by project
# ---------------------------------------------------------------------------


@router.get(
    "/{project_id}/wbs",
    response_model=WBSPublic,
    summary="Retrieve the most recent WBS for a project",
)
def get_project_wbs(
    project_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> WBSPublic:
    """Return the latest WBS run for a project."""
    _get_owned_project(project_id, current_user.id, db)

    wbs_repo = WbsRepository(db)
    wbs_run = wbs_repo.get_latest_by_project(project_id)
    if not wbs_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No WBS found for this project",
        )

    items = wbs_repo.get_wbs_items(wbs_run.id)
    return WBSPublic(
        id=wbs_run.id,
        project_id=wbs_run.project_id,
        source_document_id=wbs_run.source_document_id,
        generation_status=wbs_run.generation_status,
        items=[WBSItemPublic.model_validate(i) for i in items],
    )


@router.get(
    "/{project_id}/wbs/export",
    summary="Export the most recent WBS as markdown, CSV, or JSON",
    response_class=Response,
)
def export_project_wbs(
    project_id: str,
    fmt: Annotated[OutputFormat, Query(alias="format")] = "json",
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Export the latest WBS run for a project in the requested format."""
    _get_owned_project(project_id, current_user.id, db)

    wbs_repo = WbsRepository(db)
    wbs_run = wbs_repo.get_latest_by_project(project_id)
    if not wbs_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No WBS found for this project",
        )

    service = OutputService(
        wbs_repository=wbs_repo,
        scope_repository=ScopeRepository(db),
    )
    try:
        content, content_type = service.export(wbs_run.id, fmt)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return PlainTextResponse(content=content, media_type=content_type)


# ---------------------------------------------------------------------------
# 6.4  Analysis endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/{project_id}/scope",
    response_model=ScopeAnalysisPayload,
    summary="Retrieve scope analysis results for a project",
)
def get_project_scope(
    project_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ScopeAnalysisPayload:
    """Return the most recent scope analysis for the project."""
    _get_owned_project(project_id, current_user.id, db)
    scope = _get_scope_or_404(project_id, db)
    return ScopeAnalysisPayload(**scope.scope_json)


@router.get(
    "/{project_id}/disciplines",
    response_model=dict[str, list[str]],
    summary="Retrieve identified disciplines for a project",
)
def get_project_disciplines(
    project_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, list[str]]:
    """Return the sorted discipline list from the most recent scope analysis."""
    _get_owned_project(project_id, current_user.id, db)
    scope = _get_scope_or_404(project_id, db)
    payload = ScopeAnalysisPayload(**scope.scope_json)
    return {"disciplines": sorted(payload.disciplines)}


@router.get(
    "/{project_id}/deliverables",
    response_model=dict[str, list[str]],
    summary="Retrieve identified deliverables for a project",
)
def get_project_deliverables(
    project_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, list[str]]:
    """Return the deliverable list from the most recent scope analysis."""
    _get_owned_project(project_id, current_user.id, db)
    scope = _get_scope_or_404(project_id, db)
    payload = ScopeAnalysisPayload(**scope.scope_json)
    return {"deliverables": payload.deliverables}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_owned_project(project_id: str, user_id: str, db: Session):  # type: ignore[return]
    """Return project or raise 404/403."""

    project = ProjectRepository(db).get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    if project.owner_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to project",
        )
    return project


def _get_scope_or_404(project_id: str, db: Session):  # type: ignore[return]
    """Return scope analysis or raise 404."""

    scope = ScopeRepository(db).get_latest_by_project_id(project_id)
    if not scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scope analysis found for this project",
        )
    return scope
