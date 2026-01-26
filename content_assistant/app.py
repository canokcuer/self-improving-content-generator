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


def _get_logo_html(logo_path: Path, max_width: int = 400, centered: bool = False) -> str:
    """Get logo HTML without fullscreen icon."""
    import base64
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()

    align = "center" if centered else "left"
    return f'''
    <div style="text-align: {align}; margin-bottom: 1rem;">
        <img src="data:image/png;base64,{logo_data}" style="max-width: {max_width}px; width: 100%;">
    </div>
    '''


def main():
    """Main application entry point."""
    # Check authentication first
    if not check_authentication():
        # Show centered logo on login page (no fullscreen icon)
        if LOGO_PATH.exists():
            st.markdown(_get_logo_html(LOGO_PATH, max_width=400, centered=True), unsafe_allow_html=True)
        show_login_form()
        return

    # Logo in sidebar (after sign-in) - no fullscreen icon
    if LOGO_PATH.exists():
        st.sidebar.markdown(_get_logo_html(LOGO_PATH, max_width=250, centered=False), unsafe_allow_html=True)
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
