"""API routes for WBS (Work Breakdown Structure) operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schedule_builder.auth.dependencies import get_current_user
from schedule_builder.core.exceptions import NotFoundError
from schedule_builder.db.session import get_db_session
from schedule_builder.repositories.document_repository import DocumentRepository
from schedule_builder.repositories.project_repository import ProjectRepository
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.repositories.wbs_repository import WbsRepository
from schedule_builder.schemas.wbs import (
    WBSGenerationRequest,
    WBSGenerationResponse,
    WBSItemPublic,
    WBSPublic,
)
from schedule_builder.services.wbs_service import WbsService

if TYPE_CHECKING:
    from schedule_builder.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/wbs", tags=["wbs"])


def get_wbs_service(db: Session = Depends(get_db_session)) -> WbsService:
    """Inject WBS service with repositories."""
    scope_repo = ScopeRepository(db)
    wbs_repo = WbsRepository(db)
    return WbsService(scope_repo, wbs_repo)


@router.post(
    "/generate",
    response_model=WBSGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate WBS from scope analysis",
)
def generate_wbs(
    request: WBSGenerationRequest,
    wbs_service: WbsService = Depends(get_wbs_service),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> WBSGenerationResponse:
    """Generate Work Breakdown Structure from persisted scope analysis.

    Args:
        request: WBSGenerationRequest with document_id
        wbs_service: WBS service (injected)
        db: Database session (injected)
        current_user: Authenticated user

    Returns:
        WBSGenerationResponse with generated WBS structure

    Raises:
        HTTPException 404: If scope analysis not found for document
        HTTPException 403: If user doesn't own document/project
    """
    # Load document to verify ownership and get project
    doc_repo = DocumentRepository(db)
    project_repo = ProjectRepository(db)

    document = doc_repo.get_by_id(request.document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {request.document_id} not found",
        )

    # Verify user owns document's project
    project = project_repo.get_by_id(document.project_id)
    if not project or project.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to document's project",
        )

    logger.info(
        f"User {current_user.id} generating WBS for document {request.document_id} "
        f"in project {project.id}"
    )

    try:
        result = wbs_service.generate_wbs_from_scope(
            document_id=request.document_id, project_id=project.id
        )

        return WBSGenerationResponse(
            wbs_run_id=result["wbs_run_id"],
            project_id=result["project_id"],
            document_id=result["document_id"],
            generation_status="generated",
            item_count=result["item_count"],
            wbs=[],  # Items returned separately
        )
    except NotFoundError as e:
        logger.warning(f"WBS generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/runs/{wbs_run_id}",
    response_model=WBSPublic,
    summary="Retrieve generated WBS structure",
)
def get_wbs_run(
    wbs_run_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> WBSPublic:
    """Retrieve a generated WBS run with all items.

    Args:
        wbs_run_id: WBS run ID to retrieve
        db: Database session (injected)
        current_user: Authenticated user

    Returns:
        WBSPublic with full structure

    Raises:
        HTTPException 404: If WBS run not found
        HTTPException 403: If user doesn't own associated project
    """
    wbs_repo = WbsRepository(db)
    project_repo = ProjectRepository(db)

    wbs_run = wbs_repo.get_wbs_run(wbs_run_id)
    if not wbs_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WBS run {wbs_run_id} not found",
        )

    # Verify user owns project
    project = project_repo.get_by_id(wbs_run.project_id)
    if not project or project.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to WBS run",
        )

    items = wbs_repo.get_wbs_items(wbs_run_id)

    return WBSPublic(
        id=wbs_run.id,
        project_id=wbs_run.project_id,
        source_document_id=wbs_run.source_document_id,
        generation_status=wbs_run.generation_status,
        items=[WBSItemPublic.model_validate(i) for i in items],
    )
