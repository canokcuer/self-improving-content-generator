"""CREATE mode UI for content generation.

Provides a conversational chat interface for:
- Multi-agent content briefing
- Preview generation and approval
- Full content generation
- Feedback collection

SECURITY NOTE: All database operations go through the API client
which enforces authentication via JWT tokens.
"""

import streamlit as st
from typing import Optional
import logging

from content_assistant.agents import (
    AgentCoordinator,
    AgentStage,
)
from content_assistant.services.api_client import api_client
from content_assistant.utils.error_handler import handle_error, ErrorType

logger = logging.getLogger(__name__)


# Stage display names and descriptions
STAGE_INFO = {
    AgentStage.ORCHESTRATOR: {
        "name": "Briefing",
        "icon": "clipboard",
        "description": "Understanding your content needs",
        "thinking": "Understanding your request...",
    },
    AgentStage.WELLNESS: {
        "name": "Verification",
        "icon": "check-circle",
        "description": "Verifying facts and gathering information",
        "thinking": "Verifying facts against knowledge base...",
    },
    AgentStage.STORYTELLING_PREVIEW: {
        "name": "Preview",
        "icon": "eye",
        "description": "Creating content preview",
        "thinking": "Crafting engaging hooks and preview...",
    },
    AgentStage.STORYTELLING_CONTENT: {
        "name": "Content",
        "icon": "file-text",
        "description": "Generating full content",
        "thinking": "Writing your full content...",
    },
    AgentStage.REVIEW: {
        "name": "Review",
        "icon": "star",
        "description": "Collecting your feedback",
        "thinking": "Processing your feedback...",
    },
    AgentStage.COMPLETE: {
        "name": "Complete",
        "icon": "check",
        "description": "Content generation complete",
        "thinking": "Finishing up...",
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
    if "awaiting_response" not in st.session_state:
        st.session_state.awaiting_response = False


def _get_or_create_coordinator() -> AgentCoordinator:
    """Get existing coordinator or create new one."""
    if st.session_state.coordinator is None:
        def on_stage_change(new_stage: AgentStage):
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

    # Also save to database via API if conversation exists
    conversation_id = st.session_state.conversation_id
    if conversation_id:
        try:
            response = api_client.add_message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                agent_name=agent,
            )
            if not response.success:
                logger.warning(f"Failed to save message: {response.error}")
        except Exception as e:
            logger.warning(f"Failed to save message: {e}")


def _start_new_conversation() -> None:
    """Start a new conversation."""
    # Reset coordinator
    coordinator = _get_or_create_coordinator()
    coordinator.reset()

    # Clear chat history
    st.session_state.chat_messages = []
    st.session_state.current_preview = None
    st.session_state.current_content = None
    st.session_state.awaiting_response = False

    # Create new conversation via API
    user_id = _get_user_id()
    if user_id:
        try:
            response = api_client.create_conversation()
            if response.success and response.data:
                st.session_state.conversation_id = response.data.get("id")
                coordinator.set_user_context(user_id, st.session_state.conversation_id)
            else:
                logger.warning(f"Failed to create conversation: {response.error}")
                st.session_state.conversation_id = None
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
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
        response = api_client.get_conversation(conversation_id)
        if response.success and response.data:
            conversation = response.data
            st.session_state.conversation_id = conversation_id

            # Restore chat messages
            st.session_state.chat_messages = []
            messages = conversation.get("messages", [])
            for msg in messages:
                if isinstance(msg, dict):
                    st.session_state.chat_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                        "agent": msg.get("agent_name"),
                    })

            # Restore coordinator state
            coordinator = _get_or_create_coordinator()
            agent_state = conversation.get("agent_state")
            if agent_state:
                coordinator.import_state(agent_state)

            user_id = _get_user_id()
            if user_id:
                coordinator.set_user_context(user_id, conversation_id)
        else:
            logger.warning(f"Failed to load conversation: {response.error}")
            _start_new_conversation()

    except Exception as e:
        logger.error(f"Failed to continue conversation: {e}")
        _start_new_conversation()


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
            with st.chat_message("assistant"):
                # Show agent badge
                if agent and agent != "system":
                    agent_display = agent.replace("_", " ").title()
                    st.caption(f"*{agent_display} Agent*")

                st.markdown(content)


def _render_thinking_indicator(stage: AgentStage, step: str = "") -> None:
    """Render a thinking indicator in the chat."""
    info = STAGE_INFO.get(stage, {})
    thinking_text = info.get("thinking", "Processing...")
    agent_name = stage.value.split("_")[0].title()

    with st.chat_message("assistant"):
        st.caption(f"*{agent_name} Agent*")
        with st.status(thinking_text, expanded=True) as status:
            st.write(f"Stage: **{info.get('name', 'Processing')}**")
            if step:
                st.write(f"Step: {step}")
            st.write("Please wait...")
            return status


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

        # Load past conversations via API
        user_id = _get_user_id()
        if user_id:
            try:
                response = api_client.get_conversations(limit=10)

                if response.success and response.data:
                    conversations = response.data
                    for conv in conversations:
                        title = conv.get("title") or "Untitled"
                        if len(title) > 30:
                            title = title[:27] + "..."

                        # Highlight current conversation
                        conv_id = conv.get("id")
                        is_current = conv_id == st.session_state.conversation_id
                        button_type = "primary" if is_current else "secondary"

                        if st.button(
                            title,
                            key=f"conv_{conv_id}",
                            type=button_type,
                            use_container_width=True,
                        ):
                            _continue_conversation(conv_id)
                            st.rerun()
                else:
                    st.caption("No past conversations")

            except Exception as e:
                logger.warning(f"Failed to load conversations: {e}")
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


def _process_and_display_response(message: str, response_placeholder) -> None:
    """Process message and display response with thinking indicators."""
    coordinator = _get_or_create_coordinator()
    current_stage = coordinator.get_current_stage()
    stage_info = STAGE_INFO.get(current_stage, {})
    agent_name = current_stage.value.split("_")[0]

    # Show thinking in the placeholder
    with response_placeholder.container():
        with st.chat_message("assistant"):
            st.caption(f"*{agent_name.title()} Agent*")
            with st.status(stage_info.get("thinking", "Processing..."), expanded=True) as status:
                st.write(f"**Stage:** {stage_info.get('name', 'Processing')}")
                st.write("Analyzing your message...")
                st.write("*Calling Claude API...*")

                try:
                    # Process through coordinator
                    result = coordinator.process_message(message)
                    status.update(label="Done!", state="complete", expanded=False)

                except Exception as e:
                    status.update(label="Error occurred", state="error", expanded=True)
                    st.error(f"**Error:** {str(e)}")
                    st.code(str(type(e).__name__))  # Show error type for debugging
                    _add_message("assistant", f"I encountered an error: {str(e)}. Please try again.", agent="system")
                    return

    # Clear placeholder and add response to history
    response_placeholder.empty()

    # Add the actual response
    stage = AgentStage(result["stage"])
    response_agent_name = stage.value.split("_")[0]

    _add_message("assistant", result["response"], agent=response_agent_name)

    # Handle stage-specific data
    if result.get("data"):
        data = result["data"]

        if "preview" in data:
            st.session_state.current_preview = data["preview"]

        if "content" in data:
            st.session_state.current_content = data["content"]

    # Save coordinator state via API
    conversation_id = st.session_state.conversation_id
    if conversation_id:
        try:
            update_data = {
                "agent_state": coordinator.export_state(),
                "current_agent": response_agent_name,
            }

            brief = coordinator.state.brief
            if brief:
                update_data["brief_data"] = brief.to_dict()
                update_data["funnel_stage"] = brief.funnel_stage
                update_data["platform"] = brief.platform
                update_data["content_type"] = brief.content_type
                update_data["campaign_info"] = {
                    "has_campaign": brief.has_campaign,
                    "campaign_price": brief.campaign_price,
                    "campaign_duration": brief.campaign_duration,
                    "campaign_center": brief.campaign_center,
                    "campaign_deadline": brief.campaign_deadline,
                }

            response = api_client.update_conversation(conversation_id, update_data)
            if not response.success:
                logger.warning(f"Failed to update conversation state: {response.error}")
        except Exception as e:
            logger.warning(f"Failed to update conversation state: {e}")


def render_create_mode() -> None:
    """Render the CREATE mode chat interface."""
    _initialize_session_state()

    # Render sidebar
    _render_sidebar()

    # Main content area
    st.header("Create Content")

    # Show processing banner if awaiting response
    if st.session_state.awaiting_response:
        st.info("Processing your message... Please wait.")

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

        # Create placeholder for response (before preview/content panels)
        response_placeholder = st.empty()

        # Render preview panel if available
        _render_preview_panel()

        # Render content panel if available
        _render_content_panel()

    # Chat input at bottom
    coordinator = _get_or_create_coordinator()
    stage = coordinator.get_current_stage()

    # Determine placeholder text based on stage
    input_placeholders = {
        AgentStage.ORCHESTRATOR: "Tell me about the content you want to create...",
        AgentStage.WELLNESS: "Ask about specific facts or programs...",
        AgentStage.STORYTELLING_PREVIEW: "Do you like this preview? (yes/no/try another)",
        AgentStage.STORYTELLING_CONTENT: "Any adjustments needed?",
        AgentStage.REVIEW: "Share your feedback on the content...",
        AgentStage.COMPLETE: "Start a new conversation for more content",
    }

    input_placeholder = input_placeholders.get(stage, "Type your message...")

    # Disable input if processing or complete
    disabled = stage == AgentStage.COMPLETE or st.session_state.awaiting_response

    # Chat input
    if user_input := st.chat_input(input_placeholder, disabled=disabled):
        # Add user message immediately to chat history
        _add_message("user", user_input)
        # Set flag to process on next render
        st.session_state.awaiting_response = True
        st.rerun()

    # Process response if awaiting (after messages are displayed)
    if st.session_state.awaiting_response:
        # Get the last user message
        last_user_msg = None
        for msg in reversed(st.session_state.chat_messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        if last_user_msg:
            _process_and_display_response(last_user_msg, response_placeholder)
            st.session_state.awaiting_response = False
            st.rerun()
