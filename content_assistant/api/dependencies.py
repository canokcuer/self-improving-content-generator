"""
Shared Dependencies for API Routes

This module provides common dependencies used across API endpoints:
- Database client access (authenticated, respects RLS)
- Current user extraction from JWT
- Common query parameters
"""

from typing import Optional
from fastapi import Depends, HTTPException, Query
from supabase import create_client, Client
import os

from content_assistant.api.middleware.auth import get_current_user, AuthenticatedUser


def get_authenticated_client(user: AuthenticatedUser = Depends(get_current_user)) -> Client:
    """
    Get a Supabase client authenticated as the current user.

    This client respects RLS policies, so users can only access their own data.
    The user's JWT token is used for authentication.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")  # Anon key, NOT service key

    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=500, detail="Database configuration error")

    client = create_client(supabase_url, supabase_key)

    # Set the user's JWT token for RLS
    # This ensures all queries respect row-level security
    client.auth.set_session(user.access_token, user.refresh_token or "")

    return client


def get_admin_client() -> Client:
    """
    Get a Supabase client with service role (bypasses RLS).

    WARNING: Only use this for admin operations that have been
    explicitly authorized via role checks.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Admin configuration error")

    return create_client(supabase_url, service_key)


class PaginationParams:
    """Common pagination parameters for list endpoints."""

    def __init__(
        self,
        limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
        offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    ):
        self.limit = limit
        self.offset = offset


def pagination_params(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginationParams:
    """Dependency for pagination parameters."""
    return PaginationParams(limit=limit, offset=offset)
