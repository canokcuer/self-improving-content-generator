"""CREATE mode UI for content generation.

Provides the interface for:
- 13-question Socratic brief form
- Preview generation and approval
- Full content generation
"""

import streamlit as st

from content_assistant.generation.brief import (
    ContentBrief,
    Platform,
    ContentType,
    get_questions,
    validate_brief,
)
from content_assistant.generation.preview import generate_preview
from content_assistant.generation.generator import generate_content
from content_assistant.rag.knowledge_base import search_knowledge
from content_assistant.review.signals import store_generation_signals
from content_assistant.review.few_shot import get_few_shot_examples


def _render_step_indicator(steps: list, current_step: str) -> None:
    """Render a modern step indicator."""
    current_index = steps.index(current_step) if current_step in steps else 0

    # Create step indicator HTML
    step_html = '<div style="display: flex; justify-content: space-between; margin-bottom: 2rem;">'

    for i, step in enumerate(steps):
        if i < current_index:
            # Completed step
            step_html += f'''
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem;
                            background: #D1FAE5; border-radius: 8px; flex: 1; margin: 0 0.25rem;">
                    <span style="color: #059669; font-weight: 600;">✓</span>
                    <span style="color: #059669; font-size: 0.875rem; font-weight: 500;">{step.title()}</span>
                </div>
            '''
        elif i == current_index:
            # Current step
            step_html += f'''
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem;
                            background: #EDF7F0; border-radius: 8px; border: 2px solid #2D5A3D; flex: 1; margin: 0 0.25rem;">
                    <span style="background: #2D5A3D; color: white; width: 20px; height: 20px;
                                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                font-size: 0.75rem; font-weight: 600;">{i + 1}</span>
                    <span style="color: #2D5A3D; font-size: 0.875rem; font-weight: 600;">{step.title()}</span>
                </div>
            '''
        else:
            # Pending step
            step_html += f'''
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem;
                            background: #F3F4F6; border-radius: 8px; flex: 1; margin: 0 0.25rem;">
                    <span style="background: #D1D5DB; color: white; width: 20px; height: 20px;
                                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                font-size: 0.75rem; font-weight: 600;">{i + 1}</span>
                    <span style="color: #9CA3AF; font-size: 0.875rem; font-weight: 500;">{step.title()}</span>
                </div>
            '''

    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)


def render_create_mode() -> None:
    """Render the CREATE mode interface."""
    # Initialize session state
    if "current_brief" not in st.session_state:
        st.session_state.current_brief = None
    if "current_preview" not in st.session_state:
        st.session_state.current_preview = None
    if "current_content" not in st.session_state:
        st.session_state.current_content = None
    if "generation_step" not in st.session_state:
        st.session_state.generation_step = "brief"

    # Step indicator
    steps = ["brief", "preview", "content", "review"]
    current_step = st.session_state.generation_step

    _render_step_indicator(steps, current_step)

    # Render current step
    if current_step == "brief":
        _render_brief_form()
    elif current_step == "preview":
        _render_preview_step()
    elif current_step == "content":
        _render_content_step()
    elif current_step == "review":
        _render_review_step()


def _render_brief_form() -> None:
    """Render the 13-question brief form."""
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.25rem; font-weight: 600; color: #1A1A1A; margin-bottom: 0.5rem;">
                Content Brief
            </h2>
            <p style="color: #6B7280; font-size: 0.875rem;">
                Answer these questions to guide your content creation
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("brief_form"):
        # Platform and content type
        col1, col2 = st.columns(2)
        with col1:
            platform = st.selectbox(
                "Platform",
                options=[p.value for p in Platform],
                format_func=lambda x: x.title(),
            )
        with col2:
            content_type = st.selectbox(
                "Content Type",
                options=[ct.value for ct in ContentType],
                format_func=lambda x: x.title(),
            )

        st.divider()

        # Get Socratic questions
        questions = get_questions()

        # Required questions
        st.markdown("### Required Questions")

        answers = {}
        for q in questions:
            if q["required"]:
                answers[q["id"]] = st.text_area(
                    q["question"],
                    help=q["hint"],
                    key=f"brief_{q['id']}",
                    height=100,
                )

        # Optional questions
        with st.expander("Optional Questions (Recommended)"):
            for q in questions:
                if not q["required"]:
                    if q["id"] == "keywords":
                        keywords_text = st.text_input(
                            q["question"],
                            help=q["hint"],
                            key=f"brief_{q['id']}",
                        )
                        answers[q["id"]] = [k.strip() for k in keywords_text.split(",") if k.strip()]
                    else:
                        answers[q["id"]] = st.text_area(
                            q["question"],
                            help=q["hint"],
                            key=f"brief_{q['id']}",
                            height=80,
                        )

        submitted = st.form_submit_button("Generate Preview", type="primary")

        if submitted:
            try:
                brief = ContentBrief(
                    platform=Platform(platform),
                    content_type=ContentType(content_type),
                    transformation=answers.get("transformation", ""),
                    audience=answers.get("audience", ""),
                    pain_point=answers.get("pain_point", ""),
                    unique_angle=answers.get("unique_angle", ""),
                    core_message=answers.get("core_message", ""),
                    call_to_action=answers.get("call_to_action", ""),
                    evidence=answers.get("evidence"),
                    emotional_journey=answers.get("emotional_journey"),
                    objections=answers.get("objections"),
                    tone=answers.get("tone"),
                    hook_style=answers.get("hook_style"),
                    keywords=answers.get("keywords", []),
                    constraints=answers.get("constraints"),
                )

                # Validate brief
                errors = validate_brief(brief)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    st.session_state.current_brief = brief
                    st.session_state.generation_step = "preview"
                    st.rerun()

            except Exception as e:
                st.error(f"Error creating brief: {e}")


def _render_preview_step() -> None:
    """Render the preview generation step."""
    st.markdown("""
        <h2 style="font-size: 1.25rem; font-weight: 600; color: #1A1A1A; margin-bottom: 1rem;">
            Content Preview
        </h2>
    """, unsafe_allow_html=True)

    brief = st.session_state.current_brief
    if not brief:
        st.session_state.generation_step = "brief"
        st.rerun()
        return

    # Show brief summary
    with st.expander("Brief Summary", expanded=False):
        st.markdown(brief.to_prompt_context())

    # Generate preview if not already done
    if st.session_state.current_preview is None:
        with st.spinner("Generating preview..."):
            try:
                # Get knowledge context
                knowledge_context = None
                try:
                    knowledge_results = search_knowledge(
                        brief.core_message,
                        match_count=5,
                    )
                    if knowledge_results:
                        knowledge_context = "\n\n".join([
                            r.get("content", "") for r in knowledge_results
                        ])
                except Exception:
                    pass  # Knowledge base might not be set up

                preview, metadata = generate_preview(
                    brief,
                    knowledge_context=knowledge_context,
                )

                st.session_state.current_preview = preview
                st.session_state.preview_metadata = metadata

            except Exception as e:
                st.error(f"Failed to generate preview: {e}")
                if st.button("Back to Brief"):
                    st.session_state.generation_step = "brief"
                    st.rerun()
                return

    preview = st.session_state.current_preview

    # Display preview
    st.markdown("### Hook")
    st.info(preview.hook)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Hook Type:** {preview.hook_type.replace('_', ' ').title()}")
    with col2:
        st.markdown(f"**Direction:** {preview.brief_summary}")

    st.markdown("### Open Loops")
    for loop in preview.open_loops:
        st.markdown(f"- {loop}")

    st.markdown("### Promise")
    st.markdown(preview.promise)

    # Show cost
    if "preview_metadata" in st.session_state:
        meta = st.session_state.preview_metadata
        st.caption(f"Cost: ${meta.get('cost_usd', 0):.4f}")

    st.divider()

    # Actions
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Regenerate Preview"):
            st.session_state.current_preview = None
            st.rerun()

    with col2:
        if st.button("Back to Brief"):
            st.session_state.current_preview = None
            st.session_state.generation_step = "brief"
            st.rerun()

    with col3:
        if st.button("Approve & Generate Content", type="primary"):
            st.session_state.generation_step = "content"
            st.rerun()


def _render_content_step() -> None:
    """Render the full content generation step."""
    st.markdown("""
        <h2 style="font-size: 1.25rem; font-weight: 600; color: #1A1A1A; margin-bottom: 1rem;">
            Generated Content
        </h2>
    """, unsafe_allow_html=True)

    brief = st.session_state.current_brief
    preview = st.session_state.current_preview

    if not brief or not preview:
        st.session_state.generation_step = "brief"
        st.rerun()
        return

    # Generate content if not already done
    if st.session_state.current_content is None:
        with st.spinner("Generating content..."):
            try:
                # Get knowledge context
                knowledge_context = None
                try:
                    knowledge_results = search_knowledge(
                        brief.core_message,
                        match_count=5,
                    )
                    if knowledge_results:
                        knowledge_context = "\n\n".join([
                            r.get("content", "") for r in knowledge_results
                        ])
                except Exception:
                    pass

                # Get few-shot examples
                few_shot = None
                try:
                    brief_text = brief.to_prompt_context()
                    examples = get_few_shot_examples(
                        brief_text,
                        platform=brief.platform.value,
                        min_rating=4,
                        max_examples=3,
                    )
                    if examples:
                        few_shot = examples
                except Exception:
                    pass

                content = generate_content(
                    brief,
                    preview,
                    knowledge_context=knowledge_context,
                    few_shot_examples=few_shot,
                )

                st.session_state.current_content = content

            except Exception as e:
                st.error(f"Failed to generate content: {e}")
                if st.button("Back to Preview"):
                    st.session_state.generation_step = "preview"
                    st.rerun()
                return

    content = st.session_state.current_content

    # Display content
    st.markdown("### Your Content")
    st.text_area(
        "Content",
        value=content.content,
        height=400,
        label_visibility="collapsed",
    )

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Words", content.word_count)
    with col2:
        st.metric("Characters", content.character_count)
    with col3:
        if content.hashtags:
            st.metric("Hashtags", len(content.hashtags))

    # Cost
    if content.metadata:
        st.caption(f"Cost: ${content.metadata.get('cost_usd', 0):.4f}")

    st.divider()

    # Actions
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Regenerate Content"):
            st.session_state.current_content = None
            st.rerun()

    with col2:
        if st.button("Back to Preview"):
            st.session_state.current_content = None
            st.session_state.generation_step = "preview"
            st.rerun()

    with col3:
        if st.button("Review & Rate", type="primary"):
            st.session_state.generation_step = "review"
            st.rerun()


def _render_review_step() -> None:
    """Render the review and rating step."""
    st.markdown("""
        <h2 style="font-size: 1.25rem; font-weight: 600; color: #1A1A1A; margin-bottom: 1rem;">
            Review & Rate
        </h2>
    """, unsafe_allow_html=True)

    brief = st.session_state.current_brief
    preview = st.session_state.current_preview
    content = st.session_state.current_content

    if not brief or not preview or not content:
        st.session_state.generation_step = "brief"
        st.rerun()
        return

    # Display final content
    st.markdown("### Final Content")
    st.text_area(
        "Content",
        value=content.content,
        height=300,
        label_visibility="collapsed",
        disabled=True,
    )

    st.divider()

    # Rating form
    with st.form("rating_form"):
        st.markdown("### Rate This Content")

        rating = st.slider(
            "Overall Rating",
            min_value=1,
            max_value=5,
            value=4,
            help="1 = Poor, 5 = Excellent",
        )

        st.markdown("**What worked well?** (Select all that apply)")
        what_worked_options = [
            "Strong hook",
            "Clear message",
            "Good flow",
            "Compelling CTA",
            "On-brand tone",
            "Accurate information",
        ]
        what_worked = [opt for opt in what_worked_options if st.checkbox(opt, key=f"worked_{opt}")]

        st.markdown("**What needs improvement?** (Select all that apply)")
        needs_work_options = [
            "Weak hook",
            "Unclear message",
            "Poor flow",
            "Weak CTA",
            "Off-brand tone",
            "Inaccurate information",
        ]
        what_needs_work = [opt for opt in needs_work_options if st.checkbox(opt, key=f"needs_{opt}")]

        approve = st.checkbox("Approve this content for use", value=True)

        submitted = st.form_submit_button("Save & Complete", type="primary")

        if submitted:
            try:
                # Store generation with signals
                user = st.session_state.get("user", {})
                user_id = user.get("id") if user else None

                store_generation_signals(
                    brief=brief.to_dict(),
                    preview=preview.to_dict(),
                    content=content.content,
                    platform=brief.platform.value,
                    content_type=brief.content_type.value,
                    rating=rating,
                    what_worked=what_worked,
                    what_needs_work=what_needs_work,
                    was_approved=approve,
                    user_id=user_id,
                    api_cost_usd=content.metadata.get("cost_usd", 0),
                )

                st.success("Content saved!")

                # Reset for new content
                if st.button("Create New Content"):
                    st.session_state.current_brief = None
                    st.session_state.current_preview = None
                    st.session_state.current_content = None
                    st.session_state.generation_step = "brief"
                    st.rerun()

            except Exception as e:
                st.error(f"Failed to save: {e}")

    # Copy button
    st.divider()
    if st.button("Copy Content to Clipboard"):
        st.code(content.content, language=None)
        st.info("Select and copy the content above.")
