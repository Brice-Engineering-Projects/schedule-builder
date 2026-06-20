"""Database access layer for the Document model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from schedule_builder.models.document import Document


class DocumentRepository:
    """Encapsulates all DB queries for Document records."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, document_id: str) -> Document | None:
        return self._db.get(Document, document_id)

    def create(
        self,
        *,
        document_id: str | None = None,
        project_id: str,
        filename: str,
        content_type: str,
        file_size_bytes: int,
        storage_path: str,
        processing_status: str = "uploaded",
        extracted_text: str | None = None,
        page_count: int | None = None,
        extracted_at: datetime | None = None,
        extraction_error: str | None = None,
    ) -> Document:
        document = Document(
            id=document_id,
            project_id=project_id,
            filename=filename,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            storage_path=storage_path,
            processing_status=processing_status,
            extracted_text=extracted_text,
            page_count=page_count,
            extracted_at=extracted_at,
            extraction_error=extraction_error,
        )
        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)
        return document

    def update(self, document: Document, **fields: object) -> Document:
        for key, value in fields.items():
            setattr(document, key, value)
        self._db.commit()
        self._db.refresh(document)
        return document
