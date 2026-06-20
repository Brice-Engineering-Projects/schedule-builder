"""Database access layer for the Project model."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from schedule_builder.models.project import Project


class ProjectRepository:
    """Encapsulates read and write operations for Project records."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, project_id: str) -> Project | None:
        return self._db.get(Project, project_id)

    def create(self, owner_user_id: str, name: str, description: str | None) -> Project:
        """Persist a new project owned by the given user."""
        project = Project(owner_user_id=owner_user_id, name=name, description=description)
        self._db.add(project)
        self._db.flush()
        return project

    def list_by_owner(self, owner_user_id: str) -> list[Project]:
        """Return all projects belonging to a user, newest first."""
        stmt = (
            select(Project)
            .where(Project.owner_user_id == owner_user_id)
            .order_by(Project.created_at.desc())
        )
        return list(self._db.scalars(stmt).all())
