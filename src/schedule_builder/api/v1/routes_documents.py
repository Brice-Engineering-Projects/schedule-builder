"""Document upload and retrieval routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from schedule_builder.auth.dependencies import get_current_user
from schedule_builder.auth.schemas import UserPublic
from schedule_builder.config.settings import settings
from schedule_builder.core.exceptions import ServiceUnavailableError
from schedule_builder.db.session import get_db_session
from schedule_builder.integrations.claude_client import ClaudeClient, ScopeAnalysisClient
from schedule_builder.integrations.openai_client import OpenAIClient
from schedule_builder.repositories.document_repository import DocumentRepository
from schedule_builder.repositories.project_repository import ProjectRepository
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.schemas.document import (
    DocumentPublic,
    DocumentUploadResponse,
    ExtractedDocumentText,
)
from schedule_builder.schemas.scope import ScopeAnalysisPublic, ScopeAnalysisResponse
from schedule_builder.services.document_service import DocumentService
from schedule_builder.services.scope_service import ScopeService

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_repository(db: Session = Depends(get_db_session)) -> DocumentRepository:
    return DocumentRepository(db)


def get_project_repository(db: Session = Depends(get_db_session)) -> ProjectRepository:
    return ProjectRepository(db)


def get_document_service(
    document_repository: DocumentRepository = Depends(get_document_repository),
    project_repository: ProjectRepository = Depends(get_project_repository),
) -> DocumentService:
    return DocumentService(document_repository, project_repository, settings.upload_directory)


def get_scope_repository(db: Session = Depends(get_db_session)) -> ScopeRepository:
    return ScopeRepository(db)


def get_scope_client() -> ScopeAnalysisClient:
    if settings.ai_provider == "claude":
        return ClaudeClient()
    if settings.ai_provider == "openai":
        return OpenAIClient()
    raise ServiceUnavailableError(message="Unsupported AI provider")


def get_scope_service(
    scope_repository: ScopeRepository = Depends(get_scope_repository),
    document_service: DocumentService = Depends(get_document_service),
    ai_client: ScopeAnalysisClient = Depends(get_scope_client),
) -> ScopeService:
    return ScopeService(
        scope_repository=scope_repository, document_service=document_service, ai_client=ai_client
    )


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    project_id: str = Form(..., min_length=1),
    file: UploadFile = File(...),
    current_user: UserPublic = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    _ = current_user
    file_bytes = await file.read()
    document, extracted_text = service.ingest_document(
        project_id=project_id,
        filename=file.filename or "document",
        content_type=file.content_type or "application/octet-stream",
        file_bytes=file_bytes,
    )
    return DocumentUploadResponse(
        document=DocumentPublic.model_validate(document),
        extracted_text=extracted_text.model_copy(update={"document_id": document.id}),
    )


@router.get("/{document_id}", response_model=DocumentPublic)
async def get_document(
    document_id: str,
    current_user: UserPublic = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentPublic:
    _ = current_user
    return DocumentPublic.model_validate(service.get_document(document_id))


@router.get("/{document_id}/text", response_model=ExtractedDocumentText)
async def get_document_text(
    document_id: str,
    current_user: UserPublic = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> ExtractedDocumentText:
    _ = current_user
    return service.get_document_text(document_id)


@router.post("/{document_id}/scope", response_model=ScopeAnalysisResponse)
async def analyze_document_scope(
    document_id: str,
    current_user: UserPublic = Depends(get_current_user),
    service: ScopeService = Depends(get_scope_service),
) -> ScopeAnalysisResponse:
    _ = current_user
    return service.analyze_document_scope(document_id).response


@router.get("/{document_id}/scope", response_model=ScopeAnalysisPublic)
async def get_document_scope(
    document_id: str,
    current_user: UserPublic = Depends(get_current_user),
    service: ScopeService = Depends(get_scope_service),
) -> ScopeAnalysisPublic:
    _ = current_user
    return service.get_document_scope(document_id)
