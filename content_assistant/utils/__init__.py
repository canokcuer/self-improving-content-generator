"""
Utilities Package

Contains utility functions for:
- sanitizer: Input sanitization and validation
- error_handler: Safe error handling without exposing internals
"""

from content_assistant.utils.sanitizer import (
    sanitize_html,
    sanitize_like_pattern,
    validate_email,
    validate_uuid,
    validate_password,
    sanitize_filename,
    sanitize_search_query,
)

from content_assistant.utils.error_handler import (
    handle_error,
    safe_error_message,
    ErrorType,
    SafeError,
    SafeErrorContext,
)

__all__ = [
    # Sanitization
    "sanitize_html",
    "sanitize_like_pattern",
    "validate_email",
    "validate_uuid",
    "validate_password",
    "sanitize_filename",
    "sanitize_search_query",
    # Error handling
    "handle_error",
    "safe_error_message",
    "ErrorType",
    "SafeError",
    "SafeErrorContext",
]
