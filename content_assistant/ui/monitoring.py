"""Monitoring dashboard for API costs and usage.

Tracks API costs, usage patterns, and budget management.

SECURITY NOTE: This is an admin-only page. Access control is enforced
via the API endpoints which require admin role.
"""

import streamlit as st
from datetime import datetime, timedelta
import logging

from content_assistant.services.api_client import api_client

logger = logging.getLogger(__name__)


def render_monitoring_dashboard() -> None:
    """Render the monitoring dashboard."""
    st.header("Monitoring Dashboard")

    # Check admin access first
    if not _check_admin_access():
        st.error("Access denied. Admin privileges required.")
        return

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
        )

    st.divider()

    # Cost overview
    _render_cost_overview(start_date, end_date)

    st.divider()

    # Generation stats
    _render_generation_stats()

    st.divider()

    # Recent activity
    _render_recent_activity()


def _check_admin_access() -> bool:
    """Check if current user has admin access via API."""
    try:
        response = api_client.check_admin_status()
        if response.success and response.data:
            return response.data.get("is_admin", False)
        return False
    except Exception as e:
        logger.error(f"Failed to check admin status: {e}")
        return False


def _render_cost_overview(start_date, end_date) -> None:
    """Render API cost overview."""
    st.subheader("API Costs")

    try:
        response = api_client.get_admin_costs(
            start_date=start_date.isoformat(),
            end_date=(end_date + timedelta(days=1)).isoformat(),
        )

        if not response.success:
            st.error("Failed to load cost data")
            return

        costs = response.data or []

        if not costs:
            st.info("No API costs recorded for this period.")
            return

        # Display by service
        total_cost = 0
        cols = st.columns(len(costs) + 1)

        for i, cost in enumerate(costs):
            service = cost.get("service", "Unknown")
            service_cost = float(cost.get("total_cost", 0))
            total_cost += service_cost

            with cols[i]:
                st.metric(
                    service.title(),
                    f"${service_cost:.4f}",
                    delta=f"{cost.get('operation_count', 0)} calls",
                )

        with cols[-1]:
            st.metric("Total", f"${total_cost:.4f}")

        # Budget warning
        monthly_budget = 50.0  # Default budget
        if total_cost > monthly_budget * 0.8:
            st.warning(f"Approaching monthly budget (${monthly_budget})")

    except Exception as e:
        logger.error(f"Failed to load costs: {e}")
        st.error("Failed to load cost data")


def _render_generation_stats() -> None:
    """Render content generation statistics."""
    st.subheader("Generation Statistics")

    try:
        response = api_client.get_admin_stats()

        if not response.success:
            st.error("Failed to load statistics")
            return

        stats = response.data or {}

        total = stats.get("total_generations", 0)
        approved = stats.get("approved_count", 0)
        avg_rating = stats.get("avg_rating", 0) or 0

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Generations", total)

        with col2:
            st.metric("Approved", approved)

        with col3:
            rate = (approved / total * 100) if total > 0 else 0
            st.metric("Approval Rate", f"{rate:.1f}%")

        with col4:
            st.metric("Avg Rating", f"{avg_rating:.1f}/5")

        # Platform breakdown
        platform_breakdown = stats.get("platform_breakdown", {})
        if platform_breakdown:
            st.markdown("### By Platform")
            cols = st.columns(len(platform_breakdown))
            for i, (platform, count) in enumerate(sorted(platform_breakdown.items(), key=lambda x: -x[1])):
                with cols[i % len(cols)]:
                    st.metric(platform.title() if platform else "Unknown", count)

    except Exception as e:
        logger.error(f"Failed to load stats: {e}")
        st.error("Failed to load statistics")


def _render_recent_activity() -> None:
    """Render recent activity log."""
    st.subheader("Recent Activity")

    try:
        # Use admin stats endpoint which includes recent activity
        response = api_client.get_admin_stats()

        if not response.success:
            st.info("No recent activity available.")
            return

        stats = response.data or {}
        generations = stats.get("recent_generations", [])

        if not generations:
            st.info("No recent activity.")
            return

        # Display as table
        for gen in generations:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                created = gen.get("created_at", "")[:16].replace("T", " ")
                st.markdown(f"**{created}**")

            with col2:
                platform = gen.get("platform", "")
                st.markdown(platform.title() if platform else "—")

            with col3:
                rating = gen.get("rating")
                if rating:
                    st.markdown("⭐" * rating)
                else:
                    st.markdown("—")

            with col4:
                if gen.get("was_approved"):
                    st.markdown("✅")
                else:
                    st.markdown("—")

    except Exception as e:
        logger.error(f"Failed to load activity: {e}")
        st.error("Failed to load activity")


def log_api_cost(
    service: str,
    operation: str,
    tokens_input: int,
    tokens_output: int,
    cost_usd: float,
    metadata: dict = None,
) -> None:
    """Log an API cost entry.

    SECURITY NOTE: This function is for BACKEND USE ONLY.
    It uses admin client because cost logging happens during agent
    operations, not from user-facing UI code.

    Args:
        service: Service name (anthropic, voyage)
        operation: Operation name
        tokens_input: Input tokens used
        tokens_output: Output tokens used
        cost_usd: Cost in USD
        metadata: Optional additional metadata
    """
    try:
        # Import here to avoid circular imports and keep admin_client
        # usage isolated to this backend-only function
        from content_assistant.db.supabase_client import get_admin_client

        client = get_admin_client()

        client.table("api_costs").insert({
            "service": service,
            "operation": operation,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost_usd": cost_usd,
            "metadata": metadata or {},
        }).execute()

    except Exception:
        pass  # Don't fail on logging errors
