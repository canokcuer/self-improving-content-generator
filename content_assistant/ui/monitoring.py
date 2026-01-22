"""Monitoring dashboard for API costs and usage.

Tracks API costs, usage patterns, and budget management.
"""

import streamlit as st
from datetime import datetime, timedelta

from content_assistant.db.supabase_client import get_admin_client


def render_monitoring_dashboard() -> None:
    """Render the monitoring dashboard."""
    st.header("Monitoring Dashboard")

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


def _render_cost_overview(start_date, end_date) -> None:
    """Render API cost overview."""
    st.subheader("API Costs")

    try:
        client = get_admin_client()

        # Get cost data
        result = client.rpc(
            "get_cost_summary",
            {
                "start_date": start_date.isoformat(),
                "end_date": (end_date + timedelta(days=1)).isoformat(),
            },
        ).execute()

        costs = result.data or []

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
            st.warning(f"⚠️ Approaching monthly budget (${monthly_budget})")

    except Exception as e:
        st.error(f"Failed to load costs: {e}")


def _render_generation_stats() -> None:
    """Render content generation statistics."""
    st.subheader("Generation Statistics")

    try:
        client = get_admin_client()

        # Total generations
        total_result = client.table("content_generations").select("id", count="exact").execute()
        total = total_result.count or 0

        # Approved generations
        approved_result = (
            client.table("content_generations")
            .select("id", count="exact")
            .eq("was_approved", True)
            .execute()
        )
        approved = approved_result.count or 0

        # Average rating
        rated_result = (
            client.table("content_generations")
            .select("rating")
            .not_.is_("rating", "null")
            .execute()
        )
        ratings = [r["rating"] for r in rated_result.data if r.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

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
        st.markdown("### By Platform")
        platform_result = (
            client.table("content_generations")
            .select("platform")
            .execute()
        )

        if platform_result.data:
            platforms = {}
            for row in platform_result.data:
                p = row.get("platform", "unknown")
                platforms[p] = platforms.get(p, 0) + 1

            cols = st.columns(len(platforms))
            for i, (platform, count) in enumerate(sorted(platforms.items(), key=lambda x: -x[1])):
                with cols[i % len(cols)]:
                    st.metric(platform.title(), count)

    except Exception as e:
        st.error(f"Failed to load stats: {e}")


def _render_recent_activity() -> None:
    """Render recent activity log."""
    st.subheader("Recent Activity")

    try:
        client = get_admin_client()

        # Get recent generations
        result = (
            client.table("content_generations")
            .select("id, platform, content_type, rating, was_approved, created_at")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        generations = result.data or []

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
                st.markdown(gen.get("platform", "").title())

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
        st.error(f"Failed to load activity: {e}")


def log_api_cost(
    service: str,
    operation: str,
    tokens_input: int,
    tokens_output: int,
    cost_usd: float,
    metadata: dict = None,
) -> None:
    """Log an API cost entry.

    Args:
        service: Service name (anthropic, voyage)
        operation: Operation name
        tokens_input: Input tokens used
        tokens_output: Output tokens used
        cost_usd: Cost in USD
        metadata: Optional additional metadata
    """
    try:
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
