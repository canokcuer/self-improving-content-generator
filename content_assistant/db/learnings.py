"""Database access for approved learnings."""

from __future__ import annotations

from typing import Optional

from content_assistant.db.supabase_client import get_client


class LearningsError(Exception):
    """Raised when learning retrieval fails."""


def get_approved_learnings(
    agent_name: str,
    topic: Optional[str] = None,
    learning_type: Optional[str] = None,
    limit: int = 5,
) -> list[dict]:
    """Fetch approved learnings for an agent.

    Args:
        agent_name: Agent identifier (e.g., "storytelling").
        topic: Optional topic filter to match content/summary.
        learning_type: Optional learning type filter.
        limit: Max number of learnings to return.

    Returns:
        List of approved learning rows.

    Raises:
        LearningsError: If the query fails.
    """
    try:
        client = get_client()
        query = client.table("agent_learnings").select(
            "id, learning_type, learning_content, learning_summary, confidence_score, times_applied, success_rate"
        )
        query = query.eq("agent_name", agent_name).eq("is_approved", True)

        if learning_type:
            query = query.eq("learning_type", learning_type)

        if topic:
            topic_filter = f"%{topic}%"
            query = query.or_(
                f"learning_content.ilike.{topic_filter},learning_summary.ilike.{topic_filter}"
            )

        result = (
            query.order("confidence_score", desc=True)
            .order("success_rate", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        raise LearningsError(f"Failed to fetch approved learnings: {exc}") from exc
