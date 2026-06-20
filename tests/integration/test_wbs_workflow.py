"""End-to-end integration test: upload → scope analysis → WBS → export."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from uuid import uuid4

import fitz  # type: ignore[import-untyped]

from schedule_builder.api.v1.routes_documents import get_scope_client
from schedule_builder.main import app
from schedule_builder.schemas.scope import ScopeAnalysisPayload


@dataclass
class FakeScopeClient:
    """Deterministic AI client stub for integration tests."""

    response_text: str
    provider_name: str = "claude"
    model_name: str = "test-model"

    def analyze(self, *, system_prompt: str, user_prompt: str) -> str:
        _ = system_prompt, user_prompt
        return self.response_text


def _make_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    return doc.tobytes()


def _register_and_login(client, email: str) -> tuple[str, str]:
    reg = client.post(
        "/auth/register",
        json={"email": email, "full_name": "Integration Test", "password": "S3curePassw0rd!"},
    )
    assert reg.status_code == 201, reg.json()
    user_id = reg.json()["id"]

    login = client.post(
        "/auth/login",
        json={"email": email, "password": "S3curePassw0rd!"},
    )
    assert login.status_code == 200, login.json()
    token = login.json()["tokens"]["access_token"]
    return user_id, token


def test_full_wbs_workflow(client, db_session, tmp_path, monkeypatch) -> None:
    """Upload a document, analyse scope, generate WBS, export in all three formats."""
    from schedule_builder.config.settings import settings

    monkeypatch.setattr(settings, "upload_directory", str(tmp_path / "uploads"))

    # ── Stub AI client ──────────────────────────────────────────────────────
    scope_payload = ScopeAnalysisPayload(
        project_type="Water Distribution",
        scope_summary="Design of water main replacement for the southern corridor.",
        deliverables=["60% Plans", "Final Plans", "Specifications"],
        disciplines=["Civil", "Structural"],
        meetings=["Kickoff", "60% Review"],
        permits=["Construction Permit"],
        services=["Design"],
    )
    app.dependency_overrides[get_scope_client] = lambda: FakeScopeClient(
        scope_payload.model_dump_json()
    )

    try:
        email = f"workflow.{uuid4().hex[:8]}@example.com"
        _, token = _register_and_login(client, email)
        auth = {"Authorization": f"Bearer {token}"}

        # ── 1. Create project ───────────────────────────────────────────────
        proj_resp = client.post(
            "/v1/projects",
            json={"name": "Water Main Replacement", "description": "Integration test project"},
            headers=auth,
        )
        assert proj_resp.status_code == 201, proj_resp.json()
        project_id = proj_resp.json()["id"]

        # ── 2. Upload document ──────────────────────────────────────────────
        pdf_bytes = _make_pdf(
            "Scope of Work: Replace 2,400 LF of 12-inch water main.\n"
            "Deliverables: 60% plans, final plans, technical specifications.\n"
            "Disciplines: Civil Engineering, Structural Engineering.\n"
        )
        upload_resp = client.post(
            "/v1/documents/upload",
            headers=auth,
            files={"file": ("scope.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
            data={"project_id": project_id},
        )
        assert upload_resp.status_code == 201, upload_resp.json()
        document_id = upload_resp.json()["document"]["id"]

        # ── 3. Run scope analysis, then generate WBS ───────────────────────
        scope_analysis_resp = client.post(f"/v1/documents/{document_id}/scope", headers=auth)
        assert scope_analysis_resp.status_code == 200, scope_analysis_resp.json()

        wbs_resp = client.post(
            "/v1/wbs/generate",
            json={"document_id": document_id},
            headers=auth,
        )
        assert wbs_resp.status_code == 201, wbs_resp.json()
        wbs_data = wbs_resp.json()
        wbs_run_id = wbs_data["wbs_run_id"]
        assert wbs_data["item_count"] >= 5

        # ── 4. Retrieve WBS via project endpoint ────────────────────────────
        proj_wbs = client.get(f"/v1/projects/{project_id}/wbs", headers=auth)
        assert proj_wbs.status_code == 200
        assert len(proj_wbs.json()["items"]) >= 5

        # ── 5. Retrieve scope / disciplines / deliverables ──────────────────
        scope_resp = client.get(f"/v1/projects/{project_id}/scope", headers=auth)
        assert scope_resp.status_code == 200
        assert scope_resp.json()["project_type"] == "Water Distribution"

        disc_resp = client.get(f"/v1/projects/{project_id}/disciplines", headers=auth)
        assert disc_resp.status_code == 200
        assert disc_resp.json()["disciplines"] == ["Civil", "Structural"]

        deliv_resp = client.get(f"/v1/projects/{project_id}/deliverables", headers=auth)
        assert deliv_resp.status_code == 200
        assert "60% Plans" in deliv_resp.json()["deliverables"]

        # ── 6. Export WBS — all three formats ──────────────────────────────
        for fmt in ("markdown", "csv", "json"):
            export_resp = client.get(
                f"/v1/wbs/runs/{wbs_run_id}/export",
                params={"format": fmt},
                headers=auth,
            )
            assert export_resp.status_code == 200, f"{fmt} export failed: {export_resp.text}"
            assert len(export_resp.text) > 0

        # Verify JSON export structure
        json_export = client.get(
            f"/v1/projects/{project_id}/wbs/export",
            params={"format": "json"},
            headers=auth,
        )
        assert json_export.status_code == 200
        data = json.loads(json_export.text)
        assert data["project_id"] == project_id
        assert len(data["wbs"]) >= 5
        assert "scope" in data

    finally:
        app.dependency_overrides.clear()
