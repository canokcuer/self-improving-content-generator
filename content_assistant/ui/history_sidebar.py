"""History sidebar for past generations.

Shows past content generations with ability to reload and reuse.

SECURITY NOTE: All database operations go through the API client
which enforces authentication via JWT tokens.
"""

import streamlit as st
from typing import Optional
import logging

from content_assistant.services.api_client import api_client
from content_assistant.utils.error_handler import safe_error_message

logger = logging.getLogger(__name__)


def render_history_sidebar() -> None:
    """Render the history sidebar."""
    st.sidebar.markdown("## History")

    # Get user's past generations
    user = st.session_state.get("user", {})
    user_id = user.get("id") if user else None

    if not user_id:
        st.sidebar.info("Log in to see your history.")
        return

    try:
        response = api_client.get_generations(limit=10)

        if not response.success:
            st.sidebar.error("Failed to load history")
            return

        generations = response.data or []

        if not generations:
            st.sidebar.info("No past generations yet.")
            return

        for gen in generations:
            _render_history_item(gen)

    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        st.sidebar.error("Failed to load history")


def _render_history_item(generation: dict) -> None:
    """Render a single history item."""
    gen_id = generation.get("id", "")
    platform = generation.get("platform", "unknown")
    rating = generation.get("rating")
    created = generation.get("created_at", "")[:10]  # Just date
    was_approved = generation.get("was_approved", False)

    # Get brief info
    brief = generation.get("brief", {})
    core_message = brief.get("core_message", "Untitled")[:50]

    # Create expandable item
    with st.sidebar.expander(f"{platform.title()} - {created}"):
        st.markdown(f"**{core_message}**")

        if rating:
            st.markdown(f"Rating: {'⭐' * rating}")

        if was_approved:
            st.markdown("✅ Approved")

        # Preview content
        content = generation.get("content", "")
        if content:
            st.markdown(content[:100] + "..." if len(content) > 100 else content)

        # Load button
        if st.button("Load", key=f"load_{gen_id}"):
            _load_generation(gen_id)


def _load_generation(generation_id: str) -> None:
    """Load a generation into the current session."""
    try:
        response = api_client.get_generation(generation_id)

        if response.success and response.data:
            # Store in session state for reference
            st.session_state.loaded_generation = response.data
            st.sidebar.success("Loaded! Check content in main area.")
        else:
            st.sidebar.error("Generation not found")

    except Exception as e:
        logger.error(f"Failed to load generation: {e}")
        st.sidebar.error("Failed to load")


def get_loaded_generation() -> Optional[dict]:
    """Get the currently loaded generation if any."""
    return st.session_state.get("loaded_generation")


def clear_loaded_generation() -> None:
    """Clear the loaded generation."""
    if "loaded_generation" in st.session_state:
        del st.session_state.loaded_generation
