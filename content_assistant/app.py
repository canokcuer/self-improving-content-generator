"""Main Streamlit application entry point.

TheLifeCo Content Marketing Assistant - Self-improving AI content generation.
"""

import sys
from pathlib import Path

# Add parent directory to path for Streamlit Cloud
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="TheLifeCo Content Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

from content_assistant.ui.auth import check_authentication, show_login_form, logout  # noqa: E402
from content_assistant.ui.create_mode import render_create_mode  # noqa: E402
from content_assistant.ui.review_mode import render_review_mode  # noqa: E402
from content_assistant.ui.history_sidebar import render_history_sidebar  # noqa: E402
from content_assistant.ui.monitoring import render_monitoring_dashboard  # noqa: E402
from content_assistant.ui.styles import inject_custom_css, get_logo_path  # noqa: E402


def main():
    """Main application entry point."""
    # Inject custom CSS
    inject_custom_css()

    # Check authentication first
    if not check_authentication():
        show_login_form()
        return

    # Sidebar content for authenticated users
    with st.sidebar:
        # Logo and branding
        logo_path = get_logo_path()
        if logo_path.exists():
            st.image(str(logo_path), width=180)
        st.markdown("---")

        # User info
        user = st.session_state.get("user", {})
        st.markdown(f"**{user.get('email', 'User')}**")

        if st.button("Sign Out", use_container_width=True):
            logout()
            return

        st.markdown("---")

        # Mode selection with icons
        mode = st.radio(
            "Mode",
            ["CREATE", "REVIEW", "MONITOR"],
            format_func=lambda x: {
                "CREATE": "✨ Create",
                "REVIEW": "📝 Review",
                "MONITOR": "📊 Monitor"
            }.get(x, x),
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Render history sidebar (except in monitor mode)
        if mode != "MONITOR":
            render_history_sidebar()

        # Footer
        st.markdown("---")
        st.caption("v0.1.0 · TheLifeCo")

    # Main content area
    # Header
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h1 style="font-size: 1.75rem; font-weight: 600; margin-bottom: 0.25rem;">
                Content Assistant
            </h1>
            <p style="color: #6B7280; font-size: 0.875rem;">
                AI-powered content creation for wellness marketing
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Main content area with error handling
    try:
        if mode == "CREATE":
            render_create_mode()
        elif mode == "REVIEW":
            render_review_mode()
        else:
            render_monitoring_dashboard()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("Please try refreshing the page or contact support if the issue persists.")

        # Debug info in expander
        with st.expander("Error Details"):
            st.exception(e)


if __name__ == "__main__":
    main()
