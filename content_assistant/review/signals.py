"""Signal storage for content generation feedback.

Captures user feedback signals (ratings, checkboxes, implicit signals)
for learning and improving content generation over time.

SECURITY NOTE:
- Functions that modify user-specific data validate user ownership
- Backend agents use these for service operations with validated user_id
- UI should use API endpoints which enforce auth via JWT
"""

from typing import Optional
from uuid import UUID
import logging

from content_assistant.db.supabase_client import get_admin_client
from content_assistant.rag.embeddings import embed_text, EmbeddingError

logger = logging.getLogger(__name__)


class SignalError(Exception):
    """Raised when signal operations fail."""

    pass


class AuthorizationError(SignalError):
    """Raised when user doesn't have access to a generation."""

    pass


def _validate_user_owns_generation(
    generation_id: str,
    user_id: str,
    client=None
) -> bool:
    """Validate that a user owns a specific generation.

    Args:
        generation_id: ID of the generation
        user_id: ID of the user to validate
        client: Optional Supabase client

    Returns:
        True if user owns the generation

    Raises:
        AuthorizationError: If user doesn't own the generation
        SignalError: If generation not found
    """
    if client is None:
        client = get_admin_client()

    result = client.table("content_generations")\
        .select("user_id")\
        .eq("id", str(generation_id))\
        .execute()

    if not result.data:
        raise SignalError(f"Generation not found: {generation_id}")

    owner_id = result.data[0].get("user_id")
    if owner_id != user_id:
        logger.warning(
            f"Authorization failed: user {user_id} attempted to access "
            f"generation {generation_id} owned by {owner_id}"
        )
        raise AuthorizationError("You don't have access to this generation")

    return True


def store_generation_signals(
    brief: dict,
    preview: dict,
    content: str,
    platform: str,
    content_type: str,
    rating: Optional[int] = None,
    what_worked: Optional[list[str]] = None,
    what_needs_work: Optional[list[str]] = None,
    was_approved: bool = False,
    was_regenerated: bool = False,
    manual_edits: Optional[str] = None,
    user_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    variant: Optional[str] = None,
    api_cost_usd: Optional[float] = None,
) -> str:
    """Store a content generation with its signals.

    Args:
        brief: Content brief as dict
        preview: Content preview as dict
        content: Generated content text
        platform: Target platform
        content_type: Type of content
        rating: User rating 1-5 (optional)
        what_worked: List of positive feedback points
        what_needs_work: List of improvement areas
        was_approved: Whether content was approved
        was_regenerated: Whether content was regenerated
        manual_edits: Any manual edits made
        user_id: User identifier
        experiment_id: A/B experiment ID if applicable
        variant: Experiment variant if applicable
        api_cost_usd: API cost for generation

    Returns:
        str: UUID of the stored generation

    Raises:
        SignalError: If storage fails
    """
    try:
        client = get_admin_client()

        # Generate embeddings for similarity search later
        brief_embedding = None
        content_embedding = None

        try:
            # Create brief text for embedding
            brief_text = " ".join([
                brief.get("transformation", ""),
                brief.get("audience", ""),
                brief.get("pain_point", ""),
                brief.get("core_message", ""),
            ])
            if brief_text.strip():
                brief_embedding = embed_text(brief_text, input_type="document")

            # Embed the content
            if content and content.strip():
                content_embedding = embed_text(content, input_type="document")

        except EmbeddingError:
            # Embeddings are optional - continue without them
            pass

        data = {
            "brief": brief,
            "preview": preview,
            "content": content,
            "platform": platform,
            "content_type": content_type,
            "rating": rating,
            "what_worked": what_worked or [],
            "what_needs_work": what_needs_work or [],
            "was_approved": was_approved,
            "was_regenerated": was_regenerated,
            "manual_edits": manual_edits,
            "user_id": user_id,
            "experiment_id": experiment_id,
            "variant": variant,
            "api_cost_usd": api_cost_usd,
        }

        if brief_embedding:
            data["brief_embedding"] = brief_embedding

        if content_embedding:
            data["content_embedding"] = content_embedding

        result = client.table("content_generations").insert(data).execute()

        if not result.data:
            raise SignalError("No data returned after insert")

        return result.data[0]["id"]

    except SignalError:
        raise
    except Exception as e:
        raise SignalError(f"Failed to store generation: {e}") from e


def get_generation_by_id(
    generation_id: str | UUID,
    require_user_id: Optional[str] = None
) -> Optional[dict]:
    """Get a content generation by ID.

    Args:
        generation_id: UUID of the generation
        require_user_id: If provided, validates that this user owns the generation.
                        Use this for user-initiated requests to prevent unauthorized access.

    Returns:
        Generation data dict or None if not found

    Raises:
        AuthorizationError: If require_user_id is set and user doesn't own generation
        SignalError: If query fails
    """
    try:
        client = get_admin_client()

        # If user validation required, check ownership first
        if require_user_id:
            _validate_user_owns_generation(str(generation_id), require_user_id, client)

        result = (
            client.table("content_generations")
            .select("*")
            .eq("id", str(generation_id))
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    except AuthorizationError:
        raise
    except Exception as e:
        raise SignalError(f"Failed to get generation: {e}") from e


def update_generation_rating(
    generation_id: str | UUID,
    rating: int,
    what_worked: Optional[list[str]] = None,
    what_needs_work: Optional[list[str]] = None,
    require_user_id: Optional[str] = None,
) -> bool:
    """Update the rating and feedback for a generation.

    Args:
        generation_id: UUID of the generation
        rating: New rating 1-5
        what_worked: Updated positive feedback
        what_needs_work: Updated improvement areas
        require_user_id: If provided, validates that this user owns the generation.
                        Use this for user-initiated requests to prevent unauthorized access.

    Returns:
        True if update successful

    Raises:
        AuthorizationError: If require_user_id is set and user doesn't own generation
        SignalError: If update fails
    """
    if not 1 <= rating <= 5:
        raise SignalError("Rating must be between 1 and 5")

    try:
        client = get_admin_client()

        # If user validation required, check ownership first
        if require_user_id:
            _validate_user_owns_generation(str(generation_id), require_user_id, client)

        update_data = {"rating": rating}

        if what_worked is not None:
            update_data["what_worked"] = what_worked

        if what_needs_work is not None:
            update_data["what_needs_work"] = what_needs_work

        result = (
            client.table("content_generations")
            .update(update_data)
            .eq("id", str(generation_id))
            .execute()
        )

        return len(result.data) > 0

    except AuthorizationError:
        raise
    except Exception as e:
        raise SignalError(f"Failed to update rating: {e}") from e


def mark_generation_approved(
    generation_id: str | UUID,
    manual_edits: Optional[str] = None,
    require_user_id: Optional[str] = None,
) -> bool:
    """Mark a generation as approved.

    Args:
        generation_id: UUID of the generation
        manual_edits: Any manual edits made before approval
        require_user_id: If provided, validates that this user owns the generation.
                        Use this for user-initiated requests to prevent unauthorized access.

    Returns:
        True if update successful

    Raises:
        AuthorizationError: If require_user_id is set and user doesn't own generation
        SignalError: If update fails
    """
    try:
        client = get_admin_client()

        # If user validation required, check ownership first
        if require_user_id:
            _validate_user_owns_generation(str(generation_id), require_user_id, client)

        update_data = {"was_approved": True}

        if manual_edits:
            update_data["manual_edits"] = manual_edits

        result = (
            client.table("content_generations")
            .update(update_data)
            .eq("id", str(generation_id))
            .execute()
        )

        return len(result.data) > 0

    except AuthorizationError:
        raise
    except Exception as e:
        raise SignalError(f"Failed to mark approved: {e}") from e


def get_user_generations(
    user_id: str,
    limit: int = 20,
    platform: Optional[str] = None,
) -> list[dict]:
    """Get recent generations for a user.

    Args:
        user_id: User identifier
        limit: Maximum number of results
        platform: Optional platform filter

    Returns:
        List of generation dicts

    Raises:
        SignalError: If query fails
    """
    try:
        client = get_admin_client()

        query = (
            client.table("content_generations")
            .select("id, brief, preview, content, platform, content_type, rating, was_approved, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
        )

        if platform:
            query = query.eq("platform", platform)

        result = query.execute()

        return result.data or []

    except Exception as e:
        raise SignalError(f"Failed to get user generations: {e}") from e


def get_generation_stats(user_id: Optional[str] = None) -> dict:
    """Get statistics about content generations.

    Args:
        user_id: Optional user ID to filter stats

    Returns:
        Dict with generation statistics

    Raises:
        SignalError: If query fails
    """
    try:
        client = get_admin_client()

        # Total count
        count_query = client.table("content_generations").select("id", count="exact")
        if user_id:
            count_query = count_query.eq("user_id", user_id)
        count_result = count_query.execute()
        total = count_result.count or 0

        # Approved count
        approved_query = (
            client.table("content_generations")
            .select("id", count="exact")
            .eq("was_approved", True)
        )
        if user_id:
            approved_query = approved_query.eq("user_id", user_id)
        approved_result = approved_query.execute()
        approved = approved_result.count or 0

        # Average rating (for rated content)
        rated_query = (
            client.table("content_generations")
            .select("rating")
            .not_.is_("rating", "null")
        )
        if user_id:
            rated_query = rated_query.eq("user_id", user_id)
        rated_result = rated_query.execute()

        ratings = [r["rating"] for r in rated_result.data if r.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            "total_generations": total,
            "approved_generations": approved,
            "approval_rate": (approved / total * 100) if total > 0 else 0,
            "average_rating": round(avg_rating, 2),
            "rated_count": len(ratings),
        }

    except Exception as e:
        raise SignalError(f"Failed to get stats: {e}") from e
