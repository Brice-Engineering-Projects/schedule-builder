"""Unit tests for WBS service."""

from __future__ import annotations

from uuid import uuid4

import pytest

from schedule_builder.core.exceptions import NotFoundError
from schedule_builder.models.document import Document
from schedule_builder.models.project import Project
from schedule_builder.models.scope_analysis import ScopeAnalysis
from schedule_builder.models.user import User
from schedule_builder.repositories.scope_repository import ScopeRepository
from schedule_builder.repositories.wbs_repository import WbsRepository
from schedule_builder.schemas.scope import ScopeAnalysisPayload
from schedule_builder.services.wbs_service import WbsService


def _create_project(db_session) -> str:
    """Create a test project with owner."""
    owner = User(
        email=f"wbs.owner.{uuid4().hex[:8]}@example.com",
        full_name="WBS Test Owner",
        password_hash="hash",
    )
    db_session.add(owner)
    db_session.flush()
    project = Project(owner_user_id=owner.id, name="WBS Test Project", description=None)
    db_session.add(project)
    db_session.commit()
    return project.id


def _create_document_with_scope(db_session, project_id: str) -> str:
    """Create a document with scope analysis."""
    doc = Document(
        project_id=project_id,
        filename="test.pdf",
        content_type="application/pdf",
        file_size_bytes=1000,
        storage_path="/tmp/test.pdf",
    )
    db_session.add(doc)
    db_session.flush()

    # Create scope analysis
    scope_payload = ScopeAnalysisPayload(
        project_type="Geotechnical Investigation",
        scope_summary="Site investigation and recommendations",
        deliverables=["Boring logs", "Laboratory testing", "Engineering report"],
        disciplines=["Geotechnical Engineering", "Environmental"],
        meetings=["Kickoff", "60% design review"],
        permits=["Boring permit"],
        services=["Field investigation"],
    )

    scope = ScopeAnalysis(
        document_id=doc.id,
        provider="claude",
        model="test-model",
        scope_json=scope_payload.model_dump(),
        summary="Test summary",
    )
    db_session.add(scope)
    db_session.commit()
    return doc.id


def test_wbs_service_generates_from_scope(db_session) -> None:
    """Test WBS generation from persisted scope analysis."""
    project_id = _create_project(db_session)
    document_id = _create_document_with_scope(db_session, project_id)

    scope_repo = ScopeRepository(db_session)
    wbs_repo = WbsRepository(db_session)
    service = WbsService(scope_repo, wbs_repo)

    result = service.generate_wbs_from_scope(document_id=document_id, project_id=project_id)

    assert result["wbs_run_id"]
    assert result["project_id"] == project_id
    assert result["document_id"] == document_id
    assert result["item_count"] >= 5  # At least PM, Design, and some tasks
    assert len(result["items"]) == result["item_count"]

    # Verify structure
    for item in result["items"]:
        assert "wbs_number" in item
        assert "title" in item
        assert "level" in item


def test_wbs_service_raises_not_found_if_no_scope(db_session) -> None:
    """Test WBS generation fails if scope analysis not found."""
    project_id = _create_project(db_session)

    # Create document WITHOUT scope analysis
    doc = Document(
        project_id=project_id,
        filename="test.pdf",
        content_type="application/pdf",
        file_size_bytes=1000,
        storage_path="/tmp/test.pdf",
    )
    db_session.add(doc)
    db_session.commit()

    scope_repo = ScopeRepository(db_session)
    wbs_repo = WbsRepository(db_session)
    service = WbsService(scope_repo, wbs_repo)

    with pytest.raises(NotFoundError, match="No scope analysis found"):
        service.generate_wbs_from_scope(document_id=doc.id, project_id=project_id)


def test_wbs_service_includes_pm_phase() -> None:
    """Test WBS always includes Project Management phase."""
    scope_payload = ScopeAnalysisPayload(
        project_type="Geotechnical Investigation",
        scope_summary="Site investigation",
        deliverables=["Report"],
        disciplines=[],
        meetings=[],
        permits=[],
        services=[],
    )

    service = WbsService(None, None)  # type: ignore
    items = service._build_wbs_structure(scope_payload)

    # Find PM phase
    pm_items = [item for item in items if item["title"] == "Project Management"]
    assert len(pm_items) == 1
    assert pm_items[0]["wbs_number"] == "1.0"
    assert pm_items[0]["level"] == 1


def test_wbs_service_includes_design_phase() -> None:
    """Test WBS includes Design phase with deliverables as tasks."""
    scope_payload = ScopeAnalysisPayload(
        project_type="Environmental Assessment",
        scope_summary="Phase I ESA",
        deliverables=["Phase I ESA Report", "Phase II Recommendations"],
        disciplines=["Environmental"],
        meetings=["Kickoff"],
        permits=[],
        services=["Regulatory review"],
    )

    service = WbsService(None, None)  # type: ignore
    items = service._build_wbs_structure(scope_payload)

    # Find Design phase (should be 3.0)
    design_items = [item for item in items if item["wbs_number"] == "3.0"]
    assert len(design_items) == 1
    assert design_items[0]["title"] == "Design"

    # Verify deliverables are tasks under Design
    design_tasks = [item for item in items if item.get("parent_wbs_number") == "3.0"]
    assert len(design_tasks) >= 2


def test_wbs_service_includes_data_collection_for_disciplines() -> None:
    """Test WBS includes Data Collection phase when disciplines present."""
    scope_payload = ScopeAnalysisPayload(
        project_type="Transportation",
        scope_summary="Site survey",
        deliverables=["Existing Conditions Plan"],
        disciplines=["Surveying", "Geotechnical"],
        meetings=["Site walk"],
        permits=[],
        services=[],
    )

    service = WbsService(None, None)  # type: ignore
    items = service._build_wbs_structure(scope_payload)

    # Find Data Collection phase (should be 2.0)
    dc_items = [item for item in items if item["wbs_number"] == "2.0"]
    assert len(dc_items) == 1
    assert "Data Collection" in dc_items[0]["title"]

    # Verify disciplines are tasks under Data Collection
    dc_tasks = [item for item in items if item.get("parent_wbs_number") == "2.0"]
    assert len(dc_tasks) >= 2


def test_wbs_service_includes_services_phase_when_applicable() -> None:
    """Test WBS includes services/permits phase when applicable."""
    scope_payload = ScopeAnalysisPayload(
        project_type="Environmental",
        scope_summary="Permitting support",
        deliverables=["Permit application"],
        disciplines=[],
        meetings=[],
        permits=["NEPA review", "CWA Section 404"],
        services=["Regulatory consultation"],
    )

    service = WbsService(None, None)  # type: ignore
    items = service._build_wbs_structure(scope_payload)

    # Should have PM, Design, and Services phases
    top_level = [item for item in items if item["level"] == 1]
    titles = [item["title"] for item in top_level]
    assert "Project Management" in titles
    assert "Design" in titles
    assert any("Environmental" in title or "Permit" in title for title in titles)


def test_wbs_repository_creates_and_retrieves_run(
    db_session,
) -> None:
    """Test WBS repository create and retrieve."""
    repo = WbsRepository(db_session)

    # Create run
    wbs_run = repo.create_wbs_run(project_id="test-project-1")
    db_session.commit()
    assert wbs_run.id
    assert wbs_run.project_id == "test-project-1"

    # Retrieve
    retrieved = repo.get_wbs_run(wbs_run.id)
    assert retrieved
    assert retrieved.id == wbs_run.id


def test_wbs_repository_adds_items(
    db_session,
) -> None:
    """Test WBS repository add items."""
    repo = WbsRepository(db_session)

    # Create run
    wbs_run = repo.create_wbs_run(project_id="test-project-2")
    db_session.commit()

    # Add items
    items_data: list[dict[str, str | int | None]] = [
        {"wbs_number": "1.0", "title": "Phase 1", "level": 1, "parent_wbs_number": None},
        {"wbs_number": "1.1", "title": "Task 1", "level": 2, "parent_wbs_number": "1.0"},
    ]
    items = repo.add_wbs_items(wbs_run.id, items_data)
    db_session.commit()

    assert len(items) == 2
    assert items[0].wbs_number == "1.0"
    assert items[1].wbs_number == "1.1"

    # Retrieve items
    retrieved_items = repo.get_wbs_items(wbs_run.id)
    assert len(retrieved_items) == 2
