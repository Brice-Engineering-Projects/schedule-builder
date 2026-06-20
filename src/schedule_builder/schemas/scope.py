"""Schemas for AI scope analysis output."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScopeAnalysisPayload(BaseModel):
    project_type: str = Field(min_length=1)
    scope_summary: str = Field(min_length=1)
    deliverables: list[str] = Field(default_factory=list, min_length=1)
    disciplines: list[str] = Field(default_factory=list)
    meetings: list[str] = Field(default_factory=list)
    permits: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)


class ScopeAnalysisPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    provider: str
    model: str
    summary: str | None = None
    scope_json: ScopeAnalysisPayload


class ScopeAnalysisResponse(BaseModel):
    document_id: str
    source_filename: str
    provider: str
    model: str
    prompt_version: str
    extracted_at: datetime
    analysis: ScopeAnalysisPayload
    chunk_count: int
