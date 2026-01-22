"""Signal-derived ranker for few-shot example selection.

Combines semantic similarity with signal scores to rank
examples for optimal few-shot learning.
"""

from content_assistant.db.supabase_client import get_admin_client
from content_assistant.rag.embeddings import embed_query, EmbeddingError


class RankerError(Exception):
    """Raised when ranking operations fail."""

    pass


def rank_examples(
    query_text: str,
    candidates: list[dict],
    similarity_weight: float = 0.5,
    rating_weight: float = 0.3,
    recency_weight: float = 0.2,
) -> list[dict]:
    """Rank candidate examples using combined scoring.

    Combines:
    - Semantic similarity to the query
    - User rating signals
    - Recency (more recent = slightly higher)

    Args:
        query_text: Text to find similar examples for
        candidates: List of candidate examples with rating, created_at
        similarity_weight: Weight for similarity score (0-1)
        rating_weight: Weight for rating score (0-1)
        recency_weight: Weight for recency score (0-1)

    Returns:
        Sorted list of candidates with combined scores

    Raises:
        RankerError: If ranking fails
    """
    if not candidates:
        return []

    # Normalize weights
    total_weight = similarity_weight + rating_weight + recency_weight
    if total_weight == 0:
        total_weight = 1
    sim_w = similarity_weight / total_weight
    rat_w = rating_weight / total_weight
    rec_w = recency_weight / total_weight

    try:
        # Generate query embedding for similarity
        query_embedding = None
        if query_text and query_text.strip():
            try:
                query_embedding = embed_query(query_text)
            except EmbeddingError:
                # Fall back to non-similarity ranking
                pass

        # Calculate scores for each candidate
        scored_candidates = []
        max_rating = 5.0

        # Get recency range
        from datetime import datetime

        now = datetime.utcnow()
        dates = []
        for c in candidates:
            created = c.get("created_at")
            if created:
                if isinstance(created, str):
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        dates.append(dt.replace(tzinfo=None))
                    except ValueError:
                        dates.append(now)
                else:
                    dates.append(created)

        oldest = min(dates) if dates else now
        date_range = (now - oldest).total_seconds() or 1

        for i, candidate in enumerate(candidates):
            # Similarity score (0-1)
            similarity_score = candidate.get("similarity", 0.5)

            # If we have embeddings, we could recalculate, but trust pre-computed
            if query_embedding and "content_embedding" in candidate:
                # Could compute cosine similarity here if needed
                pass

            # Rating score (0-1)
            rating = candidate.get("rating", 3)
            rating_score = (rating / max_rating) if rating else 0.6

            # Recency score (0-1, more recent = higher)
            created = candidate.get("created_at")
            if created:
                if isinstance(created, str):
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        created = dt.replace(tzinfo=None)
                    except ValueError:
                        created = now
                age_seconds = (now - created).total_seconds()
                recency_score = 1 - (age_seconds / date_range) if date_range > 0 else 1
            else:
                recency_score = 0.5

            # Combined score
            combined_score = (
                sim_w * similarity_score +
                rat_w * rating_score +
                rec_w * recency_score
            )

            scored_candidate = {
                **candidate,
                "combined_score": combined_score,
                "similarity_score": similarity_score,
                "rating_score": rating_score,
                "recency_score": recency_score,
            }
            scored_candidates.append(scored_candidate)

        # Sort by combined score descending
        scored_candidates.sort(key=lambda x: x["combined_score"], reverse=True)

        return scored_candidates

    except Exception as e:
        raise RankerError(f"Failed to rank examples: {e}") from e


def get_top_examples_for_brief(
    brief_text: str,
    platform: str,
    limit: int = 5,
    min_rating: int = 4,
) -> list[dict]:
    """Get top-ranked examples for a content brief.

    Combines database query with ranking for optimal results.

    Args:
        brief_text: Text representation of the brief
        platform: Target platform
        limit: Maximum examples to return
        min_rating: Minimum rating threshold

    Returns:
        List of top-ranked examples

    Raises:
        RankerError: If retrieval or ranking fails
    """
    try:
        # Get query embedding
        query_embedding = embed_query(brief_text)

        client = get_admin_client()

        # Use RPC for vector similarity search
        result = client.rpc(
            "match_content_generations",
            {
                "query_embedding": query_embedding,
                "min_rating": min_rating,
                "match_count": limit * 3,  # Get more for ranking
            },
        ).execute()

        candidates = result.data or []

        # Filter by platform
        candidates = [c for c in candidates if c.get("platform") == platform]

        # Rank and limit
        ranked = rank_examples(
            query_text=brief_text,
            candidates=candidates,
            similarity_weight=0.5,
            rating_weight=0.35,
            recency_weight=0.15,
        )

        return ranked[:limit]

    except EmbeddingError as e:
        raise RankerError(f"Failed to generate query embedding: {e}") from e
    except Exception as e:
        raise RankerError(f"Failed to get examples: {e}") from e


def explain_ranking(example: dict) -> str:
    """Generate explanation for why an example was ranked.

    Args:
        example: Ranked example with scores

    Returns:
        Human-readable explanation
    """
    combined = example.get("combined_score", 0)
    similarity = example.get("similarity_score", 0)
    rating = example.get("rating_score", 0)
    recency = example.get("recency_score", 0)

    lines = [
        f"Combined Score: {combined:.2f}",
        f"- Similarity: {similarity:.2f} (semantic match to your brief)",
        f"- Rating: {rating:.2f} (user feedback quality)",
        f"- Recency: {recency:.2f} (how recent the example is)",
    ]

    return "\n".join(lines)
