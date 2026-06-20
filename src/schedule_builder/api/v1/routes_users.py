from fastapi import APIRouter

from schedule_builder.core.exceptions import BadRequestError, NotFoundError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: int) -> dict[str, str | int]:
    if user_id <= 0:
        raise BadRequestError(
            message="User ID must be a positive integer",
            details={"user_id": user_id},
        )

    if user_id != 1:
        raise NotFoundError(
            message="User not found",
            details={"user_id": user_id},
        )

    return {
        "id": 1,
        "email": "admin@schedulebuilder.com",
        "full_name": "Schedule Builder Admin",
        "status": "active",
    }
