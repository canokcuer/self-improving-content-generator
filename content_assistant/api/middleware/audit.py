"""
Audit Logging Middleware

Logs all API requests for security monitoring and compliance.
Sensitive data is masked in logs.
"""

import time
import logging
import json
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

logger = logging.getLogger("audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all API requests with security-relevant details.

    Logs include:
    - Timestamp
    - User ID (from JWT)
    - Method and path
    - Status code
    - Response time
    - Client IP

    Sensitive data (passwords, tokens, etc.) is masked.
    """

    SENSITIVE_PATHS = [
        "/api/auth",
        "/api/admin",
    ]

    SENSITIVE_FIELDS = [
        "password",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "authorization",
    ]

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and log audit information."""
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_id = self._get_user_id(request)

        # Process the request
        response = await call_next(request)

        # Calculate response time
        duration_ms = (time.time() - start_time) * 1000

        # Build audit log entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": client_ip,
            "user_id": user_id,
        }

        # Add query params (masked)
        if request.query_params:
            audit_entry["query_params"] = self._mask_sensitive(
                dict(request.query_params)
            )

        # Log based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(audit_entry))
        elif response.status_code >= 400:
            logger.warning(json.dumps(audit_entry))
        else:
            logger.info(json.dumps(audit_entry))

        # Log to database for sensitive paths (admin operations)
        if any(path.startswith(p) for p in self.SENSITIVE_PATHS):
            await self._log_to_database(audit_entry)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        # Check for forwarded headers (reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request state (set by auth middleware)."""
        # Auth middleware should set this
        if hasattr(request.state, "user"):
            user = request.state.user
            if hasattr(user, "user_id"):
                return user.user_id
        return None

    def _mask_sensitive(self, data: dict) -> dict:
        """Mask sensitive fields in a dictionary."""
        masked = {}
        for key, value in data.items():
            if any(s in key.lower() for s in self.SENSITIVE_FIELDS):
                masked[key] = "[REDACTED]"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive(value)
            else:
                masked[key] = value
        return masked

    async def _log_to_database(self, audit_entry: dict) -> None:
        """Log sensitive operations to database for compliance."""
        try:
            # Import here to avoid circular imports
            from content_assistant.db.supabase_client import get_admin_client

            client = get_admin_client()
            client.table("audit_logs").insert({
                "timestamp": audit_entry["timestamp"],
                "user_id": audit_entry.get("user_id"),
                "action": f"{audit_entry['method']} {audit_entry['path']}",
                "status_code": audit_entry["status_code"],
                "client_ip": audit_entry["client_ip"],
                "details": {
                    "duration_ms": audit_entry["duration_ms"],
                    "query_params": audit_entry.get("query_params"),
                },
            }).execute()
        except Exception as e:
            # Don't fail request on audit logging errors
            logger.error(f"Failed to log audit to database: {e}")


def setup_audit_logging():
    """Configure audit logging handlers."""
    # Create audit logger
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)

    # Create file handler for audit logs
    try:
        import os
        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_path = os.path.join(log_dir, "logs", "audit.log")

        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)

        # Use JSON format for easy parsing
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)

        audit_logger.addHandler(file_handler)

    except Exception as e:
        # Fall back to console logging
        logging.warning(f"Could not set up audit file logging: {e}")
