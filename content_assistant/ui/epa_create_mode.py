"""EPA-based CREATE mode UI for content generation.

Uses the new EPA-GONCA-ALP architecture:
- EPA: Main orchestrator that talks to users
- GONCA: Wellness sub-agent (invoked by EPA)
- ALP: Storytelling sub-agent (invoked by EPA)

SECURITY NOTE: All database operations go through the API client
which enforces authentication via JWT tokens.
"""

import streamlit as st
from typing import Optional
import logging

import re

from content_assistant.agents import (
    EPAAgent,
    EPAStage,
    ContentBrief,
)
from content_assistant.services.api_client import api_client
from content_assistant.utils.error_handler import handle_error, ErrorType

logger = logging.getLogger(__name__)


def _clean_response_content(content: str) -> str:
    """Clean response content by removing JSON blocks and code that shouldn't be shown to users.

    This filters out:
    - JSON code blocks (```json ... ```)
    - Generic code blocks (``` ... ```)
    - Raw JSON objects that look like tool calls
    """
    if not content:
        return content

    # Remove JSON code blocks (```json ... ```)
    content = re.sub(r'```json\s*\n[\s\S]*?\n```', '', content)

    # Remove generic code blocks (``` ... ```) that contain JSON-like content
    def remove_json_blocks(match):
        block_content = match.group(1)
        # If it looks like JSON (starts with { or [), remove the whole block
        if block_content.strip().startswith(('{', '[')):
            return ''
        return match.group(0)  # Keep non-JSON code blocks

    content = re.sub(r'```\s*\n([\s\S]*?)\n```', remove_json_blocks, content)

    # Remove raw JSON objects that look like tool responses
    # Pattern: lines that are just JSON objects
    content = re.sub(r'^\s*\{[^}]+\}\s*$', '', content, flags=re.MULTILINE)

    # Clean up multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()


# Stage display names and descriptions for EPA
STAGE_INFO = {
    EPAStage.BRIEFING: {
        "name": "Briefing",
        "icon": "clipboard",
        "description": "Understanding your content needs",
        "thinking": "EPA is gathering requirements...",
    },
    EPAStage.CONSULTING_GONCA: {
        "name": "Research",
        "icon": "book",
        "description": "EPA is consulting GONCA (wellness expert)",
        "thinking": "Gathering verified facts from knowledge base...",
    },
    EPAStage.CONSULTING_ALP: {
        "name": "Creating",
        "icon": "pen",
        "description": "EPA is consulting ALP (storytelling expert)",
        "thinking": "Crafting your content...",
    },
    EPAStage.REVIEWING: {
        "name": "Review",
        "icon": "check-circle",
        "description": "EPA is reviewing content quality",
        "thinking": "Quality checking content...",
    },
    EPAStage.PRESENTING: {
        "name": "Presenting",
        "icon": "eye",
        "description": "Here's your content",
        "thinking": "Preparing content for you...",
    },
    EPAStage.COLLECTING_FEEDBACK: {
        "name": "Feedback",
        "icon": "message-square",
        "description": "Processing your feedback",
        "thinking": "Analyzing your feedback...",
    },
    EPAStage.REVISING: {
        "name": "Revising",
        "icon": "edit",
        "description": "Making revisions",
        "thinking": "Updating content based on feedback...",
    },
    EPAStage.COMPLETE: {
        "name": "Complete",
        "icon": "check",
        "description": "Content generation complete",
        "thinking": "Finishing up...",
    },
}


def _initialize_session_state() -> None:
    """Initialize all session state variables."""
    if "epa_agent" not in st.session_state:
        st.session_state.epa_agent = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "current_content" not in st.session_state:
        st.session_state.current_content = None
    if "awaiting_response" not in st.session_state:
        st.session_state.awaiting_response = False


def _get_or_create_epa() -> EPAAgent:
    """Get existing EPA agent or create new one."""
    if st.session_state.epa_agent is None:
        st.session_state.epa_agent = EPAAgent()
    return st.session_state.epa_agent


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
    """Start a new conversation with EPA."""
    # Reset EPA agent
    epa = _get_or_create_epa()
    epa.reset()

    # Clear chat history
    st.session_state.chat_messages = []
    st.session_state.current_content = None
    st.session_state.awaiting_response = False

    # Create new conversation via API
    user_id = _get_user_id()
    if user_id:
        try:
            response = api_client.create_conversation()
            if response.success and response.data:
                st.session_state.conversation_id = response.data.get("id")
            else:
                logger.warning(f"Failed to create conversation: {response.error}")
                st.session_state.conversation_id = None
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            st.session_state.conversation_id = None

    # Add welcome message from EPA
    welcome = """Hello! I'm EPA, your content creation assistant for TheLifeCo.

I'll help you create engaging wellness content by understanding your needs deeply. To create the best content, I'll need to know about:

- **Who** you're targeting (your audience)
- **What pain point** you're addressing (this is crucial!)
- **Which programs or centers** to feature
- **Where** the content will be published
- And a few more details...

**Let's start!** Tell me about the content you'd like to create. For example:
- "I want to create an Instagram post about our detox program for Bodrum"
- "Help me write an email about weight loss for people feeling low energy"
- "Create a LinkedIn post about our mental wellness offerings"

What would you like to create today?"""

    _add_message("assistant", welcome, agent="epa")


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

            # Restore EPA state
            epa = _get_or_create_epa()
            agent_state = conversation.get("agent_state")
            if agent_state:
                epa.import_state(agent_state)

        else:
            logger.warning(f"Failed to load conversation: {response.error}")
            _start_new_conversation()

    except Exception as e:
        logger.error(f"Failed to continue conversation: {e}")
        _start_new_conversation()


def _render_stage_indicator() -> None:
    """Render the current stage indicator."""
    epa = _get_or_create_epa()
    current_stage = epa.get_state().stage

    # Key stages to show
    stages = [
        EPAStage.BRIEFING,
        EPAStage.CONSULTING_GONCA,
        EPAStage.CONSULTING_ALP,
        EPAStage.REVIEWING,
        EPAStage.COMPLETE,
    ]

    # Create columns for stage indicators
    cols = st.columns(len(stages))

    stage_order = list(EPAStage)
    current_idx = stage_order.index(current_stage)

    for i, stage in enumerate(stages):
        info = STAGE_INFO.get(stage, {})
        name = info.get("name", stage.value)
        stage_idx = stage_order.index(stage)

        with cols[i]:
            if stage == current_stage:
                st.markdown(f"**:blue[{i+1}. {name}]**")
            elif current_idx > stage_idx:
                st.markdown(f":green[{i+1}. {name}]")
            else:
                st.markdown(f":gray[{i+1}. {name}]")

    # Show current stage description
    current_info = STAGE_INFO.get(current_stage, {})
    st.caption(f"*{current_info.get('description', 'Processing...')}*")


def _render_brief_status() -> None:
    """Render the brief collection status."""
    epa = _get_or_create_epa()
    brief = epa.get_brief()
    missing = brief.get_missing_fields()

    if brief.is_complete():
        st.success("Brief complete - ready for content generation")
    else:
        with st.expander("Brief Status", expanded=False):
            st.caption(f"Missing: {len(missing)} fields")
            for field in missing:
                st.caption(f"- {field}")


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
                if agent:
                    agent_display = {
                        "epa": "EPA (Orchestrator)",
                        "gonca": "GONCA (Wellness)",
                        "alp": "ALP (Storytelling)",
                        "review": "Review",
                    }.get(agent.lower(), agent.title())
                    st.caption(f"*{agent_display}*")

                # Clean content to remove code blocks and JSON
                cleaned_content = _clean_response_content(content)
                st.markdown(cleaned_content)


def _render_content_panel() -> None:
    """Render content panel if available."""
    content = st.session_state.current_content
    if not content:
        return

    with st.expander("Generated Content", expanded=True):
        # Hook
        if content.get("hook"):
            st.markdown("### Hook")
            st.info(content["hook"])
            if content.get("hook_type"):
                st.caption(f"*Hook type: {content['hook_type']}*")

        # Main content
        content_text = content.get("content", "")
        st.markdown("### Content")
        st.text_area(
            "Content",
            value=content_text,
            height=300,
            label_visibility="collapsed",
        )

        # CTA
        if content.get("call_to_action"):
            st.markdown("### Call to Action")
            st.markdown(content["call_to_action"])

        # Hashtags
        if content.get("hashtags"):
            st.markdown("### Hashtags")
            st.markdown(" ".join(f"#{tag}" for tag in content["hashtags"]))

        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", content.get("word_count", len(content_text.split())))
        with col2:
            st.metric("Characters", content.get("character_count", len(content_text)))
        with col3:
            if content.get("storytelling_framework"):
                st.metric("Framework", content["storytelling_framework"])

        # Copy button
        full_content = f"{content.get('hook', '')}\n\n{content_text}\n\n{content.get('call_to_action', '')}"
        if st.button("Copy to Clipboard", key="copy_content"):
            st.code(full_content, language=None)
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
        epa = st.session_state.epa_agent
        if epa:
            st.caption("**Session Stats**")
            state = epa.get_state()
            st.caption(f"Stage: {epa.get_stage_display()}")
            st.caption(f"Brief: {epa.get_brief_summary()}")

            stats = epa.get_stats()
            if stats.get("total_cost_usd", 0) > 0:
                st.caption(f"API Cost: ${stats['total_cost_usd']:.4f}")


def _process_and_display_response(message: str, response_placeholder) -> None:
    """Process message and display response with thinking indicators."""
    epa = _get_or_create_epa()
    state = epa.get_state()
    stage_info = STAGE_INFO.get(state.stage, {})

    # Show thinking in the placeholder
    with response_placeholder.container():
        with st.chat_message("assistant"):
            st.caption("*EPA (Orchestrator)*")
            with st.status(stage_info.get("thinking", "Processing..."), expanded=True) as status:
                st.write(f"**Stage:** {stage_info.get('name', 'Processing')}")
                st.write("Analyzing your message...")

                try:
                    # Process through EPA
                    result = epa.process_message_sync(message)
                    status.update(label="Done!", state="complete", expanded=False)

                except Exception as e:
                    status.update(label="Error occurred", state="error", expanded=True)
                    st.error(f"**Error:** {str(e)}")
                    _add_message("assistant", f"I encountered an error: {str(e)}. Please try again.", agent="epa")
                    return

    # Clear placeholder and add response to history
    response_placeholder.empty()

    # Add the actual response
    _add_message("assistant", result.content, agent="epa")

    # Check for generated content
    storytelling_response = epa.get_state().storytelling_response
    if storytelling_response:
        st.session_state.current_content = {
            "hook": storytelling_response.hook,
            "hook_type": storytelling_response.hook_type,
            "content": storytelling_response.content,
            "call_to_action": storytelling_response.call_to_action,
            "hashtags": storytelling_response.hashtags,
            "word_count": storytelling_response.word_count,
            "character_count": storytelling_response.character_count,
            "storytelling_framework": storytelling_response.storytelling_framework,
        }

    # Save EPA state via API
    conversation_id = st.session_state.conversation_id
    if conversation_id:
        try:
            update_data = {
                "agent_state": epa.export_state(),
                "current_agent": "epa",
            }

            brief = epa.get_brief()
            if brief.pain_area:  # Only update if we have some brief data
                update_data["brief_data"] = brief.to_dict()
                update_data["funnel_stage"] = brief.funnel_stage.value if brief.funnel_stage else None
                update_data["platform"] = brief.platform.value if brief.platform else None

            response = api_client.update_conversation(conversation_id, update_data)
            if not response.success:
                logger.warning(f"Failed to update conversation state: {response.error}")
        except Exception as e:
            logger.warning(f"Failed to update conversation state: {e}")


def render_epa_create_mode() -> None:
    """Render the EPA-based CREATE mode chat interface."""
    _initialize_session_state()

    # Render sidebar
    _render_sidebar()

    # Main content area
    st.header("Create Content")
    st.caption("Powered by EPA-GONCA-ALP architecture")

    # Show processing banner if awaiting response
    if st.session_state.awaiting_response:
        st.info("Processing your message... Please wait.")

    # Stage indicator
    _render_stage_indicator()

    # Brief status (collapsed by default)
    _render_brief_status()

    st.divider()

    # Start new conversation if none exists
    if not st.session_state.chat_messages:
        _start_new_conversation()

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Render chat messages
        _render_chat_messages()

        # Create placeholder for response (before content panel)
        response_placeholder = st.empty()

        # Render content panel if available
        _render_content_panel()

    # Chat input at bottom
    epa = _get_or_create_epa()
    state = epa.get_state()

    # Determine placeholder text based on stage
    input_placeholders = {
        EPAStage.BRIEFING: "Tell me about the content you want to create...",
        EPAStage.CONSULTING_GONCA: "EPA is gathering information...",
        EPAStage.CONSULTING_ALP: "EPA is creating content...",
        EPAStage.REVIEWING: "EPA is reviewing...",
        EPAStage.PRESENTING: "How does this content look? Any feedback?",
        EPAStage.COLLECTING_FEEDBACK: "Share your feedback on the content...",
        EPAStage.REVISING: "Working on revisions...",
        EPAStage.COMPLETE: "Start a new conversation for more content",
    }

    input_placeholder = input_placeholders.get(state.stage, "Type your message...")

    # Disable input if processing or complete
    disabled = state.stage == EPAStage.COMPLETE or st.session_state.awaiting_response

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


# For backward compatibility and easy switching
render_create_mode = render_epa_create_mode
