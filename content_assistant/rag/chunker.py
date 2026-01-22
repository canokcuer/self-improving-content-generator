"""Text chunking module with overlapping chunks and paragraph-aware breaking.

Creates chunks suitable for embedding and retrieval.
"""

import re
from dataclasses import dataclass
from typing import Iterator

from content_assistant.config import get_config


class ChunkerError(Exception):
    """Raised when text chunking fails."""

    pass


@dataclass
class Chunk:
    """A text chunk with metadata."""

    content: str
    index: int
    start_char: int
    end_char: int

    @property
    def length(self) -> int:
        """Return chunk length in characters."""
        return len(self.content)


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs.

    Args:
        text: Input text

    Returns:
        List of paragraphs (non-empty)
    """
    # Split on multiple newlines (paragraph breaks)
    paragraphs = re.split(r"\n\s*\n", text)
    # Filter empty and clean up whitespace
    return [p.strip() for p in paragraphs if p.strip()]


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    """Split text into overlapping chunks.

    Uses paragraph-aware breaking when possible to avoid splitting
    mid-sentence or mid-word.

    Args:
        text: Input text to chunk
        chunk_size: Maximum chunk size in characters (default from config)
        chunk_overlap: Overlap between chunks in characters (default from config)

    Returns:
        List of Chunk objects

    Raises:
        ChunkerError: If chunking fails
    """
    if chunk_size is None or chunk_overlap is None:
        config = get_config()
        chunk_size = chunk_size or config.chunk_size
        chunk_overlap = chunk_overlap or config.chunk_overlap

    if chunk_overlap >= chunk_size:
        raise ChunkerError(
            f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
        )

    if not text or not text.strip():
        return []

    # Clean text
    text = text.strip()

    # If text is small enough, return as single chunk
    if len(text) <= chunk_size:
        return [Chunk(content=text, index=0, start_char=0, end_char=len(text))]

    chunks = []
    paragraphs = split_into_paragraphs(text)

    current_chunk = ""
    current_start = 0
    char_position = 0

    for para in paragraphs:
        para_with_spacing = para + "\n\n"

        # If adding this paragraph exceeds chunk size
        if len(current_chunk) + len(para_with_spacing) > chunk_size:
            if current_chunk:
                # Save current chunk
                chunks.append(
                    Chunk(
                        content=current_chunk.strip(),
                        index=len(chunks),
                        start_char=current_start,
                        end_char=char_position,
                    )
                )

                # Start new chunk with overlap
                if chunk_overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-chunk_overlap:]
                    current_chunk = overlap_text + para_with_spacing
                    current_start = char_position - chunk_overlap
                else:
                    current_chunk = para_with_spacing
                    current_start = char_position
            else:
                # Paragraph itself is too long, need to split it
                para_chunks = _split_long_paragraph(
                    para, chunk_size, chunk_overlap, char_position, len(chunks)
                )
                chunks.extend(para_chunks)
                current_chunk = ""
                current_start = char_position + len(para_with_spacing)
        else:
            current_chunk += para_with_spacing

        char_position += len(para_with_spacing)

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(
            Chunk(
                content=current_chunk.strip(),
                index=len(chunks),
                start_char=current_start,
                end_char=char_position,
            )
        )

    # Re-index chunks
    for i, chunk in enumerate(chunks):
        chunk.index = i

    return chunks


def _split_long_paragraph(
    paragraph: str,
    chunk_size: int,
    chunk_overlap: int,
    start_position: int,
    start_index: int,
) -> list[Chunk]:
    """Split a long paragraph that exceeds chunk_size.

    Tries to split on sentence boundaries when possible.

    Args:
        paragraph: The paragraph text
        chunk_size: Maximum chunk size
        chunk_overlap: Overlap between chunks
        start_position: Character position in original text
        start_index: Starting chunk index

    Returns:
        List of Chunk objects
    """
    chunks = []
    current_pos = 0

    while current_pos < len(paragraph):
        end_pos = min(current_pos + chunk_size, len(paragraph))

        # Try to find a good break point (sentence end)
        if end_pos < len(paragraph):
            # Look for sentence end within last 20% of chunk
            search_start = current_pos + int(chunk_size * 0.8)
            search_region = paragraph[search_start:end_pos]

            # Look for sentence endings
            for pattern in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
                idx = search_region.rfind(pattern)
                if idx != -1:
                    end_pos = search_start + idx + len(pattern)
                    break

        chunk_text = paragraph[current_pos:end_pos].strip()

        if chunk_text:
            chunks.append(
                Chunk(
                    content=chunk_text,
                    index=start_index + len(chunks),
                    start_char=start_position + current_pos,
                    end_char=start_position + end_pos,
                )
            )

        # Move to next chunk with overlap
        current_pos = end_pos - chunk_overlap
        if current_pos <= chunks[-1].start_char - start_position if chunks else 0:
            current_pos = end_pos  # Prevent infinite loop

    return chunks


def chunk_document(
    content: str,
    source: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> Iterator[dict]:
    """Chunk a document and yield chunk dictionaries.

    Args:
        content: Document content
        source: Source filename/identifier
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks

    Yields:
        Dict with content, source, chunk_index, and metadata
    """
    chunks = chunk_text(content, chunk_size, chunk_overlap)

    for chunk in chunks:
        yield {
            "content": chunk.content,
            "source": source,
            "chunk_index": chunk.index,
            "metadata": {
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "length": chunk.length,
            },
        }
