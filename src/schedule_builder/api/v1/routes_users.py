"""User-facing API routes."""

from fastapi import APIRouter, Depends

from schedule_builder.auth.dependencies import get_current_user
from schedule_builder.auth.schemas import UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    """Return the currently authenticated user's profile."""
    return current_user
