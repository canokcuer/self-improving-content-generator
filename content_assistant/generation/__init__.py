"""Content generation module for TheLifeCo Content Assistant."""

from content_assistant.generation.brief import (
    ContentBrief,
    Platform,
    ContentType,
    validate_brief,
    BriefError,
)
from content_assistant.generation.claude_client import (
    generate_text,
    generate_json,
    ClaudeError,
)
from content_assistant.generation.preview import (
    ContentPreview,
    generate_preview,
    PreviewError,
)
from content_assistant.generation.generator import (
    GeneratedContent,
    generate_content,
    GeneratorError,
)

__all__ = [
    # Brief
    "ContentBrief",
    "Platform",
    "ContentType",
    "validate_brief",
    "BriefError",
    # Claude Client
    "generate_text",
    "generate_json",
    "ClaudeError",
    # Preview
    "ContentPreview",
    "generate_preview",
    "PreviewError",
    # Generator
    "GeneratedContent",
    "generate_content",
    "GeneratorError",
]
