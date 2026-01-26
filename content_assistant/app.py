"""Main Streamlit application entry point.

Self-Improving Content Generator for TLC - AI-powered content generation.
"""

import sys
from pathlib import Path

# Add parent directory to path for Streamlit Cloud
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Self-Improving Content Generator for TLC",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Get logo path
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

from content_assistant.ui.auth import check_authentication, show_login_form, logout  # noqa: E402
from content_assistant.ui.epa_create_mode import render_epa_create_mode as render_create_mode  # noqa: E402
from content_assistant.ui.review_mode import render_review_mode  # noqa: E402
from content_assistant.ui.history_sidebar import render_history_sidebar  # noqa: E402
from content_assistant.ui.monitoring import render_monitoring_dashboard  # noqa: E402


def main():
    """Main application entry point."""
    # Check authentication first
    if not check_authentication():
        # Show logo and title on login page
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=350)
        st.markdown("### Self-Improving Content Generator for TLC")
        st.markdown("*AI-powered content assistant for wellness marketing*")
        show_login_form()
        return

    # Logo in sidebar (after sign-in) - use full container width for quality
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)
        st.sidebar.divider()

    # User info and logout in sidebar
    user = st.session_state.get("user", {})
    st.sidebar.markdown(f"**Logged in as:** {user.get('email', 'User')}")
    if st.sidebar.button("Logout"):
        logout()
        return

    st.sidebar.divider()

    # Mode selection
    mode = st.sidebar.radio(
        "Mode",
        ["CREATE", "REVIEW", "MONITOR"],
        help="CREATE: Generate content | REVIEW: Analyze content | MONITOR: View stats",
    )

    st.sidebar.divider()

    # Render history sidebar only in REVIEW mode
    # CREATE mode has its own conversation sidebar
    if mode == "REVIEW":
        render_history_sidebar()

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

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("v0.1.0 | TLC Content Generator")
    st.sidebar.markdown("[Report Issue](https://github.com/thelifeco/content-assistant/issues)")


if __name__ == "__main__":
    main()
