"""RAG (Retrieval-Augmented Generation) pipeline components."""

from content_assistant.rag.loader import load_document, load_directory, LoaderError
from content_assistant.rag.chunker import chunk_text, chunk_document, Chunk, ChunkerError
from content_assistant.rag.embeddings import (
    embed_text,
    embed_texts,
    embed_query,
    embed_document,
    EmbeddingError,
)
from content_assistant.rag.vector_store import (
    store_chunk,
    store_chunks,
    search_similar,
    VectorStoreError,
)
from content_assistant.rag.knowledge_base import (
    load_file_to_knowledge_base,
    load_directory_to_knowledge_base,
    load_default_knowledge_base,
    search_knowledge,
    KnowledgeBaseError,
)

__all__ = [
    # Loader
    "load_document",
    "load_directory",
    "LoaderError",
    # Chunker
    "chunk_text",
    "chunk_document",
    "Chunk",
    "ChunkerError",
    # Embeddings
    "embed_text",
    "embed_texts",
    "embed_query",
    "embed_document",
    "EmbeddingError",
    # Vector Store
    "store_chunk",
    "store_chunks",
    "search_similar",
    "VectorStoreError",
    # Knowledge Base
    "load_file_to_knowledge_base",
    "load_directory_to_knowledge_base",
    "load_default_knowledge_base",
    "search_knowledge",
    "KnowledgeBaseError",
]
