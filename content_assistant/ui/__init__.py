"""Streamlit UI components for TheLifeCo Content Assistant."""

from content_assistant.ui.auth import (
    check_authentication,
    show_login_form,
    logout,
)
from content_assistant.ui.create_mode import render_create_mode
from content_assistant.ui.review_mode import render_review_mode
from content_assistant.ui.history_sidebar import render_history_sidebar
from content_assistant.ui.monitoring import render_monitoring_dashboard

__all__ = [
    # Auth
    "check_authentication",
    "show_login_form",
    "logout",
    # Modes
    "render_create_mode",
    "render_review_mode",
    # Sidebar
    "render_history_sidebar",
    # Monitoring
    "render_monitoring_dashboard",
]
