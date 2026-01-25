"""
Input Sanitization Utilities

Provides functions to sanitize and validate user inputs to prevent:
- XSS (Cross-Site Scripting)
- SQL Injection (via LIKE pattern escaping)
- Invalid data formats
"""

import html
import re
from typing import Tuple


def sanitize_html(text: str, max_length: int = 50000) -> str:
    """
    Escape HTML special characters and enforce length limit.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length (default 50000)

    Returns:
        Sanitized text with HTML entities escaped

    Example:
        >>> sanitize_html("<script>alert('xss')</script>")
        "&lt;script&gt;alert('xss')&lt;/script&gt;"
    """
    if not text:
        return ""

    # Truncate to max length first
    text = text[:max_length]

    # Escape HTML special characters
    return html.escape(text)


def sanitize_like_pattern(pattern: str) -> str:
    """
    Escape SQL LIKE pattern special characters.

    Prevents SQL injection via LIKE patterns by escaping
    % and _ characters that have special meaning.

    Args:
        pattern: Input pattern to sanitize

    Returns:
        Pattern with LIKE special characters escaped

    Example:
        >>> sanitize_like_pattern("%admin%")
        "\\%admin\\%"
    """
    if not pattern:
        return ""

    # Escape LIKE special characters
    # Order matters: escape backslash first
    pattern = pattern.replace("\\", "\\\\")
    pattern = pattern.replace("%", "\\%")
    pattern = pattern.replace("_", "\\_")

    return pattern


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_email("user@example.com")
        (True, "")
        >>> validate_email("invalid")
        (False, "Invalid email format")
    """
    if not email:
        return False, "Email is required"

    if len(email) > 254:
        return False, "Email too long (max 254 characters)"

    # RFC 5322 simplified pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, ""


def validate_uuid(value: str) -> bool:
    """
    Validate UUID format.

    Args:
        value: String to validate as UUID

    Returns:
        True if valid UUID format, False otherwise

    Example:
        >>> validate_uuid("550e8400-e29b-41d4-a716-446655440000")
        True
        >>> validate_uuid("not-a-uuid")
        False
    """
    if not value:
        return False

    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, str(value).lower()))


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_password("abc123")
        (False, "Password must be at least 12 characters")
        >>> validate_password("SecureP@ssw0rd!")
        (True, "")
    """
    if not password:
        return False, "Password is required"

    if len(password) < 12:
        return False, "Password must be at least 12 characters"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    # Check for common weak passwords
    common_passwords = [
        "password12345",
        "qwerty123456",
        "123456789012",
        "admin1234567",
    ]
    if password.lower() in common_passwords:
        return False, "Password is too common"

    return True, ""


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.

    Args:
        filename: Original filename
        max_length: Maximum allowed length

    Returns:
        Safe filename with dangerous characters removed
    """
    if not filename:
        return ""

    # Remove path separators and dangerous characters
    filename = re.sub(r'[/\\:*?"<>|]', '_', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Truncate
    filename = filename[:max_length]

    return filename


def sanitize_search_query(query: str, max_length: int = 500) -> str:
    """
    Sanitize a search query.

    Args:
        query: Search query to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized query safe for use in searches
    """
    if not query:
        return ""

    # Truncate
    query = query[:max_length]

    # Remove potentially dangerous characters but keep basic punctuation
    query = re.sub(r'[<>"\';]', '', query)

    # Normalize whitespace
    query = ' '.join(query.split())

    return query
