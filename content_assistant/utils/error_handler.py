"""
Error Handling Utilities

Provides safe error handling that doesn't expose internal details to users.
All sensitive information is logged server-side while users see generic messages.
"""

import logging
import traceback
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Categorized error types for user-friendly messages."""
    AUTH_FAILED = "auth_failed"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMITED = "rate_limited"
    SERVER_ERROR = "server_error"
    DATABASE_ERROR = "database_error"
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    CONFIGURATION_ERROR = "configuration_error"


# User-safe error messages (no internal details)
ERROR_MESSAGES = {
    ErrorType.AUTH_FAILED: "Authentication failed. Please check your credentials and try again.",
    ErrorType.PERMISSION_DENIED: "You don't have permission to perform this action.",
    ErrorType.NOT_FOUND: "The requested resource was not found.",
    ErrorType.VALIDATION_ERROR: "Invalid input. Please check your data and try again.",
    ErrorType.RATE_LIMITED: "Too many requests. Please wait a moment and try again.",
    ErrorType.SERVER_ERROR: "An unexpected error occurred. Please try again later.",
    ErrorType.DATABASE_ERROR: "Unable to complete the operation. Please try again.",
    ErrorType.NETWORK_ERROR: "Network error. Please check your connection and try again.",
    ErrorType.API_ERROR: "Service temporarily unavailable. Please try again later.",
    ErrorType.CONFIGURATION_ERROR: "System configuration error. Please contact support.",
}


def handle_error(
    error: Exception,
    error_type: ErrorType = ErrorType.SERVER_ERROR,
    log_details: bool = True,
    context: Optional[str] = None,
) -> str:
    """
    Handle an error safely: log details internally, return safe message to user.

    Args:
        error: The exception that occurred
        error_type: Category of error for user message
        log_details: Whether to log full error details
        context: Optional context string for logging

    Returns:
        User-safe error message

    Example:
        try:
            result = risky_operation()
        except DatabaseError as e:
            st.error(handle_error(e, ErrorType.DATABASE_ERROR))
    """
    if log_details:
        log_message = f"{error_type.value}"
        if context:
            log_message += f" [{context}]"
        log_message += f": {error}"

        logger.error(log_message)
        logger.debug(f"Traceback:\n{traceback.format_exc()}")

    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES[ErrorType.SERVER_ERROR])


def safe_error_message(error: Exception) -> str:
    """
    Convert any exception to a safe user-facing message.

    Automatically categorizes common exception types.

    Args:
        error: Any exception

    Returns:
        User-safe error message
    """
    error_name = type(error).__name__.lower()

    # Map exception types to error categories
    if "auth" in error_name or "token" in error_name or "credential" in error_name:
        return handle_error(error, ErrorType.AUTH_FAILED)
    elif "permission" in error_name or "forbidden" in error_name or "authorization" in error_name:
        return handle_error(error, ErrorType.PERMISSION_DENIED)
    elif "notfound" in error_name or "404" in str(error):
        return handle_error(error, ErrorType.NOT_FOUND)
    elif "validation" in error_name or "invalid" in error_name:
        return handle_error(error, ErrorType.VALIDATION_ERROR)
    elif "ratelimit" in error_name or "429" in str(error):
        return handle_error(error, ErrorType.RATE_LIMITED)
    elif "database" in error_name or "sql" in error_name or "postgres" in error_name:
        return handle_error(error, ErrorType.DATABASE_ERROR)
    elif "connection" in error_name or "network" in error_name or "timeout" in error_name:
        return handle_error(error, ErrorType.NETWORK_ERROR)
    elif "api" in error_name:
        return handle_error(error, ErrorType.API_ERROR)
    else:
        return handle_error(error, ErrorType.SERVER_ERROR)


class SafeErrorContext:
    """
    Context manager for handling errors safely.

    Usage:
        with SafeErrorContext(ErrorType.DATABASE_ERROR, "creating user"):
            db.create_user(data)

    If an exception occurs, it's logged with context and re-raised
    as a SafeError with a user-friendly message.
    """

    def __init__(
        self,
        error_type: ErrorType = ErrorType.SERVER_ERROR,
        context: Optional[str] = None,
    ):
        self.error_type = error_type
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            safe_message = handle_error(exc_val, self.error_type, context=self.context)
            # Log but don't suppress the exception
            # The caller can catch and display safe_message
            return False  # Re-raise the exception


class SafeError(Exception):
    """
    An exception with a user-safe message.

    Use this when you need to raise an exception that will be shown to users.
    """

    def __init__(self, user_message: str, internal_message: Optional[str] = None):
        self.user_message = user_message
        self.internal_message = internal_message or user_message
        super().__init__(self.internal_message)

        # Log the internal message
        if internal_message:
            logger.error(f"SafeError: {internal_message}")

    def __str__(self):
        return self.user_message
