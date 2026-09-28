"""FastAPI dependencies for extracting and verifying authenticated Supabase user."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..schemas.auth import UserResponse
from ..services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[UserResponse]:
    """Extract authenticated user if token present and valid; otherwise None."""
    if not token:
        return None
    return await AuthService.get_user_from_token(token)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
) -> UserResponse:
    """Enforce authenticated user, raising HTTP 401 if missing or invalid."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await AuthService.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Require admin authorization, raising HTTP 403 if unauthorized."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this action",
        )
    return current_user
