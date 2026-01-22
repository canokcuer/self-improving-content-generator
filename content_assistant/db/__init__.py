"""Database layer for Supabase operations."""

from content_assistant.db.supabase_client import (
    get_client,
    get_admin_client,
    clear_client_cache,
    check_connection,
    DatabaseError,
)

__all__ = [
    "get_client",
    "get_admin_client",
    "clear_client_cache",
    "check_connection",
    "DatabaseError",
]
