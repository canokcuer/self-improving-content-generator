"""
API Client Service

Provides a secure HTTP client for the Streamlit frontend to communicate
with the FastAPI backend. All database operations should go through this
client instead of direct Supabase calls.
"""

from dataclasses import dataclass
from typing import Any, Optional, Dict, List
import httpx
import streamlit as st
import os
import logging
from datetime import date

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standardized API response wrapper."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: int = 200


class APIClient:
    """
    HTTP client for communicating with the FastAPI backend.

    All methods return APIResponse objects with success/error status.
    The client automatically includes the user's JWT token for authentication.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API. Defaults to environment variable
                      or localhost:8000.
        """
        self.base_url = base_url or os.getenv("API_URL", "http://localhost:8000")
        self._timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including auth token."""
        headers = {"Content-Type": "application/json"}

        # Get token from Streamlit session state
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _handle_response(self, response: httpx.Response) -> APIResponse:
        """Convert HTTP response to APIResponse."""
        try:
            if response.status_code == 401:
                return APIResponse(
                    success=False,
                    error="Session expired. Please login again.",
                    status_code=401,
                )
            if response.status_code == 403:
                return APIResponse(
                    success=False,
                    error="Permission denied.",
                    status_code=403,
                )
            if response.status_code == 404:
                return APIResponse(
                    success=False,
                    error="Resource not found.",
                    status_code=404,
                )
            if response.status_code == 429:
                return APIResponse(
                    success=False,
                    error="Too many requests. Please wait a moment.",
                    status_code=429,
                )
            if response.status_code >= 500:
                return APIResponse(
                    success=False,
                    error="Server error. Please try again.",
                    status_code=response.status_code,
                )

            response.raise_for_status()

            # Handle empty responses (204 No Content)
            if response.status_code == 204:
                return APIResponse(success=True, data=None, status_code=204)

            return APIResponse(
                success=True,
                data=response.json(),
                status_code=response.status_code,
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return APIResponse(
                success=False,
                error=f"Request failed: {e.response.status_code}",
                status_code=e.response.status_code,
            )
        except Exception as e:
            logger.error(f"Request error: {e}")
            return APIResponse(
                success=False,
                error="Network error. Please check your connection.",
                status_code=0,
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> APIResponse:
        """Make a synchronous HTTP request."""
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.request(
                    method=method,
                    url=f"{self.base_url}{endpoint}",
                    headers=self._get_headers(),
                    params=params,
                    json=json,
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return APIResponse(
                success=False,
                error="Unable to connect to server. Please try again.",
                status_code=0,
            )

    # ============================================
    # Conversation Methods
    # ============================================

    def get_conversations(self, limit: int = 20, offset: int = 0) -> APIResponse:
        """Get list of user's conversations."""
        return self._request(
            "GET",
            "/api/conversations",
            params={"limit": limit, "offset": offset},
        )

    def get_conversation(self, conversation_id: str) -> APIResponse:
        """Get a specific conversation by ID."""
        return self._request("GET", f"/api/conversations/{conversation_id}")

    def create_conversation(self, title: Optional[str] = None) -> APIResponse:
        """Create a new conversation."""
        return self._request(
            "POST",
            "/api/conversations",
            json={"title": title},
        )

    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
    ) -> APIResponse:
        """Update a conversation's metadata."""
        data = {}
        if title is not None:
            data["title"] = title
        if status is not None:
            data["status"] = status

        return self._request(
            "PUT",
            f"/api/conversations/{conversation_id}",
            json=data,
        )

    def delete_conversation(self, conversation_id: str) -> APIResponse:
        """Delete a conversation."""
        return self._request("DELETE", f"/api/conversations/{conversation_id}")

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> APIResponse:
        """Add a message to a conversation."""
        return self._request(
            "POST",
            f"/api/conversations/{conversation_id}/messages",
            json={"role": role, "content": content},
        )

    # ============================================
    # Generation Methods
    # ============================================

    def get_generations(
        self,
        limit: int = 20,
        offset: int = 0,
        platform: Optional[str] = None,
        min_rating: Optional[int] = None,
    ) -> APIResponse:
        """Get list of user's generations."""
        params = {"limit": limit, "offset": offset}
        if platform:
            params["platform"] = platform
        if min_rating:
            params["min_rating"] = min_rating

        return self._request("GET", "/api/generations", params=params)

    def get_generation(self, generation_id: str) -> APIResponse:
        """Get a specific generation by ID."""
        return self._request("GET", f"/api/generations/{generation_id}")

    def create_generation(
        self,
        brief: Dict[str, Any],
        content: str,
        platform: Optional[str] = None,
        preview: Optional[Dict] = None,
        conversation_id: Optional[str] = None,
    ) -> APIResponse:
        """Create a new generation record."""
        data = {
            "brief": brief,
            "content": content,
        }
        if platform:
            data["platform"] = platform
        if preview:
            data["preview"] = preview
        if conversation_id:
            data["conversation_id"] = conversation_id

        return self._request("POST", "/api/generations", json=data)

    def update_generation(
        self,
        generation_id: str,
        rating: Optional[int] = None,
        feedback: Optional[str] = None,
        was_approved: Optional[bool] = None,
    ) -> APIResponse:
        """Update a generation's signals."""
        data = {}
        if rating is not None:
            data["rating"] = rating
        if feedback is not None:
            data["feedback"] = feedback
        if was_approved is not None:
            data["was_approved"] = was_approved

        return self._request(
            "PUT",
            f"/api/generations/{generation_id}",
            json=data,
        )

    def delete_generation(self, generation_id: str) -> APIResponse:
        """Delete a generation."""
        return self._request("DELETE", f"/api/generations/{generation_id}")

    def get_generation_stats(self) -> APIResponse:
        """Get user's generation statistics."""
        return self._request("GET", "/api/generations/stats")

    # ============================================
    # Admin Methods
    # ============================================

    def check_admin_status(self) -> APIResponse:
        """Check if current user is an admin."""
        return self._request("GET", "/api/admin/check-status")

    def get_admin_costs(self, start_date: date, end_date: date) -> APIResponse:
        """Get cost report (admin only)."""
        return self._request(
            "GET",
            "/api/admin/costs",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

    def get_admin_stats(self) -> APIResponse:
        """Get admin dashboard statistics (admin only)."""
        return self._request("GET", "/api/admin/stats")

    def get_admin_users(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """Get list of users (admin only)."""
        return self._request(
            "GET",
            "/api/admin/users",
            params={"limit": limit, "offset": offset},
        )


# Global singleton instance
api_client = APIClient()
