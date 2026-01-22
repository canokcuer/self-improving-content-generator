"""REVIEW mode UI for content analysis.

Provides the interface for:
- Wellness verification
- Engagement analysis
- Content comparison
"""

import streamlit as st

from content_assistant.review.wellness_verifier import (
    verify_wellness_claims,
    get_verification_summary,
)
from content_assistant.review.engagement import (
    analyze_engagement,
    get_engagement_summary,
    compare_content_versions,
)


def render_review_mode() -> None:
    """Render the REVIEW mode interface."""
    st.header("Review Content")

    # Tab navigation
    tab1, tab2, tab3 = st.tabs([
        "Wellness Verification",
        "Engagement Analysis",
        "Compare Versions",
    ])

    with tab1:
        _render_wellness_verification()

    with tab2:
        _render_engagement_analysis()

    with tab3:
        _render_comparison()


def _render_wellness_verification() -> None:
    """Render wellness verification interface."""
    st.subheader("Wellness Claim Verification")
    st.markdown("Check your content against TheLifeCo's knowledge base.")

    content = st.text_area(
        "Paste content to verify",
        height=200,
        placeholder="Enter your content here...",
        key="verify_content",
    )

    strict_mode = st.checkbox(
        "Strict Mode",
        help="Require explicit knowledge base support for all claims",
    )

    if st.button("Verify Content", type="primary", disabled=not content):
        with st.spinner("Verifying claims..."):
            try:
                result = verify_wellness_claims(content, strict_mode=strict_mode)

                # Show result
                if result.is_verified:
                    st.success(f"Verification Passed ({result.score}/100)")
                else:
                    st.warning(f"Needs Review ({result.score}/100)")

                # Detailed results
                st.markdown(get_verification_summary(result))

                # Supporting knowledge
                if result.supporting_knowledge:
                    with st.expander("Supporting Knowledge"):
                        for k in result.supporting_knowledge:
                            st.markdown(f"**Source:** {k.get('source', 'Unknown')}")
                            st.markdown(k.get("content", "")[:500] + "...")
                            st.divider()

            except Exception as e:
                st.error(f"Verification failed: {e}")


def _render_engagement_analysis() -> None:
    """Render engagement analysis interface."""
    st.subheader("Engagement Analysis")
    st.markdown("Analyze your content's engagement potential.")

    content = st.text_area(
        "Paste content to analyze",
        height=200,
        placeholder="Enter your content here...",
        key="analyze_content",
    )

    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox(
            "Platform",
            options=["instagram", "linkedin", "twitter", "facebook", "blog"],
            format_func=lambda x: x.title(),
            key="analyze_platform",
        )
    with col2:
        content_type = st.selectbox(
            "Content Type",
            options=["post", "article", "story", "reel", "carousel"],
            format_func=lambda x: x.title(),
            key="analyze_type",
        )

    if st.button("Analyze Engagement", type="primary", disabled=not content):
        with st.spinner("Analyzing..."):
            try:
                analysis = analyze_engagement(content, platform, content_type)

                # Score display
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    score = analysis.overall_score
                    if score >= 80:
                        st.metric("Overall", f"{score}/100", delta="Good")
                    elif score >= 60:
                        st.metric("Overall", f"{score}/100")
                    else:
                        st.metric("Overall", f"{score}/100", delta="Needs work", delta_color="inverse")

                with col2:
                    st.metric("Hook", f"{analysis.hook_strength}/100")

                with col3:
                    st.metric("Retention", f"{analysis.retention_score}/100")

                with col4:
                    st.metric("CTA", f"{analysis.cta_effectiveness}/100")

                # Detailed analysis
                st.markdown(get_engagement_summary(analysis))

            except Exception as e:
                st.error(f"Analysis failed: {e}")


def _render_comparison() -> None:
    """Render content comparison interface."""
    st.subheader("Compare Content Versions")
    st.markdown("Compare two versions of content to see which performs better.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Version A")
        version_a = st.text_area(
            "Version A",
            height=200,
            placeholder="Paste version A...",
            label_visibility="collapsed",
            key="compare_a",
        )

    with col2:
        st.markdown("### Version B")
        version_b = st.text_area(
            "Version B",
            height=200,
            placeholder="Paste version B...",
            label_visibility="collapsed",
            key="compare_b",
        )

    platform = st.selectbox(
        "Platform",
        options=["instagram", "linkedin", "twitter", "facebook", "blog"],
        format_func=lambda x: x.title(),
        key="compare_platform",
    )

    if st.button(
        "Compare Versions",
        type="primary",
        disabled=not (version_a and version_b),
    ):
        with st.spinner("Comparing..."):
            try:
                result = compare_content_versions(version_a, version_b, platform)

                # Winner display
                winner = result.get("winner", "tie")
                confidence = result.get("confidence", 0)

                if winner == "A":
                    st.success(f"**Winner: Version A** (Confidence: {confidence}%)")
                elif winner == "B":
                    st.success(f"**Winner: Version B** (Confidence: {confidence}%)")
                else:
                    st.info("**Result: Tie** - Both versions are comparable")

                # Scores
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Version A Score",
                        f"{result.get('version_a_score', 0)}/100",
                    )
                with col2:
                    st.metric(
                        "Version B Score",
                        f"{result.get('version_b_score', 0)}/100",
                    )

                # Key differences
                if result.get("key_differences"):
                    st.markdown("### Key Differences")
                    for diff in result["key_differences"]:
                        st.markdown(f"- {diff}")

                # Recommendation
                if result.get("recommendation"):
                    st.markdown("### Recommendation")
                    st.info(result["recommendation"])

            except Exception as e:
                st.error(f"Comparison failed: {e}")
