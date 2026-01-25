"""
Rate Limiting Middleware

Implements in-memory rate limiting per user.
Can be upgraded to Redis-based rate limiting for distributed deployments.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Optional
from fastapi import Depends, HTTPException, Request, status
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.

    For production with multiple instances, replace with Redis-based implementation.
    """

    def __init__(self):
        self._requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """
        Check if a request is within rate limits.

        Args:
            key: Unique identifier (user_id or IP)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed: bool, remaining: int)
        """
        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)

            # Remove expired entries
            self._requests[key] = [
                ts for ts in self._requests[key]
                if ts > window_start
            ]

            current_count = len(self._requests[key])
            remaining = max(0, max_requests - current_count)

            if current_count >= max_requests:
                return False, 0

            # Record this request
            self._requests[key].append(now)
            return True, remaining - 1

    async def cleanup_expired(self, max_age_seconds: int = 3600):
        """Remove entries older than max_age to prevent memory leaks."""
        async with self._lock:
            cutoff = datetime.utcnow() - timedelta(seconds=max_age_seconds)
            keys_to_remove = []

            for key, timestamps in self._requests.items():
                self._requests[key] = [ts for ts in timestamps if ts > cutoff]
                if not self._requests[key]:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._requests[key]


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_func: Optional[Callable[[Request], str]] = None,
):
    """
    Rate limiting dependency factory.

    Usage:
        @router.post("/chat", dependencies=[Depends(rate_limit(10, 60))])
        async def send_chat():
            ...

    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        key_func: Optional function to extract rate limit key from request
    """
    async def dependency(request: Request):
        # Get rate limit key (user_id if authenticated, else IP)
        user = getattr(request.state, "user", None)
        if key_func:
            key = key_func(request)
        elif user and hasattr(user, "user_id"):
            key = f"user:{user.user_id}"
        else:
            key = f"ip:{request.client.host if request.client else 'unknown'}"

        allowed, remaining = await _rate_limiter.check_rate_limit(
            key, max_requests, window_seconds
        )

        # Add rate limit headers
        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_limit = max_requests
        request.state.rate_limit_reset = window_seconds

        if not allowed:
            logger.warning(f"Rate limit exceeded for {key}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(window_seconds),
                },
            )

    return dependency


# Pre-configured rate limiters for common use cases
rate_limit_default = rate_limit(100, 60)  # 100 requests per minute
rate_limit_chat = rate_limit(10, 60)  # 10 chat messages per minute
rate_limit_generation = rate_limit(5, 60)  # 5 generations per minute
rate_limit_auth = rate_limit(5, 60)  # 5 auth attempts per minute
rate_limit_admin = rate_limit(50, 60)  # 50 admin requests per minute
