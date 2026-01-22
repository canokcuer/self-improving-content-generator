"""Tests for text chunker module."""

import pytest

from content_assistant.rag.chunker import (
    chunk_text,
    chunk_document,
    split_into_paragraphs,
    Chunk,
    ChunkerError,
)


class TestSplitIntoParagraphs:
    """Tests for split_into_paragraphs function."""

    def test_split_simple_paragraphs(self):
        """Test splitting text with simple paragraph breaks."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."

        paragraphs = split_into_paragraphs(text)

        assert len(paragraphs) == 3
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."
        assert paragraphs[2] == "Third paragraph."

    def test_split_handles_multiple_newlines(self):
        """Test handling of multiple newlines."""
        text = "Para 1.\n\n\n\nPara 2."

        paragraphs = split_into_paragraphs(text)

        assert len(paragraphs) == 2

    def test_split_filters_empty_paragraphs(self):
        """Test that empty paragraphs are filtered out."""
        text = "\n\n\nContent\n\n\n"

        paragraphs = split_into_paragraphs(text)

        assert len(paragraphs) == 1
        assert paragraphs[0] == "Content"


class TestChunkText:
    """Tests for chunk_text function."""

    def test_small_text_single_chunk(self, mock_env_vars):
        """Test that small text returns single chunk."""
        text = "This is a short text."

        chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)

        assert len(chunks) == 1
        assert chunks[0].content == text

    def test_chunk_indices_sequential(self, mock_env_vars):
        """Test that chunk indices are sequential."""
        text = "Para 1.\n\n" * 20  # Long enough for multiple chunks

        chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)

        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_chunks_have_required_fields(self, mock_env_vars):
        """Test that chunks have all required fields."""
        text = "Test content.\n\nMore content."

        chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)

        for chunk in chunks:
            assert isinstance(chunk, Chunk)
            assert isinstance(chunk.content, str)
            assert isinstance(chunk.index, int)
            assert isinstance(chunk.start_char, int)
            assert isinstance(chunk.end_char, int)
            assert chunk.length > 0

    def test_empty_text_returns_empty_list(self, mock_env_vars):
        """Test that empty text returns empty list."""
        chunks = chunk_text("", chunk_size=500, chunk_overlap=50)
        assert chunks == []

        chunks = chunk_text("   ", chunk_size=500, chunk_overlap=50)
        assert chunks == []

    def test_invalid_overlap_raises_error(self, mock_env_vars):
        """Test that overlap >= size raises error."""
        with pytest.raises(ChunkerError):
            chunk_text("test", chunk_size=100, chunk_overlap=100)

        with pytest.raises(ChunkerError):
            chunk_text("test", chunk_size=100, chunk_overlap=150)


class TestChunkDocument:
    """Tests for chunk_document function."""

    def test_chunk_document_yields_dicts(self, mock_env_vars):
        """Test that chunk_document yields proper dicts."""
        content = "Test content for chunking.\n\nMore content here."
        source = "test.md"

        chunks = list(chunk_document(content, source, chunk_size=500, chunk_overlap=50))

        assert len(chunks) >= 1
        for chunk in chunks:
            assert "content" in chunk
            assert "source" in chunk
            assert "chunk_index" in chunk
            assert "metadata" in chunk
            assert chunk["source"] == source

    def test_chunk_document_metadata_has_positions(self, mock_env_vars):
        """Test that metadata includes character positions."""
        content = "Test content."
        source = "test.md"

        chunks = list(chunk_document(content, source, chunk_size=500, chunk_overlap=50))

        assert len(chunks) == 1
        assert "start_char" in chunks[0]["metadata"]
        assert "end_char" in chunks[0]["metadata"]
        assert "length" in chunks[0]["metadata"]
