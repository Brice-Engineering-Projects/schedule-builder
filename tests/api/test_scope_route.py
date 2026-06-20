from __future__ import annotations

from dataclasses import dataclass

from schedule_builder.api.v1.routes_documents import get_scope_client
from schedule_builder.main import app
from schedule_builder.models.project import Project
from schedule_builder.models.user import User
from schedule_builder.schemas.scope import ScopeAnalysisPayload


@dataclass
class FakeScopeClient:
    response_text: str
    provider_name: str = "claude"
    model_name: str = "test-model"

    def analyze(self, *, system_prompt: str, user_prompt: str) -> str:
        _ = system_prompt, user_prompt
        return self.response_text


def _create_project(db_session) -> str:
    owner = User(email="scope.route@example.com", full_name="Owner", password_hash="hash")
    db_session.add(owner)
    db_session.flush()
    project = Project(owner_user_id=owner.id, name="Route Project", description=None)
    db_session.add(project)
    db_session.commit()
    return project.id


def test_analyze_document_scope_route(client, db_session, tmp_path, monkeypatch) -> None:
    from schedule_builder.config.settings import settings

    monkeypatch.setattr(settings, "upload_directory", str(tmp_path / "uploads"))
    scope_payload = ScopeAnalysisPayload(
        project_type="Water Infrastructure",
        scope_summary="A short scope summary for the project.",
        deliverables=["Plan set"],
        disciplines=["Civil"],
        meetings=["Kickoff meeting"],
        permits=["ROW permit"],
        services=["Design"],
    ).model_dump_json()

    app.dependency_overrides[get_scope_client] = lambda: FakeScopeClient(scope_payload)

    try:
        register_response = client.post(
            "/auth/register",
            json={
                "email": "scope.route.user@example.com",
                "password": "S3curePassw0rd!",
                "full_name": "Scope Route User",
            },
        )
        user_id = register_response.json()["id"]
        project = Project(owner_user_id=user_id, name="Scope Project", description=None)
        db_session.add(project)
        db_session.commit()

        login_response = client.post(
            "/auth/login",
            json={
                "email": "scope.route.user@example.com",
                "password": "S3curePassw0rd!",
            },
        )
        token = login_response.json()["tokens"]["access_token"]

        upload_response = client.post(
            "/v1/documents/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "file": (
                    "scope.txt",
                    b"This scope text is long enough to be valid for analysis.",
                    "text/plain",
                )
            },
            data={"project_id": project.id},
        )
        document_id = upload_response.json()["document"]["id"]

        response = client.post(
            f"/v1/documents/{document_id}/scope",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["analysis"]["project_type"] == "Water Infrastructure"
    finally:
        app.dependency_overrides.pop(get_scope_client, None)
