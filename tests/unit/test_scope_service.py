from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import pytest
from pydantic import ValidationError

from schedule_builder.models.project import Project
from schedule_builder.models.user import User
from schedule_builder.repositories.document_repository import DocumentRepository
from schedule_builder.repositories.project_repository import ProjectRepository
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.schemas.scope import ScopeAnalysisPayload
from schedule_builder.services.document_service import DocumentService
from schedule_builder.services.scope_service import ScopeService
from schedule_builder.utils.prompts import load_prompt


@dataclass
class FakeScopeClient:
    response_text: str
    provider_name: str = "claude"
    model_name: str = "test-model"

    def analyze(self, *, system_prompt: str, user_prompt: str) -> str:
        _ = system_prompt, user_prompt
        return self.response_text


def _create_project(db_session) -> str:
    owner = User(
        email=f"scope.owner.{uuid4().hex[:8]}@example.com",
        full_name="Owner",
        password_hash="hash",
    )
    db_session.add(owner)
    db_session.flush()
    project = Project(owner_user_id=owner.id, name="Scope Project", description=None)
    db_session.add(project)
    db_session.commit()
    return project.id


def _create_document(db_session, tmp_path, project_id: str) -> str:
    document_service = DocumentService(
        DocumentRepository(db_session),
        ProjectRepository(db_session),
        str(tmp_path / "uploads"),
    )
    document, _ = document_service.ingest_document(
        project_id=project_id,
        filename="scope.txt",
        content_type="text/plain",
        file_bytes=(
            "This engineering scope includes civil design, permitting, coordination meetings, "
            "deliverable development, and discipline coordination for the project."
        ).encode("utf-8"),
    )
    return document.id


def test_scope_service_parses_and_persists_analysis(db_session, tmp_path) -> None:
    project_id = _create_project(db_session)
    document_id = _create_document(db_session, tmp_path, project_id)

    client = FakeScopeClient(
        response_text="""
        {
          "project_type": "Water Infrastructure",
          "scope_summary": "Design and permitting support for a water main replacement.",
          "deliverables": ["30% plans", "60% plans"],
          "disciplines": ["Civil", "Survey"],
          "meetings": ["Kickoff meeting"],
          "permits": ["ROW permit"],
          "services": ["Design", "Permitting"]
        }
        """,
    )
    service = ScopeService(
        scope_repository=ScopeRepository(db_session),
        document_service=DocumentService(
            DocumentRepository(db_session),
            ProjectRepository(db_session),
            str(tmp_path / "uploads"),
        ),
        ai_client=client,
    )

    result = service.analyze_document_scope(document_id)

    assert result.response.analysis.project_type == "Water Infrastructure"
    assert result.response.chunk_count == 1
    assert result.persisted.document_id == document_id


def test_scope_service_deduplicates_chunk_results(db_session, tmp_path) -> None:
    project_id = _create_project(db_session)
    document_id = _create_document(db_session, tmp_path, project_id)

    payload = {
        "project_type": "Roadway",
        "scope_summary": "Roadway improvements.",
        "deliverables": ["Plan set"],
        "disciplines": ["Civil"],
        "meetings": ["Coordination meeting"],
        "permits": ["Permit A"],
        "services": ["Design"],
    }
    fake_response = ScopeAnalysisPayload.model_validate(payload).model_dump_json()
    client = FakeScopeClient(response_text=fake_response)
    service = ScopeService(
        scope_repository=ScopeRepository(db_session),
        document_service=DocumentService(
            DocumentRepository(db_session),
            ProjectRepository(db_session),
            str(tmp_path / "uploads"),
        ),
        ai_client=client,
        chunk_size=20,
    )

    result = service.analyze_document_scope(document_id)

    assert result.response.chunk_count > 1
    assert result.response.analysis.deliverables == ["Plan set"]


def test_scope_payload_requires_at_least_one_deliverable() -> None:
    with pytest.raises(ValidationError):
        ScopeAnalysisPayload(
            project_type="Roadway",
            scope_summary="Roadway improvements.",
            deliverables=[],
            disciplines=["Civil"],
            meetings=["Coordination meeting"],
            permits=["Permit A"],
            services=["Design"],
        )


def test_scope_prompt_is_loaded_from_repository() -> None:
    prompt = load_prompt("scope_analysis.md")

    assert "project_type" in prompt
    assert "Return JSON only" in prompt
