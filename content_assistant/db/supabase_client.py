"""Supabase client module for database operations.

Provides two client types:
- Regular client: Uses anon key, respects Row Level Security (RLS)
- Admin client: Uses service key, bypasses RLS for admin operations
"""

from functools import lru_cache
from typing import Optional

from supabase import create_client, Client

from content_assistant.config import get_config


class DatabaseError(Exception):
    """Raised when database operations fail."""

    pass


@lru_cache(maxsize=1)
def get_client() -> Client:
    """Get the regular Supabase client (respects RLS).

    Use this for user-facing operations where Row Level Security
    should be enforced.

    Returns:
        Client: Supabase client instance

    Raises:
        DatabaseError: If client creation fails
    """
    try:
        config = get_config()
        return create_client(config.supabase_url, config.supabase_key)
    except Exception as e:
        raise DatabaseError(f"Failed to create Supabase client: {e}") from e


@lru_cache(maxsize=1)
def get_admin_client() -> Client:
    """Get the admin Supabase client (bypasses RLS).

    Use this for admin operations that need to bypass Row Level Security,
    such as:
    - Embedding knowledge base documents
    - System-level data management
    - Background processing tasks

    Returns:
        Client: Supabase admin client instance

    Raises:
        DatabaseError: If client creation fails
    """
    try:
        config = get_config()
        return create_client(config.supabase_url, config.supabase_service_key)
    except Exception as e:
        raise DatabaseError(f"Failed to create Supabase admin client: {e}") from e


def clear_client_cache():
    """Clear both client caches. Useful for testing."""
    get_client.cache_clear()
    get_admin_client.cache_clear()


def check_connection(client: Optional[Client] = None) -> bool:
    """Check if the Supabase connection is working.

    Args:
        client: Optional client to test. If None, uses regular client.

    Returns:
        bool: True if connection is healthy

    Raises:
        DatabaseError: If connection check fails
    """
    try:
        if client is None:
            client = get_client()
        # Try a simple query to verify connection
        # This will fail gracefully if the table doesn't exist yet
        client.table("knowledge_chunks").select("id").limit(1).execute()
        return True
    except Exception as e:
        # Connection might work but table doesn't exist yet - that's okay
        error_str = str(e).lower()
        if "does not exist" in error_str or "relation" in error_str:
            return True
        raise DatabaseError(f"Connection check failed: {e}") from e
