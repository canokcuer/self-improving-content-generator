"""
Services Package

Contains service clients for the Streamlit frontend:
- api_client: HTTP client for communicating with the FastAPI backend
"""

from content_assistant.services.api_client import api_client, APIClient, APIResponse

__all__ = ["api_client", "APIClient", "APIResponse"]
