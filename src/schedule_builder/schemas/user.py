"""Pydantic schemas for user API requests and responses."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPublic(BaseModel):
    """Safe user representation — never includes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    is_active: bool


class UserUpdate(BaseModel):
    """Fields allowed in a PATCH /users/me request."""

    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = Field(default=None)
