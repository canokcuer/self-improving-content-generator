"""Voyage AI embedding module for generating vector embeddings.

Uses voyage-3-lite model for 1024-dimensional embeddings.
"""

from functools import lru_cache
from typing import Optional

import voyageai

from content_assistant.config import get_config


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""

    pass


@lru_cache(maxsize=1)
def get_voyage_client() -> voyageai.Client:
    """Get cached Voyage AI client.

    Returns:
        voyageai.Client: Configured client instance
    """
    config = get_config()
    return voyageai.Client(api_key=config.voyage_api_key)


def embed_text(
    text: str,
    model: Optional[str] = None,
    input_type: str = "document",
) -> list[float]:
    """Generate embedding for a single text.

    Args:
        text: Text to embed
        model: Model name (default from config)
        input_type: Either "document" (for storage) or "query" (for search)

    Returns:
        List of floats representing the embedding vector (1024 dimensions)

    Raises:
        EmbeddingError: If embedding generation fails
    """
    if not text or not text.strip():
        raise EmbeddingError("Cannot embed empty text")

    try:
        config = get_config()
        model = model or config.voyage_model
        client = get_voyage_client()

        result = client.embed(
            texts=[text],
            model=model,
            input_type=input_type,
            output_dimension=config.embedding_dimension,
        )

        if not result.embeddings or len(result.embeddings) == 0:
            raise EmbeddingError("No embedding returned from Voyage AI")

        return result.embeddings[0]

    except EmbeddingError:
        raise
    except Exception as e:
        raise EmbeddingError(f"Failed to generate embedding: {e}") from e


def embed_texts(
    texts: list[str],
    model: Optional[str] = None,
    input_type: str = "document",
    batch_size: int = 128,
) -> list[list[float]]:
    """Generate embeddings for multiple texts.

    Args:
        texts: List of texts to embed
        model: Model name (default from config)
        input_type: Either "document" (for storage) or "query" (for search)
        batch_size: Number of texts to embed per API call

    Returns:
        List of embedding vectors

    Raises:
        EmbeddingError: If embedding generation fails
    """
    if not texts:
        return []

    # Filter empty texts but track their positions
    non_empty_indices = [i for i, t in enumerate(texts) if t and t.strip()]
    non_empty_texts = [texts[i] for i in non_empty_indices]

    if not non_empty_texts:
        raise EmbeddingError("All texts are empty")

    try:
        config = get_config()
        model = model or config.voyage_model
        client = get_voyage_client()

        all_embeddings = []

        # Process in batches
        for i in range(0, len(non_empty_texts), batch_size):
            batch = non_empty_texts[i : i + batch_size]

            result = client.embed(
                texts=batch,
                model=model,
                input_type=input_type,
                output_dimension=config.embedding_dimension,
            )

            if not result.embeddings:
                raise EmbeddingError(f"No embeddings returned for batch {i // batch_size}")

            all_embeddings.extend(result.embeddings)

        # Reconstruct full list with None for empty texts
        if len(non_empty_indices) == len(texts):
            return all_embeddings

        full_embeddings: list[list[float]] = [[] for _ in texts]
        for idx, embedding in zip(non_empty_indices, all_embeddings):
            full_embeddings[idx] = embedding

        return full_embeddings

    except EmbeddingError:
        raise
    except Exception as e:
        raise EmbeddingError(f"Failed to generate embeddings: {e}") from e


def embed_query(query: str, model: Optional[str] = None) -> list[float]:
    """Generate embedding for a search query.

    Uses "query" input type for better search performance.

    Args:
        query: Search query text
        model: Model name (default from config)

    Returns:
        Embedding vector

    Raises:
        EmbeddingError: If embedding generation fails
    """
    return embed_text(query, model=model, input_type="query")


def embed_document(text: str, model: Optional[str] = None) -> list[float]:
    """Generate embedding for a document.

    Uses "document" input type for storage.

    Args:
        text: Document text
        model: Model name (default from config)

    Returns:
        Embedding vector

    Raises:
        EmbeddingError: If embedding generation fails
    """
    return embed_text(text, model=model, input_type="document")


def clear_client_cache():
    """Clear the Voyage client cache. Useful for testing."""
    get_voyage_client.cache_clear()
