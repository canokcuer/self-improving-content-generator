"""
TheLifeCo Content Assistant - Secure API Layer

This module provides a FastAPI-based backend that enforces:
- JWT authentication via Supabase tokens
- Rate limiting per user
- Input validation via Pydantic
- Audit logging for all operations
- Role-based access control for admin features

The API acts as the secure gateway between the Streamlit frontend
and the Supabase database, ensuring all access respects RLS policies.
"""

from content_assistant.api.main import app

__all__ = ["app"]
