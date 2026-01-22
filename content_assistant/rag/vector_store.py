"""Vector store operations for Supabase pgvector.

Handles storing and retrieving embeddings from the knowledge_chunks table.
"""

from typing import Optional
from uuid import UUID

from content_assistant.db.supabase_client import get_admin_client


class VectorStoreError(Exception):
    """Raised when vector store operations fail."""

    pass


def store_chunk(
    content: str,
    source: str,
    chunk_index: int,
    embedding: list[float],
    metadata: Optional[dict] = None,
) -> str:
    """Store a knowledge chunk with its embedding.

    Args:
        content: Chunk text content
        source: Source document identifier
        chunk_index: Index of chunk within source
        embedding: Vector embedding (1024 dimensions)
        metadata: Optional metadata dict

    Returns:
        str: UUID of the stored chunk

    Raises:
        VectorStoreError: If storage fails
    """
    try:
        client = get_admin_client()

        data = {
            "content": content,
            "source": source,
            "chunk_index": chunk_index,
            "embedding": embedding,
            "metadata": metadata or {},
        }

        result = client.table("knowledge_chunks").upsert(
            data,
            on_conflict="source,chunk_index",
        ).execute()

        if not result.data:
            raise VectorStoreError("No data returned after insert")

        return result.data[0]["id"]

    except VectorStoreError:
        raise
    except Exception as e:
        raise VectorStoreError(f"Failed to store chunk: {e}") from e


def store_chunks(chunks: list[dict]) -> list[str]:
    """Store multiple knowledge chunks.

    Args:
        chunks: List of chunk dicts with content, source, chunk_index,
                embedding, and optional metadata

    Returns:
        List of UUIDs for stored chunks

    Raises:
        VectorStoreError: If storage fails
    """
    if not chunks:
        return []

    try:
        client = get_admin_client()

        # Prepare data for bulk insert
        data = [
            {
                "content": chunk["content"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "embedding": chunk["embedding"],
                "metadata": chunk.get("metadata", {}),
            }
            for chunk in chunks
        ]

        result = client.table("knowledge_chunks").upsert(
            data,
            on_conflict="source,chunk_index",
        ).execute()

        if not result.data:
            raise VectorStoreError("No data returned after bulk insert")

        return [row["id"] for row in result.data]

    except VectorStoreError:
        raise
    except Exception as e:
        raise VectorStoreError(f"Failed to store chunks: {e}") from e


def search_similar(
    query_embedding: list[float],
    match_threshold: float = 0.7,
    match_count: int = 5,
    source_filter: Optional[str] = None,
) -> list[dict]:
    """Search for similar knowledge chunks.

    Args:
        query_embedding: Query vector (1024 dimensions)
        match_threshold: Minimum similarity score (0-1)
        match_count: Maximum number of results
        source_filter: Optional source to filter by

    Returns:
        List of matching chunks with similarity scores

    Raises:
        VectorStoreError: If search fails
    """
    try:
        client = get_admin_client()

        result = client.rpc(
            "match_knowledge_chunks",
            {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
            },
        ).execute()

        matches = result.data or []

        # Apply source filter if provided
        if source_filter:
            matches = [m for m in matches if m["source"] == source_filter]

        return matches

    except Exception as e:
        raise VectorStoreError(f"Failed to search similar chunks: {e}") from e


def get_chunk_by_id(chunk_id: str | UUID) -> Optional[dict]:
    """Get a specific chunk by ID.

    Args:
        chunk_id: UUID of the chunk

    Returns:
        Chunk data dict or None if not found

    Raises:
        VectorStoreError: If query fails
    """
    try:
        client = get_admin_client()

        result = (
            client.table("knowledge_chunks")
            .select("*")
            .eq("id", str(chunk_id))
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    except Exception as e:
        raise VectorStoreError(f"Failed to get chunk: {e}") from e


def get_chunks_by_source(source: str) -> list[dict]:
    """Get all chunks from a specific source.

    Args:
        source: Source document identifier

    Returns:
        List of chunk data dicts ordered by chunk_index

    Raises:
        VectorStoreError: If query fails
    """
    try:
        client = get_admin_client()

        result = (
            client.table("knowledge_chunks")
            .select("*")
            .eq("source", source)
            .order("chunk_index")
            .execute()
        )

        return result.data or []

    except Exception as e:
        raise VectorStoreError(f"Failed to get chunks by source: {e}") from e


def delete_source(source: str) -> int:
    """Delete all chunks from a specific source.

    Args:
        source: Source document identifier

    Returns:
        Number of deleted chunks

    Raises:
        VectorStoreError: If deletion fails
    """
    try:
        client = get_admin_client()

        # First count how many we'll delete
        count_result = (
            client.table("knowledge_chunks")
            .select("id", count="exact")
            .eq("source", source)
            .execute()
        )
        count = count_result.count or 0

        # Delete
        client.table("knowledge_chunks").delete().eq("source", source).execute()

        return count

    except Exception as e:
        raise VectorStoreError(f"Failed to delete source: {e}") from e


def get_all_sources() -> list[str]:
    """Get list of all unique sources in the knowledge base.

    Returns:
        List of source identifiers

    Raises:
        VectorStoreError: If query fails
    """
    try:
        client = get_admin_client()

        result = (
            client.table("knowledge_chunks")
            .select("source")
            .execute()
        )

        # Get unique sources
        sources = set(row["source"] for row in result.data or [])
        return sorted(sources)

    except Exception as e:
        raise VectorStoreError(f"Failed to get sources: {e}") from e


def get_chunk_count() -> int:
    """Get total number of chunks in the knowledge base.

    Returns:
        Total chunk count

    Raises:
        VectorStoreError: If query fails
    """
    try:
        client = get_admin_client()

        result = (
            client.table("knowledge_chunks")
            .select("id", count="exact")
            .execute()
        )

        return result.count or 0

    except Exception as e:
        raise VectorStoreError(f"Failed to get chunk count: {e}") from e
