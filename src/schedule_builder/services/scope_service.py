"""Scope analysis service."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from schedule_builder.core.exceptions import BadRequestError, NotFoundError, ValidationFailedError
from schedule_builder.integrations.claude_client import ScopeAnalysisClient
from schedule_builder.models.document import Document
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.schemas.scope import (
    ScopeAnalysisPayload,
    ScopeAnalysisPublic,
    ScopeAnalysisResponse,
)
from schedule_builder.services.document_service import DocumentService
from schedule_builder.utils.prompts import load_prompt

SCOPE_SYSTEM_PROMPT = load_prompt("scope_analysis.md")


@dataclass(frozen=True)
class ScopeAnalysisRun:
    response: ScopeAnalysisResponse
    persisted: ScopeAnalysisPublic


class ScopeService:
    """Turn extracted document text into structured AI scope output."""

    def __init__(
        self,
        *,
        scope_repository: ScopeRepository,
        document_service: DocumentService,
        ai_client: ScopeAnalysisClient,
        prompt_version: str = "v1",
        chunk_size: int = 8000,
    ) -> None:
        self._scopes = scope_repository
        self._documents = document_service
        self._ai_client = ai_client
        self._prompt_version = prompt_version
        self._chunk_size = chunk_size
        self._system_prompt = SCOPE_SYSTEM_PROMPT

    def analyze_document_scope(self, document_id: str) -> ScopeAnalysisRun:
        document = self._documents.get_document(document_id)
        extracted_text = self._documents.get_document_text(document_id)
        if not extracted_text.text.strip():
            raise ValidationFailedError(
                message="Document text is empty", details={"document_id": document_id}
            )

        chunks = self._chunk_text(extracted_text.text)
        chunk_payloads = [
            self._analyze_chunk(document, chunk, index, len(chunks))
            for index, chunk in enumerate(chunks, start=1)
        ]
        merged = self._merge_payloads(chunk_payloads)
        persisted = self._scopes.upsert(
            document_id=document.id,
            provider=self._ai_client.provider_name,
            model=self._ai_client.model_name,
            scope_json=merged.model_dump(),
            summary=merged.scope_summary,
        )

        response = ScopeAnalysisResponse(
            document_id=document.id,
            source_filename=document.filename,
            provider=self._ai_client.provider_name,
            model=self._ai_client.model_name,
            prompt_version=self._prompt_version,
            extracted_at=datetime.now(tz=timezone.utc),
            analysis=merged,
            chunk_count=len(chunks),
        )
        return ScopeAnalysisRun(
            response=response, persisted=ScopeAnalysisPublic.model_validate(persisted)
        )

    def get_document_scope(self, document_id: str) -> ScopeAnalysisPublic:
        scope_analysis = self._scopes.get_by_document_id(document_id)
        if scope_analysis is None:
            raise NotFoundError(
                message="Scope analysis not found", details={"document_id": document_id}
            )
        return ScopeAnalysisPublic.model_validate(scope_analysis)

    def _analyze_chunk(
        self,
        document: Document,
        chunk: str,
        chunk_index: int,
        chunk_total: int,
    ) -> ScopeAnalysisPayload:
        user_prompt = self._build_user_prompt(
            document=document,
            chunk=chunk,
            chunk_index=chunk_index,
            chunk_total=chunk_total,
        )
        response_text = self._ai_client.analyze(
            system_prompt=self._system_prompt, user_prompt=user_prompt
        )
        return self._parse_response(response_text)

    @staticmethod
    def _parse_response(response_text: str) -> ScopeAnalysisPayload:
        cleaned = response_text.strip()
        cleaned = re.sub(r"^```(?:json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned).strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise BadRequestError(
                message="AI response was not valid JSON", details={"response": response_text}
            ) from exc
        return ScopeAnalysisPayload.model_validate(data)

    def _merge_payloads(self, payloads: list[ScopeAnalysisPayload]) -> ScopeAnalysisPayload:
        first = payloads[0]
        return ScopeAnalysisPayload(
            project_type=first.project_type,
            scope_summary=" ".join(
                payload.scope_summary.strip()
                for payload in payloads
                if payload.scope_summary.strip()
            ),
            deliverables=self._deduplicate_items(
                [item for payload in payloads for item in payload.deliverables]
            ),
            disciplines=self._deduplicate_items(
                [item for payload in payloads for item in payload.disciplines]
            ),
            meetings=self._deduplicate_items(
                [item for payload in payloads for item in payload.meetings]
            ),
            permits=self._deduplicate_items(
                [item for payload in payloads for item in payload.permits]
            ),
            services=self._deduplicate_items(
                [item for payload in payloads for item in payload.services]
            ),
        )

    def _build_user_prompt(
        self,
        *,
        document: Document,
        chunk: str,
        chunk_index: int,
        chunk_total: int,
    ) -> str:
        return (
            f"Analyze engineering scope text for document {document.filename}.\n"
            f"Chunk {chunk_index} of {chunk_total}.\n"
            f"Return valid JSON only.\n\n"
            f"TEXT:\n{chunk}"
        )

    def _chunk_text(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return [""]
        if len(cleaned) <= self._chunk_size:
            return [cleaned]

        chunks: list[str] = []
        start = 0
        while start < len(cleaned):
            end = min(start + self._chunk_size, len(cleaned))
            chunks.append(cleaned[start:end])
            start = end
        return chunks

    @staticmethod
    def _deduplicate_items(items: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for item in items:
            normalized = item.strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(normalized)
        return deduped
