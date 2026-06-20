"""Pydantic schemas for Project endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Request body for creating a new project."""

    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class ProjectPublic(BaseModel):
    """Project representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    status: str
    owner_user_id: str
