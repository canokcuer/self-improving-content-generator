"""
Authentication Middleware

Validates Supabase JWT tokens and extracts user information.
All protected endpoints should use get_current_user as a dependency.
"""

from dataclasses import dataclass
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
import logging

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()

# JWT configuration
JWT_ALGORITHM = "HS256"


@dataclass
class AuthenticatedUser:
    """Represents an authenticated user extracted from JWT."""
    user_id: str
    email: Optional[str]
    role: str
    access_token: str
    refresh_token: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        return bool(self.user_id)


def _get_jwt_secret() -> str:
    """Get JWT secret from environment."""
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        logger.error("SUPABASE_JWT_SECRET not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication configuration error",
        )
    return secret


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthenticatedUser:
    """
    Validate JWT token and extract user information.

    This dependency should be used on all protected endpoints.
    It validates the Supabase JWT and extracts user_id, email, and role.

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    token = credentials.credentials

    try:
        # Decode and validate the JWT
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[JWT_ALGORITHM],
            audience="authenticated",
        )

        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "authenticated")

        if not user_id:
            logger.warning("JWT token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return AuthenticatedUser(
            user_id=user_id,
            email=email,
            role=role,
            access_token=token,
        )

    except jwt.ExpiredSignatureError:
        logger.info(f"Expired token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"Invalid JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Dependency that requires admin role.

    Use this on admin-only endpoints like cost monitoring.
    Checks the user_roles table to verify admin status.

    Raises:
        HTTPException: 403 if user is not an admin
    """
    # For now, check if role is service_role (will be enhanced with user_roles table lookup)
    # TODO: Query user_roles table to check for admin role

    from content_assistant.api.dependencies import get_admin_client

    try:
        client = get_admin_client()
        result = client.table("user_roles")\
            .select("role")\
            .eq("user_id", user.user_id)\
            .eq("role", "admin")\
            .execute()

        if not result.data:
            logger.warning(f"Non-admin user {user.user_id} attempted admin access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to verify admin status",
        )
