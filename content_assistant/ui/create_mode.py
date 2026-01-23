"""CREATE mode UI for content generation.

Provides a conversational chat interface for:
- Multi-agent content briefing
- Preview generation and approval
- Full content generation
- Feedback collection
"""

import streamlit as st
from typing import Optional

from content_assistant.agents import (
    AgentCoordinator,
    AgentStage,
    CoordinatorState,
)
from content_assistant.db.conversations import (
    create_conversation,
    get_conversation,
    update_conversation,
    get_user_conversations,
    add_message_to_conversation,
    ConversationError,
)


# Stage display names and icons
STAGE_INFO = {
    AgentStage.ORCHESTRATOR: {
        "name": "Briefing",
        "icon": "clipboard",
        "description": "Understanding your content needs",
    },
    AgentStage.WELLNESS: {
        "name": "Verification",
        "icon": "check-circle",
        "description": "Verifying facts and gathering information",
    },
    AgentStage.STORYTELLING_PREVIEW: {
        "name": "Preview",
        "icon": "eye",
        "description": "Creating content preview",
    },
    AgentStage.STORYTELLING_CONTENT: {
        "name": "Content",
        "icon": "file-text",
        "description": "Generating full content",
    },
    AgentStage.REVIEW: {
        "name": "Review",
        "icon": "star",
        "description": "Collecting your feedback",
    },
    AgentStage.COMPLETE: {
        "name": "Complete",
        "icon": "check",
        "description": "Content generation complete",
    },
}


def _initialize_session_state() -> None:
    """Initialize all session state variables."""
    if "coordinator" not in st.session_state:
        st.session_state.coordinator = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "current_preview" not in st.session_state:
        st.session_state.current_preview = None
    if "current_content" not in st.session_state:
        st.session_state.current_content = None
    if "processing" not in st.session_state:
        st.session_state.processing = False


def _get_or_create_coordinator() -> AgentCoordinator:
    """Get existing coordinator or create new one."""
    if st.session_state.coordinator is None:
        def on_stage_change(new_stage: AgentStage):
            # Update UI when stage changes
            pass

        st.session_state.coordinator = AgentCoordinator(
            on_stage_change=on_stage_change
        )
    return st.session_state.coordinator


def _get_user_id() -> Optional[str]:
    """Get current user ID from session."""
    user = st.session_state.get("user", {})
    return user.get("id") if user else None


def _add_message(role: str, content: str, agent: Optional[str] = None) -> None:
    """Add a message to the chat history."""
    message = {
        "role": role,
        "content": content,
        "agent": agent,
    }
    st.session_state.chat_messages.append(message)

    # Also save to database if conversation exists
    conversation_id = st.session_state.conversation_id
    if conversation_id:
        try:
            add_message_to_conversation(
                conversation_id=conversation_id,
                role=role,
                content=content,
                agent_name=agent,
            )
        except ConversationError:
            pass  # Non-critical, continue without persistence


def _start_new_conversation() -> None:
    """Start a new conversation."""
    # Reset coordinator
    coordinator = _get_or_create_coordinator()
    coordinator.reset()

    # Clear chat history
    st.session_state.chat_messages = []
    st.session_state.current_preview = None
    st.session_state.current_content = None

    # Create new conversation in database
    user_id = _get_user_id()
    if user_id:
        try:
            conversation = create_conversation(user_id)
            st.session_state.conversation_id = conversation.id
            coordinator.set_user_context(user_id, conversation.id)
        except ConversationError:
            st.session_state.conversation_id = None

    # Add welcome message
    welcome = """Hello! I'm here to help you create engaging content for TheLifeCo.

Tell me about the content you'd like to create. For example:
- "I want to create an Instagram post about our detox program"
- "Help me write content promoting our wellness retreat in Bodrum"
- "Create a newsletter about mindfulness and stress relief"

What would you like to create today?"""

    _add_message("assistant", welcome, agent="orchestrator")


def _continue_conversation(conversation_id: str) -> None:
    """Continue an existing conversation."""
    try:
        conversation = get_conversation(conversation_id)
        if conversation:
            st.session_state.conversation_id = conversation_id

            # Restore chat messages
            st.session_state.chat_messages = []
            for msg in conversation.messages:
                if hasattr(msg, 'role'):
                    st.session_state.chat_messages.append({
                        "role": msg.role,
                        "content": msg.content,
                        "agent": msg.agent_name,
                    })
                elif isinstance(msg, dict):
                    st.session_state.chat_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                        "agent": msg.get("agent_name"),
                    })

            # Restore coordinator state
            coordinator = _get_or_create_coordinator()
            if conversation.agent_state:
                coordinator.import_state(conversation.agent_state)

            user_id = _get_user_id()
            if user_id:
                coordinator.set_user_context(user_id, conversation_id)

    except ConversationError:
        _start_new_conversation()


def _process_user_message(message: str) -> None:
    """Process a user message through the coordinator."""
    if st.session_state.processing:
        return

    st.session_state.processing = True

    # Add user message to chat
    _add_message("user", message)

    # Get coordinator
    coordinator = _get_or_create_coordinator()

    try:
        # Process through coordinator
        result = coordinator.process_message(message)

        # Add assistant response
        stage = AgentStage(result["stage"])
        agent_name = stage.value.split("_")[0]  # Get base agent name

        _add_message("assistant", result["response"], agent=agent_name)

        # Handle stage-specific data
        if result.get("data"):
            data = result["data"]

            # Store preview
            if "preview" in data:
                st.session_state.current_preview = data["preview"]

            # Store content
            if "content" in data:
                st.session_state.current_content = data["content"]

        # Save coordinator state to conversation
        conversation_id = st.session_state.conversation_id
        if conversation_id:
            try:
                conversation = get_conversation(conversation_id)
                if conversation:
                    conversation.agent_state = coordinator.export_state()
                    conversation.current_agent = agent_name

                    # Update other fields
                    brief = coordinator.state.brief
                    if brief:
                        conversation.brief_data = brief.to_dict()
                        conversation.funnel_stage = brief.funnel_stage
                        conversation.platform = brief.platform
                        conversation.content_type = brief.content_type
                        conversation.campaign_info = brief.campaign_details or {}

                    update_conversation(conversation)
            except ConversationError:
                pass

    except Exception as e:
        _add_message("assistant", f"I encountered an error: {str(e)}. Please try again.", agent="system")

    finally:
        st.session_state.processing = False


def _render_stage_indicator() -> None:
    """Render the current stage indicator."""
    coordinator = _get_or_create_coordinator()
    current_stage = coordinator.get_current_stage()

    stages = [
        AgentStage.ORCHESTRATOR,
        AgentStage.WELLNESS,
        AgentStage.STORYTELLING_PREVIEW,
        AgentStage.STORYTELLING_CONTENT,
        AgentStage.REVIEW,
    ]

    # Create columns for stage indicators
    cols = st.columns(len(stages))

    for i, stage in enumerate(stages):
        info = STAGE_INFO.get(stage, {})
        name = info.get("name", stage.value)

        with cols[i]:
            if stage == current_stage:
                st.markdown(f"**:blue[{i+1}. {name}]**")
            elif stages.index(current_stage) > i:
                st.markdown(f":green[{i+1}. {name}]")
            else:
                st.markdown(f":gray[{i+1}. {name}]")

    # Show current stage description
    current_info = STAGE_INFO.get(current_stage, {})
    st.caption(f"*{current_info.get('description', 'Processing...')}*")


def _render_chat_messages() -> None:
    """Render all chat messages."""
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        content = msg["content"]
        agent = msg.get("agent")

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            # Assistant message
            avatar = None
            if agent == "orchestrator":
                avatar = None
            elif agent == "wellness":
                avatar = None
            elif agent == "storytelling":
                avatar = None
            elif agent == "review":
                avatar = None

            with st.chat_message("assistant", avatar=avatar):
                # Show agent badge
                if agent and agent != "system":
                    agent_display = agent.replace("_", " ").title()
                    st.caption(f"*{agent_display} Agent*")

                st.markdown(content)


def _render_preview_panel() -> None:
    """Render preview panel if available."""
    preview = st.session_state.current_preview
    if not preview:
        return

    with st.expander("Content Preview", expanded=True):
        st.markdown("### Hook")
        st.info(preview.get("hook", ""))

        if preview.get("hook_type"):
            st.caption(f"*Hook type: {preview['hook_type'].replace('_', ' ').title()}*")

        if preview.get("open_loops"):
            st.markdown("### Open Loops")
            for loop in preview["open_loops"]:
                st.markdown(f"- {loop}")

        if preview.get("promise"):
            st.markdown("### Promise")
            st.markdown(preview["promise"])


def _render_content_panel() -> None:
    """Render content panel if available."""
    content = st.session_state.current_content
    if not content:
        return

    with st.expander("Generated Content", expanded=True):
        # Content text
        content_text = content.get("content", "")
        st.text_area(
            "Content",
            value=content_text,
            height=300,
            label_visibility="collapsed",
        )

        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", content.get("word_count", len(content_text.split())))
        with col2:
            st.metric("Characters", content.get("character_count", len(content_text)))
        with col3:
            hashtags = content.get("hashtags", [])
            if hashtags:
                st.metric("Hashtags", len(hashtags))

        # Copy button
        if st.button("Copy to Clipboard", key="copy_content"):
            st.code(content_text, language=None)
            st.info("Select and copy the content above.")


def _render_sidebar() -> None:
    """Render the sidebar with conversation history."""
    with st.sidebar:
        st.subheader("Conversations")

        # New conversation button
        if st.button("New Conversation", type="primary", use_container_width=True):
            _start_new_conversation()
            st.rerun()

        st.divider()

        # Load past conversations
        user_id = _get_user_id()
        if user_id:
            try:
                conversations = get_user_conversations(user_id, limit=10)

                if conversations:
                    for conv in conversations:
                        title = conv.title or "Untitled"
                        if len(title) > 30:
                            title = title[:27] + "..."

                        # Highlight current conversation
                        is_current = conv.id == st.session_state.conversation_id
                        button_type = "primary" if is_current else "secondary"

                        if st.button(
                            title,
                            key=f"conv_{conv.id}",
                            type=button_type,
                            use_container_width=True,
                        ):
                            _continue_conversation(conv.id)
                            st.rerun()
                else:
                    st.caption("No past conversations")

            except ConversationError:
                st.caption("Could not load conversations")
        else:
            st.caption("Sign in to save conversations")

        st.divider()

        # Stats
        coordinator = st.session_state.coordinator
        if coordinator:
            st.caption("**Session Stats**")
            stats = coordinator.get_state_summary()
            st.caption(f"Stage: {stats['stage_description']}")

            cost = coordinator.get_total_cost()
            if cost > 0:
                st.caption(f"API Cost: ${cost:.4f}")


def render_create_mode() -> None:
    """Render the CREATE mode chat interface."""
    _initialize_session_state()

    # Render sidebar
    _render_sidebar()

    # Main content area
    st.header("Create Content")

    # Stage indicator
    _render_stage_indicator()

    st.divider()

    # Start new conversation if none exists
    if not st.session_state.chat_messages:
        _start_new_conversation()

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Render chat messages
        _render_chat_messages()

        # Render preview panel if available
        _render_preview_panel()

        # Render content panel if available
        _render_content_panel()

    # Chat input at bottom
    coordinator = _get_or_create_coordinator()
    stage = coordinator.get_current_stage()

    # Determine placeholder based on stage
    placeholders = {
        AgentStage.ORCHESTRATOR: "Tell me about the content you want to create...",
        AgentStage.WELLNESS: "Ask about specific facts or programs...",
        AgentStage.STORYTELLING_PREVIEW: "Do you like this preview? (yes/no/try another)",
        AgentStage.STORYTELLING_CONTENT: "Any adjustments needed?",
        AgentStage.REVIEW: "Share your feedback on the content...",
        AgentStage.COMPLETE: "Start a new conversation for more content",
    }

    placeholder = placeholders.get(stage, "Type your message...")

    # Disable input if complete
    disabled = stage == AgentStage.COMPLETE

    # Chat input
    if user_input := st.chat_input(placeholder, disabled=disabled):
        _process_user_message(user_input)
        st.rerun()

    # Show processing indicator
    if st.session_state.processing:
        with st.spinner("Thinking..."):
            pass
