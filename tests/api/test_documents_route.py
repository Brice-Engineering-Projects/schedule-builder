from __future__ import annotations

import io

import fitz  # type: ignore[import-untyped]
from docx import Document as DocxDocument  # type: ignore[import-untyped]

from schedule_builder.config.settings import settings
from schedule_builder.models.project import Project


def _build_pdf_bytes(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    return document.tobytes()


def _build_docx_bytes() -> bytes:
    document = DocxDocument()
    document.add_paragraph(
        "Water line replacement for the southern corridor and related appurtenances"
    )
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_upload_document_requires_auth(client) -> None:
    response = client.post("/v1/documents/upload")

    assert response.status_code == 401


def test_upload_pdf_document(client, db_session, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_directory", str(tmp_path / "uploads"))

    register_response = client.post(
        "/auth/register",
        json={
            "email": "doc.user@example.com",
            "password": "S3curePassw0rd!",
            "full_name": "Doc User",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]
    project = Project(owner_user_id=user_id, name="Documents Project", description=None)
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    login_response = client.post(
        "/auth/login",
        json={
            "email": "doc.user@example.com",
            "password": "S3curePassw0rd!",
        },
    )
    token = login_response.json()["tokens"]["access_token"]

    response = client.post(
        "/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": ("scope.pdf", _build_pdf_bytes("Project scope for testing"), "application/pdf")
        },
        data={"project_id": project_id},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["document"]["project_id"] == project_id
    assert payload["document"]["processing_status"] == "extracted"
    assert "Project scope for testing" in payload["extracted_text"]["text"]


def test_upload_docx_document(client, db_session, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_directory", str(tmp_path / "uploads"))

    register_response = client.post(
        "/auth/register",
        json={
            "email": "docx.user@example.com",
            "password": "S3curePassw0rd!",
            "full_name": "Docx User",
        },
    )
    user_id = register_response.json()["id"]
    project = Project(owner_user_id=user_id, name="Documents Project", description=None)
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    login_response = client.post(
        "/auth/login",
        json={
            "email": "docx.user@example.com",
            "password": "S3curePassw0rd!",
        },
    )
    token = login_response.json()["tokens"]["access_token"]

    response = client.post(
        "/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "scope.docx",
                _build_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        data={"project_id": project_id},
    )

    assert response.status_code == 201
    assert "Water line replacement" in response.json()["extracted_text"]["text"]
