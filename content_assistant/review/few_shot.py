"""Few-shot example retriever for content generation.

Retrieves similar high-performing content examples to use as
few-shot examples in prompts, improving generation quality.
"""

from typing import Optional

from content_assistant.db.supabase_client import get_admin_client
from content_assistant.rag.embeddings import embed_query, EmbeddingError


class FewShotError(Exception):
    """Raised when few-shot retrieval fails."""

    pass


def get_few_shot_examples(
    brief_text: str,
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    min_rating: int = 4,
    max_examples: int = 3,
) -> list[dict]:
    """Retrieve similar high-performing examples for few-shot learning.

    Uses vector similarity to find past generations that are semantically
    similar to the current brief, filtered by minimum rating.

    Args:
        brief_text: Text representation of the current brief
        platform: Optional platform filter (instagram, linkedin, etc.)
        content_type: Optional content type filter (post, article, etc.)
        min_rating: Minimum rating threshold (1-5)
        max_examples: Maximum number of examples to return

    Returns:
        List of example dicts with content, brief, rating, and similarity

    Raises:
        FewShotError: If retrieval fails
    """
    if not brief_text or not brief_text.strip():
        return []

    try:
        # Generate embedding for the brief
        query_embedding = embed_query(brief_text)

        client = get_admin_client()

        # Use the match_content_generations RPC function
        result = client.rpc(
            "match_content_generations",
            {
                "query_embedding": query_embedding,
                "min_rating": min_rating,
                "match_count": max_examples * 2,  # Fetch more to allow filtering
            },
        ).execute()

        examples = result.data or []

        # Apply additional filters
        if platform:
            examples = [e for e in examples if e.get("platform") == platform]

        if content_type:
            # content_type might be in the brief JSON
            examples = [
                e for e in examples
                if e.get("brief", {}).get("content_type") == content_type
            ]

        # Limit to requested count
        examples = examples[:max_examples]

        return examples

    except EmbeddingError as e:
        raise FewShotError(f"Failed to generate query embedding: {e}") from e
    except Exception as e:
        raise FewShotError(f"Failed to retrieve few-shot examples: {e}") from e


def get_examples_by_platform(
    platform: str,
    min_rating: int = 4,
    limit: int = 10,
) -> list[dict]:
    """Get top-rated examples for a specific platform.

    Args:
        platform: Platform to filter by
        min_rating: Minimum rating threshold
        limit: Maximum number of examples

    Returns:
        List of high-performing examples for the platform

    Raises:
        FewShotError: If retrieval fails
    """
    try:
        client = get_admin_client()

        result = (
            client.table("content_generations")
            .select("id, content, brief, platform, rating, created_at")
            .eq("platform", platform)
            .eq("was_approved", True)
            .gte("rating", min_rating)
            .order("rating", desc=True)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data or []

    except Exception as e:
        raise FewShotError(f"Failed to get examples by platform: {e}") from e


def get_recent_approved_examples(
    limit: int = 10,
    days: int = 30,
) -> list[dict]:
    """Get recently approved examples within a time window.

    Args:
        limit: Maximum number of examples
        days: Number of days to look back

    Returns:
        List of recent approved examples

    Raises:
        FewShotError: If retrieval fails
    """
    try:
        from datetime import datetime, timedelta

        client = get_admin_client()
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        result = (
            client.table("content_generations")
            .select("id, content, brief, platform, rating, created_at")
            .eq("was_approved", True)
            .gte("created_at", cutoff_date)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data or []

    except Exception as e:
        raise FewShotError(f"Failed to get recent examples: {e}") from e


def format_examples_for_prompt(examples: list[dict]) -> str:
    """Format examples for inclusion in generation prompts.

    Args:
        examples: List of example dicts

    Returns:
        Formatted string for prompt injection
    """
    if not examples:
        return ""

    lines = ["## High-Performing Examples (for style reference)", ""]

    for i, example in enumerate(examples, 1):
        rating = example.get("rating", "N/A")
        platform = example.get("platform", "unknown")
        content = example.get("content", "")

        lines.extend([
            f"### Example {i} (Platform: {platform}, Rating: {rating}/5)",
            "",
            content,
            "",
        ])

    return "\n".join(lines)
