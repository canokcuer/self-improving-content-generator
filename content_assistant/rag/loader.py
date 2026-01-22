"""Document loader for parsing various file formats.

Supports:
- Plain text files (.txt, .md)
- PDF files (.pdf)
"""

from pathlib import Path
from typing import Optional

from PyPDF2 import PdfReader


class LoaderError(Exception):
    """Raised when document loading fails."""

    pass


def load_text_file(file_path: Path) -> str:
    """Load content from a plain text file.

    Args:
        file_path: Path to the text file

    Returns:
        str: File content

    Raises:
        LoaderError: If file cannot be read
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            return file_path.read_text(encoding="latin-1")
        except Exception as e:
            raise LoaderError(f"Failed to read text file {file_path}: {e}") from e
    except Exception as e:
        raise LoaderError(f"Failed to read text file {file_path}: {e}") from e


def load_pdf_file(file_path: Path) -> str:
    """Load content from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        str: Extracted text content

    Raises:
        LoaderError: If PDF cannot be read or parsed
    """
    try:
        reader = PdfReader(str(file_path))
        pages = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        if not pages:
            raise LoaderError(f"No text content found in PDF: {file_path}")

        return "\n\n".join(pages)
    except LoaderError:
        raise
    except Exception as e:
        raise LoaderError(f"Failed to read PDF file {file_path}: {e}") from e


def load_document(file_path: str | Path) -> str:
    """Load content from a document file.

    Automatically detects file type and uses appropriate loader.

    Args:
        file_path: Path to the document file

    Returns:
        str: Document content

    Raises:
        LoaderError: If file cannot be loaded
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix in [".txt", ".md"]:
        return load_text_file(path)
    elif suffix == ".pdf":
        return load_pdf_file(path)
    else:
        # Try as text file
        try:
            return load_text_file(path)
        except LoaderError:
            raise LoaderError(f"Unsupported file type: {suffix}")


def load_directory(
    dir_path: str | Path,
    extensions: Optional[list[str]] = None,
) -> dict[str, str]:
    """Load all documents from a directory.

    Args:
        dir_path: Path to the directory
        extensions: List of file extensions to include (e.g., ['.txt', '.md', '.pdf'])
                   If None, loads all supported types.

    Returns:
        dict: Mapping of filename to content

    Raises:
        LoaderError: If directory loading fails
    """
    if extensions is None:
        extensions = [".txt", ".md", ".pdf"]

    dir_path = Path(dir_path)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    if not dir_path.is_dir():
        raise LoaderError(f"Not a directory: {dir_path}")

    documents = {}

    for ext in extensions:
        for file_path in dir_path.glob(f"*{ext}"):
            try:
                content = load_document(file_path)
                documents[file_path.name] = content
            except Exception as e:
                # Log warning but continue with other files
                print(f"Warning: Failed to load {file_path}: {e}")

    return documents
