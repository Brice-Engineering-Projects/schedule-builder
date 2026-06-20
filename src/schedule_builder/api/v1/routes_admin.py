from fastapi import APIRouter, Header

from schedule_builder.config.settings import settings
from schedule_builder.core.exceptions import ForbiddenError, UnauthorizedError

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
async def admin_ping(
    x_admin_token: str | None = Header(default=None),
) -> dict[str, str]:
    if not x_admin_token:
        raise UnauthorizedError(message="Missing admin token")

    if x_admin_token != settings.admin_api_token:
        raise ForbiddenError(message="Invalid admin token")

    return {"status": "ok", "message": "admin access granted"}
