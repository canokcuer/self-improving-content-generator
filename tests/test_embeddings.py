"""Tests for embeddings module."""

import pytest
from unittest.mock import patch, MagicMock

from content_assistant.rag.embeddings import (
    embed_text,
    embed_texts,
    embed_query,
    embed_document,
    clear_client_cache,
    EmbeddingError,
)


class TestEmbedText:
    """Tests for embed_text function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_embed_text_returns_vector(self, mock_env_vars):
        """Test that embed_text returns a vector."""
        with patch("content_assistant.rag.embeddings.voyageai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.embeddings = [[0.1] * 1024]
            mock_client.embed.return_value = mock_result
            mock_client_class.return_value = mock_client

            embedding = embed_text("test text")

            assert isinstance(embedding, list)
            assert len(embedding) == 1024

    def test_embed_text_empty_raises_error(self, mock_env_vars):
        """Test that embedding empty text raises error."""
        with pytest.raises(EmbeddingError):
            embed_text("")

        with pytest.raises(EmbeddingError):
            embed_text("   ")

    def test_embed_text_uses_correct_input_type(self, mock_env_vars):
        """Test that embed_text passes correct input_type."""
        with patch("content_assistant.rag.embeddings.voyageai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.embeddings = [[0.1] * 1024]
            mock_client.embed.return_value = mock_result
            mock_client_class.return_value = mock_client

            embed_text("test", input_type="query")

            # Check that embed was called with input_type="query"
            call_kwargs = mock_client.embed.call_args[1]
            assert call_kwargs["input_type"] == "query"


class TestEmbedTexts:
    """Tests for embed_texts function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_embed_texts_returns_multiple_vectors(self, mock_env_vars):
        """Test that embed_texts returns vectors for all texts."""
        with patch("content_assistant.rag.embeddings.voyageai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.embeddings = [[0.1] * 1024, [0.2] * 1024, [0.3] * 1024]
            mock_client.embed.return_value = mock_result
            mock_client_class.return_value = mock_client

            embeddings = embed_texts(["text1", "text2", "text3"])

            assert len(embeddings) == 3
            for emb in embeddings:
                assert len(emb) == 1024

    def test_embed_texts_empty_list_returns_empty(self, mock_env_vars):
        """Test that empty list returns empty list."""
        embeddings = embed_texts([])
        assert embeddings == []

    def test_embed_texts_all_empty_raises_error(self, mock_env_vars):
        """Test that all empty texts raises error."""
        with pytest.raises(EmbeddingError):
            embed_texts(["", "   ", ""])


class TestEmbedQueryAndDocument:
    """Tests for embed_query and embed_document functions."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_embed_query_uses_query_type(self, mock_env_vars):
        """Test that embed_query uses query input type."""
        with patch("content_assistant.rag.embeddings.voyageai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.embeddings = [[0.1] * 1024]
            mock_client.embed.return_value = mock_result
            mock_client_class.return_value = mock_client

            embed_query("search query")

            call_kwargs = mock_client.embed.call_args[1]
            assert call_kwargs["input_type"] == "query"

    def test_embed_document_uses_document_type(self, mock_env_vars):
        """Test that embed_document uses document input type."""
        with patch("content_assistant.rag.embeddings.voyageai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.embeddings = [[0.1] * 1024]
            mock_client.embed.return_value = mock_result
            mock_client_class.return_value = mock_client

            embed_document("document content")

            call_kwargs = mock_client.embed.call_args[1]
            assert call_kwargs["input_type"] == "document"
