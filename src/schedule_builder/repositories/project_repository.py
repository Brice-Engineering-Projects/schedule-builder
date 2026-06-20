"""Database access layer for the Project model."""

from __future__ import annotations

from sqlalchemy.orm import Session

from schedule_builder.models.project import Project


class ProjectRepository:
    """Encapsulates read operations for Project records."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, project_id: str) -> Project | None:
        return self._db.get(Project, project_id)
