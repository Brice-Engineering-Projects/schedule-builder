"""Authentication API routes."""

from fastapi import APIRouter, Depends

from schedule_builder.auth.dependencies import get_auth_service, get_current_user
from schedule_builder.auth.schemas import AuthResponse, LoginRequest, RegisterRequest, UserPublic
from schedule_builder.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=201)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    return service.register_user(payload)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return service.login_user(payload)


@router.get("/me", response_model=UserPublic)
async def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return current_user
