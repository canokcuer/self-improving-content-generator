"""Knowledge base loader combining loader, chunker, embedder, and vector store.

Provides end-to-end functionality for loading documents into the RAG system.
"""

from pathlib import Path
from typing import Optional

from content_assistant.config import get_config
from content_assistant.rag.loader import load_document, LoaderError
from content_assistant.rag.chunker import chunk_document, ChunkerError
from content_assistant.rag.embeddings import embed_texts, EmbeddingError
from content_assistant.rag.vector_store import store_chunks, delete_source, VectorStoreError


class KnowledgeBaseError(Exception):
    """Raised when knowledge base operations fail."""

    pass


def load_file_to_knowledge_base(
    file_path: str | Path,
    source_name: Optional[str] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    replace_existing: bool = True,
) -> dict:
    """Load a single file into the knowledge base.

    Args:
        file_path: Path to the file
        source_name: Override for source identifier (default: filename)
        chunk_size: Override for chunk size
        chunk_overlap: Override for chunk overlap
        replace_existing: If True, delete existing chunks for this source first

    Returns:
        dict with keys: source, chunks_created, chunks_embedded

    Raises:
        KnowledgeBaseError: If loading fails
    """
    file_path = Path(file_path)
    source = source_name or file_path.name

    try:
        # Load document
        print(f"Loading {file_path}...")
        content = load_document(file_path)

        if not content.strip():
            raise KnowledgeBaseError(f"Empty content in {file_path}")

        # Delete existing if requested
        if replace_existing:
            deleted = delete_source(source)
            if deleted > 0:
                print(f"  Deleted {deleted} existing chunks for {source}")

        # Chunk document
        print("  Chunking...")
        chunks = list(chunk_document(content, source, chunk_size, chunk_overlap))

        if not chunks:
            raise KnowledgeBaseError(f"No chunks created from {file_path}")

        print(f"  Created {len(chunks)} chunks")

        # Generate embeddings
        print("  Generating embeddings...")
        texts = [chunk["content"] for chunk in chunks]
        embeddings = embed_texts(texts, input_type="document")

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        # Store in vector database
        print("  Storing in vector database...")
        ids = store_chunks(chunks)

        print(f"  Done! Stored {len(ids)} chunks for {source}")

        return {
            "source": source,
            "chunks_created": len(chunks),
            "chunks_embedded": len(ids),
        }

    except (LoaderError, ChunkerError, EmbeddingError, VectorStoreError) as e:
        raise KnowledgeBaseError(f"Failed to load {file_path}: {e}") from e
    except Exception as e:
        raise KnowledgeBaseError(f"Unexpected error loading {file_path}: {e}") from e


def load_directory_to_knowledge_base(
    dir_path: str | Path,
    extensions: Optional[list[str]] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    replace_existing: bool = True,
) -> dict:
    """Load all documents from a directory into the knowledge base.

    Args:
        dir_path: Path to directory
        extensions: File extensions to include
        chunk_size: Override for chunk size
        chunk_overlap: Override for chunk overlap
        replace_existing: If True, delete existing chunks for each source

    Returns:
        dict with keys: files_processed, total_chunks, errors

    Raises:
        KnowledgeBaseError: If directory loading fails
    """
    dir_path = Path(dir_path)

    if extensions is None:
        extensions = [".txt", ".md", ".pdf"]

    results = {
        "files_processed": 0,
        "total_chunks": 0,
        "errors": [],
        "details": [],
    }

    try:
        # Get all matching files
        files = []
        for ext in extensions:
            files.extend(dir_path.glob(f"*{ext}"))

        if not files:
            print(f"No files found in {dir_path} with extensions {extensions}")
            return results

        print(f"Found {len(files)} files to process")

        for file_path in sorted(files):
            try:
                result = load_file_to_knowledge_base(
                    file_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    replace_existing=replace_existing,
                )
                results["files_processed"] += 1
                results["total_chunks"] += result["chunks_created"]
                results["details"].append(result)
            except KnowledgeBaseError as e:
                error_msg = f"{file_path.name}: {e}"
                print(f"  Error: {error_msg}")
                results["errors"].append(error_msg)

        print(f"\nSummary: {results['files_processed']} files, {results['total_chunks']} chunks")
        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")

        return results

    except Exception as e:
        raise KnowledgeBaseError(f"Failed to load directory {dir_path}: {e}") from e


def load_default_knowledge_base(replace_existing: bool = True) -> dict:
    """Load the default knowledge base from the project's knowledge directory.

    Args:
        replace_existing: If True, delete existing chunks for each source

    Returns:
        dict with loading results
    """
    config = get_config()
    knowledge_dir = Path(config.knowledge_dir)

    if not knowledge_dir.exists():
        raise KnowledgeBaseError(f"Knowledge directory not found: {knowledge_dir}")

    return load_directory_to_knowledge_base(
        knowledge_dir,
        extensions=[".md", ".txt"],
        replace_existing=replace_existing,
    )


def search_knowledge(
    query: str,
    match_threshold: float = 0.7,
    match_count: int = 5,
) -> list[dict]:
    """Search the knowledge base for relevant content.

    Args:
        query: Search query text
        match_threshold: Minimum similarity score (0-1)
        match_count: Maximum number of results

    Returns:
        List of matching chunks with similarity scores
    """
    from content_assistant.rag.embeddings import embed_query
    from content_assistant.rag.vector_store import search_similar

    try:
        # Generate query embedding
        query_embedding = embed_query(query)

        # Search vector store
        results = search_similar(
            query_embedding,
            match_threshold=match_threshold,
            match_count=match_count,
        )

        return results

    except (EmbeddingError, VectorStoreError) as e:
        raise KnowledgeBaseError(f"Search failed: {e}") from e
