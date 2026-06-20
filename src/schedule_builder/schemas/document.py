"""Document request and response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    filename: str
    content_type: str
    file_size_bytes: int
    processing_status: str
    uploaded_at: datetime
    extracted_at: datetime | None = None
    page_count: int | None = None
    extraction_error: str | None = None


class ExtractedDocumentText(BaseModel):
    document_id: str
    source_filename: str
    content_type: str
    text: str = Field(min_length=1)
    character_count: int
    page_count: int | None = None
    extracted_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentPublic
    extracted_text: ExtractedDocumentText
    message: str = "Document uploaded and processed"
