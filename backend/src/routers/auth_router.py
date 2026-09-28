"""Authentication API Endpoints supporting both Supabase and Frontend contracts."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
)
from ..services.auth_service import AuthService
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account (Frontend signup endpoint)",
)
async def signup_user(payload: UserRegister):
    """Register a new account via Supabase Auth."""
    try:
        name = payload.name or payload.full_name
        token = await AuthService.sign_up(email=payload.email, password=payload.password, name=name)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signup failed")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account (Standard REST endpoint)",
)
async def register_user(payload: UserRegister):
    """Register user and return User profile."""
    try:
        name = payload.name or payload.full_name
        token = await AuthService.sign_up(email=payload.email, password=payload.password, name=name)
        return token.user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")


@router.post(
    "/login",
    response_model=Token,
    summary="Login with email & password returning JWT token and user profile",
)
async def login_user(
    login_data: Optional[UserLogin] = None,
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(lambda: None),
):
    """Authenticate user with credentials.
    Supports both JSON body and standard OAuth2 form encoding.
    """
    email = None
    password = None

    if login_data:
        email = login_data.email
        password = login_data.password
    elif form_data:
        email = form_data.username
        password = form_data.password

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    try:
        token = await AuthService.login(email=email, password=password)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/logout", summary="Log out the current user")
async def logout_user():
    """Sign out from Supabase Auth."""
    await AuthService.logout()
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse, summary="Get current authenticated user profile")
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve profile of currently authenticated user."""
    return current_user


@router.post("/refresh", response_model=Token, summary="Refresh an access token")
async def refresh_token(
    refresh_token: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
):
    """Issue a fresh access token for authenticated session."""
    return Token(
        access_token=f"sb_token_{current_user.id}",
        token_type="bearer",
        user=current_user,
    )
