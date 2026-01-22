"""History sidebar for past generations.

Shows past content generations with ability to reload and reuse.
"""

import streamlit as st
from typing import Optional

from content_assistant.review.signals import get_user_generations, get_generation_by_id


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
        generations = get_user_generations(user_id, limit=10)

        if not generations:
            st.sidebar.info("No past generations yet.")
            return

        for gen in generations:
            _render_history_item(gen)

    except Exception as e:
        st.sidebar.error(f"Failed to load history: {e}")


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
        generation = get_generation_by_id(generation_id)

        if generation:
            # Store in session state for reference
            st.session_state.loaded_generation = generation
            st.sidebar.success("Loaded! Check content in main area.")

    except Exception as e:
        st.sidebar.error(f"Failed to load: {e}")


def get_loaded_generation() -> Optional[dict]:
    """Get the currently loaded generation if any."""
    return st.session_state.get("loaded_generation")


def clear_loaded_generation() -> None:
    """Clear the loaded generation."""
    if "loaded_generation" in st.session_state:
        del st.session_state.loaded_generation
