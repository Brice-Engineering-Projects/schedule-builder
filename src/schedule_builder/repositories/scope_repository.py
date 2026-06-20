"""Database access layer for the ScopeAnalysis model."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from schedule_builder.models.document import Document
from schedule_builder.models.scope_analysis import ScopeAnalysis


class ScopeRepository:
    """Encapsulates persistence for scope analysis results."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_document_id(self, document_id: str) -> ScopeAnalysis | None:
        stmt = select(ScopeAnalysis).where(ScopeAnalysis.document_id == document_id)
        return self._db.scalar(stmt)

    def get_latest_by_project_id(self, project_id: str) -> ScopeAnalysis | None:
        """Return the most recent scope analysis for any document in a project."""
        stmt = (
            select(ScopeAnalysis)
            .join(Document, ScopeAnalysis.document_id == Document.id)
            .where(Document.project_id == project_id)
            .order_by(ScopeAnalysis.created_at.desc())
        )
        return self._db.scalar(stmt)

    def upsert(
        self,
        *,
        document_id: str,
        provider: str,
        model: str,
        scope_json: dict,
        summary: str | None,
    ) -> ScopeAnalysis:
        scope_analysis = self.get_by_document_id(document_id)
        if scope_analysis is None:
            scope_analysis = ScopeAnalysis(
                document_id=document_id,
                provider=provider,
                model=model,
                scope_json=scope_json,
                summary=summary,
            )
            self._db.add(scope_analysis)
        else:
            scope_analysis.provider = provider
            scope_analysis.model = model
            scope_analysis.scope_json = scope_json
            scope_analysis.summary = summary

        self._db.commit()
        self._db.refresh(scope_analysis)
        return scope_analysis
