"""Unit tests for OutputService — markdown, CSV, and JSON export formats."""

from __future__ import annotations

from uuid import uuid4

import pytest

from schedule_builder.models.document import Document
from schedule_builder.models.project import Project
from schedule_builder.models.scope_analysis import ScopeAnalysis
from schedule_builder.models.user import User
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.repositories.wbs_repository import WbsRepository
from schedule_builder.schemas.scope import ScopeAnalysisPayload
from schedule_builder.services.output_service import OutputService
from schedule_builder.services.wbs_service import WbsService


def _create_wbs_run_with_scope(db_session) -> tuple[str, str]:
    """Create a project, document, scope analysis, and WBS run. Returns (wbs_run_id, project_id)."""
    owner = User(
        email=f"output.{uuid4().hex[:8]}@example.com",
        full_name="Output Test",
        password_hash="hash",
    )
    db_session.add(owner)
    db_session.flush()

    project = Project(owner_user_id=owner.id, name="Output Project", description=None)
    db_session.add(project)
    db_session.flush()

    doc = Document(
        project_id=project.id,
        filename="scope.pdf",
        content_type="application/pdf",
        file_size_bytes=1000,
        storage_path="/tmp/scope.pdf",
    )
    db_session.add(doc)
    db_session.flush()

    scope_payload = ScopeAnalysisPayload(
        project_type="Water Infrastructure",
        scope_summary="Design of water distribution improvements for the southern corridor.",
        deliverables=["60% Design Plans", "Final Design Plans", "Technical Specifications"],
        disciplines=["Civil", "Structural", "Environmental"],
        meetings=["Kickoff Meeting", "60% Review"],
        permits=["NPDES Permit"],
        services=["Design", "Permitting Support"],
    )
    scope = ScopeAnalysis(
        document_id=doc.id,
        provider="claude",
        model="test-model",
        scope_json=scope_payload.model_dump(),
        summary="Water infrastructure design project.",
    )
    db_session.add(scope)
    db_session.flush()

    # Generate WBS via service so items exist
    scope_repo = ScopeRepository(db_session)
    wbs_repo = WbsRepository(db_session)
    service = WbsService(scope_repo, wbs_repo)
    result = service.generate_wbs_from_scope(document_id=doc.id, project_id=project.id)
    db_session.commit()

    return result["wbs_run_id"], project.id


def test_output_service_exports_markdown(db_session) -> None:
    """Markdown export contains WBS phases and scope summary."""
    wbs_run_id, _ = _create_wbs_run_with_scope(db_session)

    service = OutputService(WbsRepository(db_session), ScopeRepository(db_session))
    content, content_type = service.export(wbs_run_id, "markdown")

    assert "text/markdown" in content_type
    # WBS structure present
    assert "Work Breakdown Structure" in content
    assert "Project Management" in content
    assert "Design" in content
    # Scope summary present
    assert "Scope Summary" in content
    assert "water distribution" in content.lower()
    # Disciplines sorted alphabetically
    disciplines_section = content[content.index("Disciplines") :]
    civil_pos = disciplines_section.index("Civil")
    env_pos = disciplines_section.index("Environmental")
    assert civil_pos < env_pos


def test_output_service_exports_csv(db_session) -> None:
    """CSV export has correct header and rows for all WBS items."""
    wbs_run_id, _ = _create_wbs_run_with_scope(db_session)

    service = OutputService(WbsRepository(db_session), ScopeRepository(db_session))
    content, content_type = service.export(wbs_run_id, "csv")

    assert "text/csv" in content_type
    lines = content.strip().splitlines()
    # First line is header
    assert lines[0] == "wbs_number,title,level,parent_wbs_number"
    # At least header + some items
    assert len(lines) >= 5
    # Each row has 4 comma-separated fields
    for line in lines[1:]:
        assert line.count(",") == 3


def test_output_service_exports_json(db_session) -> None:
    """JSON export is valid JSON with wbs and scope keys."""
    import json as _json

    wbs_run_id, project_id = _create_wbs_run_with_scope(db_session)

    service = OutputService(WbsRepository(db_session), ScopeRepository(db_session))
    content, content_type = service.export(wbs_run_id, "json")

    assert content_type == "application/json"
    data = _json.loads(content)

    assert data["wbs_run_id"] == wbs_run_id
    assert data["project_id"] == project_id
    assert len(data["wbs"]) >= 5

    # Verify WBS item structure
    for item in data["wbs"]:
        assert "wbs_number" in item
        assert "title" in item
        assert "level" in item
        assert "parent_wbs_number" in item

    # Scope section present
    assert "scope" in data
    assert data["scope"]["project_type"] == "Water Infrastructure"
    assert data["scope"]["disciplines"] == ["Civil", "Environmental", "Structural"]  # sorted


def test_output_service_raises_not_found_for_missing_run(db_session) -> None:
    """NotFoundError raised when WBS run does not exist."""
    from schedule_builder.core.exceptions import NotFoundError

    service = OutputService(WbsRepository(db_session), ScopeRepository(db_session))

    with pytest.raises(NotFoundError, match="not found"):
        service.export("nonexistent-run-id", "json")
