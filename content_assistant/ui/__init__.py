"""Streamlit UI components for TheLifeCo Content Assistant."""

from content_assistant.ui.auth import (
    check_authentication,
    show_login_form,
    logout,
)
# NEW: EPA-based create mode (recommended)
from content_assistant.ui.epa_create_mode import render_epa_create_mode
# LEGACY: Old create mode (deprecated)
from content_assistant.ui.create_mode import render_create_mode as render_legacy_create_mode
from content_assistant.ui.review_mode import render_review_mode
from content_assistant.ui.history_sidebar import render_history_sidebar
from content_assistant.ui.monitoring import render_monitoring_dashboard

# Default render_create_mode now uses EPA
render_create_mode = render_epa_create_mode

__all__ = [
    # Auth
    "check_authentication",
    "show_login_form",
    "logout",
    # Modes
    "render_create_mode",  # Now uses EPA
    "render_epa_create_mode",
    "render_legacy_create_mode",
    "render_review_mode",
    # Sidebar
    "render_history_sidebar",
    # Monitoring
    "render_monitoring_dashboard",
]
