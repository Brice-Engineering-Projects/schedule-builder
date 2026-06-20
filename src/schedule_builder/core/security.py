"""Security primitives shared across auth modules."""

from fastapi.security import OAuth2PasswordBearer

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
TOKEN_TYPE_BEARER = "bearer"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
