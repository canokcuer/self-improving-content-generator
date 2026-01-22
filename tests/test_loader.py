"""Tests for document loader module."""

import pytest
from unittest.mock import patch, MagicMock

from content_assistant.rag.loader import (
    load_text_file,
    load_document,
    load_directory,
)


class TestLoadTextFile:
    """Tests for load_text_file function."""

    def test_load_text_file_utf8(self, tmp_path):
        """Test loading UTF-8 text file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!", encoding="utf-8")

        content = load_text_file(test_file)

        assert content == "Hello, World!"

    def test_load_text_file_with_unicode(self, tmp_path):
        """Test loading file with unicode characters."""
        test_file = tmp_path / "unicode.txt"
        test_file.write_text("Hello, 世界! 🌍", encoding="utf-8")

        content = load_text_file(test_file)

        assert "世界" in content
        assert "🌍" in content


class TestLoadDocument:
    """Tests for load_document function."""

    def test_load_txt_file(self, tmp_path):
        """Test loading .txt file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content", encoding="utf-8")

        content = load_document(test_file)

        assert content == "Test content"

    def test_load_md_file(self, tmp_path):
        """Test loading .md file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Markdown\n\nContent here", encoding="utf-8")

        content = load_document(test_file)

        assert "# Markdown" in content

    def test_load_nonexistent_file_raises(self):
        """Test that loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_document("/nonexistent/path/file.txt")

    def test_load_pdf_file(self, tmp_path):
        """Test loading PDF file (mocked)."""
        test_file = tmp_path / "test.pdf"
        test_file.touch()

        with patch("content_assistant.rag.loader.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF content"
            mock_reader.return_value.pages = [mock_page]

            content = load_document(test_file)

            assert content == "PDF content"


class TestLoadDirectory:
    """Tests for load_directory function."""

    def test_load_directory_multiple_files(self, tmp_path):
        """Test loading multiple files from directory."""
        (tmp_path / "file1.txt").write_text("Content 1", encoding="utf-8")
        (tmp_path / "file2.md").write_text("Content 2", encoding="utf-8")
        (tmp_path / "ignored.jpg").touch()  # Should be ignored

        documents = load_directory(tmp_path)

        assert len(documents) == 2
        assert "file1.txt" in documents
        assert "file2.md" in documents
        assert "ignored.jpg" not in documents

    def test_load_directory_with_extension_filter(self, tmp_path):
        """Test loading with specific extensions."""
        (tmp_path / "file.txt").write_text("Text", encoding="utf-8")
        (tmp_path / "file.md").write_text("Markdown", encoding="utf-8")

        documents = load_directory(tmp_path, extensions=[".txt"])

        assert len(documents) == 1
        assert "file.txt" in documents

    def test_load_nonexistent_directory_raises(self):
        """Test that loading nonexistent directory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_directory("/nonexistent/directory")
