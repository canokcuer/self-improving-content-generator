"""
API Middleware Package

Contains middleware for:
- auth: JWT token validation and user extraction
- rate_limit: Request rate limiting per user
- audit: Request/response logging for audit trail
"""

from content_assistant.api.middleware.auth import get_current_user, require_admin, AuthenticatedUser
from content_assistant.api.middleware.audit import AuditLogMiddleware, setup_audit_logging

__all__ = [
    "get_current_user",
    "require_admin",
    "AuthenticatedUser",
    "AuditLogMiddleware",
    "setup_audit_logging",
]
