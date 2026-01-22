"""Content preview generator.

Generates a preview of the content including:
- Hook (attention-grabbing opening)
- Hook type classification
- Open loops (curiosity gaps)
- Promise (what the reader will gain)
"""

from dataclasses import dataclass
from typing import Optional

from content_assistant.generation.brief import ContentBrief
from content_assistant.generation.claude_client import generate_json, ClaudeError


class PreviewError(Exception):
    """Raised when preview generation fails."""

    pass


@dataclass
class ContentPreview:
    """Preview of content before full generation.

    Attributes:
        hook: The attention-grabbing opening line/paragraph
        hook_type: Classification of hook style used
        open_loops: List of curiosity gaps created
        promise: What the reader will gain from the content
        brief_summary: One-line summary of the content direction
    """

    hook: str
    hook_type: str
    open_loops: list[str]
    promise: str
    brief_summary: str

    def to_dict(self) -> dict:
        """Convert preview to dictionary."""
        return {
            "hook": self.hook,
            "hook_type": self.hook_type,
            "open_loops": self.open_loops,
            "promise": self.promise,
            "brief_summary": self.brief_summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentPreview":
        """Create ContentPreview from dictionary."""
        return cls(
            hook=data.get("hook", ""),
            hook_type=data.get("hook_type", ""),
            open_loops=data.get("open_loops", []),
            promise=data.get("promise", ""),
            brief_summary=data.get("brief_summary", ""),
        )


HOOK_TYPES = [
    "question",  # Opens with a provocative question
    "bold_claim",  # Makes a surprising or contrarian statement
    "story",  # Starts with a personal or relatable story
    "statistic",  # Leads with a compelling data point
    "contrast",  # Shows before/after or problem/solution
    "curiosity",  # Creates intrigue without giving away the answer
    "pain_point",  # Directly addresses the reader's struggle
    "promise",  # Immediately states what they'll learn/gain
]


PREVIEW_SYSTEM_PROMPT = """You are a content strategist for TheLifeCo, a holistic wellness company.

Your task is to create a compelling content preview that will hook the reader and set up the full content.

TheLifeCo focuses on:
- Holistic detox and wellness retreats
- Mind-body connection
- Sustainable lifestyle transformation
- Evidence-based wellness practices

Guidelines for hooks:
1. The hook must stop the scroll - it should create immediate curiosity or emotional connection
2. Match the tone to the platform (professional for LinkedIn, conversational for Instagram)
3. Open loops create "information gaps" that make readers want to continue
4. The promise should be specific and valuable, not generic

Hook types and when to use them:
- question: When challenging assumptions or creating self-reflection
- bold_claim: When you have a contrarian or surprising insight
- story: When building emotional connection through narrative
- statistic: When you have compelling data that shifts perspective
- contrast: When showing transformation or before/after
- curiosity: When the reveal is powerful enough to justify the buildup
- pain_point: When directly acknowledging a known struggle
- promise: When the value proposition is clear and compelling"""


def _build_preview_prompt(brief: ContentBrief, knowledge_context: Optional[str] = None) -> str:
    """Build the prompt for preview generation.

    Args:
        brief: Content brief with strategic details
        knowledge_context: Optional relevant knowledge base context

    Returns:
        Formatted prompt string
    """
    prompt_parts = [
        brief.to_prompt_context(),
        "",
        "## Your Task",
        "",
        "Create a content preview with:",
        "1. A compelling hook that matches the brief's intent",
        "2. Classification of the hook type used",
        "3. 2-3 open loops (curiosity gaps) the content will address",
        "4. A clear promise of what the reader will gain",
        "5. A one-line summary of the content direction",
        "",
    ]

    if knowledge_context:
        prompt_parts.extend([
            "## Relevant Knowledge",
            "",
            knowledge_context,
            "",
        ])

    prompt_parts.extend([
        "## Response Format",
        "",
        "Respond with a JSON object containing:",
        "- hook: string (the opening hook, 1-3 sentences)",
        "- hook_type: string (one of: question, bold_claim, story, statistic, contrast, curiosity, pain_point, promise)",
        "- open_loops: array of strings (2-3 curiosity gaps)",
        "- promise: string (what the reader will gain)",
        "- brief_summary: string (one-line content direction)",
    ])

    return "\n".join(prompt_parts)


def generate_preview(
    brief: ContentBrief,
    knowledge_context: Optional[str] = None,
    temperature: float = 0.8,
) -> tuple[ContentPreview, dict]:
    """Generate a content preview from a brief.

    Args:
        brief: Content brief with strategic details
        knowledge_context: Optional relevant knowledge base context
        temperature: Sampling temperature (higher = more creative)

    Returns:
        Tuple of (ContentPreview, metadata dict with tokens and cost)

    Raises:
        PreviewError: If preview generation fails
    """
    prompt = _build_preview_prompt(brief, knowledge_context)

    try:
        result = generate_json(
            prompt=prompt,
            system_prompt=PREVIEW_SYSTEM_PROMPT,
            temperature=temperature,
        )

        data = result["data"]

        # Validate required fields
        required_fields = ["hook", "hook_type", "open_loops", "promise", "brief_summary"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise PreviewError(f"Missing required fields in response: {missing}")

        # Validate hook_type
        if data["hook_type"] not in HOOK_TYPES:
            # Try to normalize
            hook_type = data["hook_type"].lower().replace(" ", "_")
            if hook_type not in HOOK_TYPES:
                hook_type = "curiosity"  # Default fallback
            data["hook_type"] = hook_type

        # Ensure open_loops is a list
        if not isinstance(data["open_loops"], list):
            data["open_loops"] = [data["open_loops"]]

        preview = ContentPreview.from_dict(data)

        metadata = {
            "model": result["model"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "cost_usd": result["cost_usd"],
        }

        return preview, metadata

    except ClaudeError as e:
        raise PreviewError(f"Failed to generate preview: {e}") from e
    except Exception as e:
        raise PreviewError(f"Unexpected error generating preview: {e}") from e


def regenerate_hook(
    brief: ContentBrief,
    current_preview: ContentPreview,
    feedback: str,
    temperature: float = 0.9,
) -> tuple[ContentPreview, dict]:
    """Regenerate just the hook based on feedback.

    Args:
        brief: Original content brief
        current_preview: Current preview to improve
        feedback: User feedback on what to change
        temperature: Higher temperature for more variation

    Returns:
        Tuple of (new ContentPreview, metadata dict)

    Raises:
        PreviewError: If regeneration fails
    """
    prompt = f"""
{brief.to_prompt_context()}

## Current Hook
{current_preview.hook}

Hook Type: {current_preview.hook_type}

## Feedback
{feedback}

## Your Task
Generate a new hook that addresses the feedback while maintaining the strategic intent.
Keep the same open loops and promise unless they need adjustment.

Respond with a JSON object containing:
- hook: string (the new opening hook)
- hook_type: string (classification)
- open_loops: array of strings
- promise: string
- brief_summary: string
"""

    try:
        result = generate_json(
            prompt=prompt,
            system_prompt=PREVIEW_SYSTEM_PROMPT,
            temperature=temperature,
        )

        data = result["data"]
        preview = ContentPreview.from_dict(data)

        metadata = {
            "model": result["model"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "cost_usd": result["cost_usd"],
        }

        return preview, metadata

    except ClaudeError as e:
        raise PreviewError(f"Failed to regenerate hook: {e}") from e
