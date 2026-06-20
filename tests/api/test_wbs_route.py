"""Integration tests for WBS API routes."""

from __future__ import annotations

from uuid import uuid4

from schedule_builder.models.document import Document
from schedule_builder.models.project import Project
from schedule_builder.models.scope_analysis import ScopeAnalysis
from schedule_builder.schemas.scope import ScopeAnalysisPayload


def _create_document_with_scope(db_session, project_id: str) -> str:
    """Create document with scope analysis."""
    doc = Document(
        project_id=project_id,
        filename="test.pdf",
        content_type="application/pdf",
        file_size_bytes=1000,
        storage_path="/tmp/test.pdf",
    )
    db_session.add(doc)
    db_session.flush()

    scope_payload = ScopeAnalysisPayload(
        project_type="Geotechnical Investigation",
        scope_summary="Site investigation and testing",
        deliverables=["Boring logs", "Lab testing", "Report"],
        disciplines=["Geotech", "Enviro"],
        meetings=["Kickoff"],
        permits=["Boring permit"],
        services=["Site investigation"],
    )

    scope = ScopeAnalysis(
        document_id=doc.id,
        provider="test",
        model="test-model",
        scope_json=scope_payload.model_dump(),
        summary="Test",
    )
    db_session.add(scope)
    db_session.commit()
    return doc.id


def _register_and_login(client, email: str) -> tuple[str, str]:
    """Register a user and return (user_id, access_token)."""
    reg = client.post(
        "/auth/register",
        json={"email": email, "full_name": "WBS Test", "password": "S3curePassw0rd!"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["id"]

    login = client.post(
        "/auth/login",
        json={"email": email, "password": "S3curePassw0rd!"},
    )
    assert login.status_code == 200
    token = login.json()["tokens"]["access_token"]
    return user_id, token


def test_generate_wbs_route(client, db_session) -> None:
    """Test WBS generation via HTTP route."""
    email = f"wbs.gen.{uuid4().hex[:8]}@example.com"
    user_id, token = _register_and_login(client, email)

    # Create project owned by the registered user
    project = Project(owner_user_id=user_id, name="WBS Gen Project", description=None)
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    document_id = _create_document_with_scope(db_session, project_id)

    response = client.post(
        "/v1/wbs/generate",
        json={"document_id": document_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "wbs_run_id" in data
    assert data["project_id"] == project_id
    assert data["document_id"] == document_id
    assert data["item_count"] >= 5


def test_get_wbs_run_route(client, db_session) -> None:
    """Test WBS retrieval via HTTP route."""
    email = f"wbs.get.{uuid4().hex[:8]}@example.com"
    user_id, token = _register_and_login(client, email)

    project = Project(owner_user_id=user_id, name="WBS Get Project", description=None)
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    document_id = _create_document_with_scope(db_session, project_id)

    # Generate WBS
    gen_resp = client.post(
        "/v1/wbs/generate",
        json={"document_id": document_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert gen_resp.status_code == 201
    wbs_run_id = gen_resp.json()["wbs_run_id"]

    # Retrieve WBS
    get_resp = client.get(
        f"/v1/wbs/runs/{wbs_run_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == wbs_run_id
    assert len(data["items"]) >= 5


def test_wbs_generation_requires_scope_analysis(client, db_session) -> None:
    """Test WBS generation fails if scope analysis not found."""
    email = f"wbs.noscope.{uuid4().hex[:8]}@example.com"
    user_id, token = _register_and_login(client, email)

    project = Project(owner_user_id=user_id, name="No Scope Project", description=None)
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    # Create document WITHOUT scope analysis
    doc = Document(
        project_id=project_id,
        filename="no-scope.pdf",
        content_type="application/pdf",
        file_size_bytes=500,
        storage_path="/tmp/no-scope.pdf",
    )
    db_session.add(doc)
    db_session.commit()

    response = client.post(
        "/v1/wbs/generate",
        json={"document_id": doc.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
