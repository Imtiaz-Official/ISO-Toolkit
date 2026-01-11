"""
Authentication routes for admin login/logout.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

from api.database.session import get_db
from api.database.models import User
from api.auth.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    create_refresh_token
)
from api.auth.rate_limiter import check_login_rate_limit

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Temporary reset key for admin password recovery (CHANGE IN PRODUCTION!)
RESET_SECRET_KEY = os.getenv("ADMIN_RESET_KEY", "reset-admin-2024-temp-key")

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        # Check for at least one uppercase, one lowercase, one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    is_active: bool
    password_changed: bool
    created_at: str
    last_login: Optional[str] = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


def get_client_ip(request: Request) -> str:
    """Get client IP address from request, handling proxy headers."""
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection IP
    if request.client:
        return request.client.host

    return "unknown"


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current authenticated admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.

    Uses OAuth2 password flow for compatibility with frontend libraries.
    Includes rate limiting to prevent brute force attacks.
    """
    # Get client IP for rate limiting
    client_ip = get_client_ip(request)

    # Check rate limit based on IP
    allowed, retry_after = check_login_rate_limit(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Rate limit on failed login (use username as key as well)
        check_login_rate_limit(f"{client_ip}:{form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens with 24 hour expiration
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict()
    )


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    Note: Regular users are not admins. Admin status must be set manually.
    Password must meet strength requirements.
    """
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with strong password hashing
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_admin=False,  # Default to regular user
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(**new_user.to_dict())


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    token_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh an access token using a refresh token.
    """
    from api.auth.auth_utils import decode_access_token
    payload = decode_access_token(token_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict()
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return UserResponse(**current_user.to_dict())


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    New password must meet strength requirements.
    Marks password as changed after successful update.
    """
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.password_changed = True
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout():
    """
    Logout endpoint. Since we use JWT tokens, the client should simply
    discard the token. This endpoint exists for API completeness and
    potential future server-side token blacklisting.
    """
    return {"message": "Successfully logged out"}


# Temporary admin password reset endpoint - USE ENVIRONMENT VARIABLE IN PRODUCTION!
@router.get("/reset-admin")
@router.post("/reset-admin")
async def reset_admin_password(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    ADMIN PASSWORD RESET - Requires secure key from environment.

    SECURITY: In production, set ADMIN_RESET_KEY environment variable to a
    strong random value. Without this, the endpoint uses a default key that
    is publicly known and should be changed immediately.

    Call with reset_key in query params: GET/POST /api/auth/reset-admin?reset_key=YOUR_KEY

    To generate a secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
    """
    reset_key = request.query_params.get("reset_key")

    # Check if using custom environment variable
    env_key = os.getenv("ADMIN_RESET_KEY")
    actual_key = env_key if env_key else RESET_SECRET_KEY

    if reset_key != actual_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid reset key"
        )

    # Find or create admin user
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("AdminPass123"),
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
    else:
        # Update password
        admin_user.hashed_password = get_password_hash("AdminPass123")
        admin_user.is_admin = True
        admin_user.is_active = True

    db.commit()

    return {
        "message": "Admin password reset successfully!",
        "username": "admin",
        "new_password": "AdminPass123",
        "note": "Please remove this endpoint after use for security"
    }


# Admin-only routes
@router.get("/admin/users", response_model=list[UserResponse])
async def list_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).
    """
    users = db.query(User).all()
    return [UserResponse(**user.to_dict()) for user in users]


@router.post("/admin/users/{user_id}/toggle-admin")
async def toggle_admin_status(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Toggle admin status for a user (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_admin = not user.is_admin
    db.commit()

    return {
        "message": f"User {user.username} admin status toggled to {user.is_admin}",
        "is_admin": user.is_admin
    }


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    username = user.username
    db.delete(user)
    db.commit()

    return {"message": f"User {username} deleted successfully"}
