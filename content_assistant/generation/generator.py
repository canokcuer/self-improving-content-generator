"""Full content generator.

Takes an approved preview and generates complete content
following TheLifeCo's brand guidelines and platform requirements.
"""

from dataclasses import dataclass, field
from typing import Optional

from content_assistant.generation.brief import ContentBrief, get_platform_guidelines
from content_assistant.generation.preview import ContentPreview
from content_assistant.generation.claude_client import generate_text, ClaudeError


class GeneratorError(Exception):
    """Raised when content generation fails."""

    pass


@dataclass
class GeneratedContent:
    """Complete generated content.

    Attributes:
        content: The full generated content text
        brief: Original brief used for generation
        preview: Approved preview used as foundation
        word_count: Number of words in content
        character_count: Number of characters
        hashtags: Extracted hashtags (for social)
        metadata: Generation metadata (tokens, cost, etc.)
    """

    content: str
    brief: ContentBrief
    preview: ContentPreview
    word_count: int = 0
    character_count: int = 0
    hashtags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Calculate counts after initialization."""
        if self.content:
            self.word_count = len(self.content.split())
            self.character_count = len(self.content)
            # Extract hashtags
            self.hashtags = [
                word for word in self.content.split()
                if word.startswith("#")
            ]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "brief": self.brief.to_dict(),
            "preview": self.preview.to_dict(),
            "word_count": self.word_count,
            "character_count": self.character_count,
            "hashtags": self.hashtags,
            "metadata": self.metadata,
        }


GENERATOR_SYSTEM_PROMPT = """You are a master content creator for TheLifeCo, a holistic wellness company known for transformative detox retreats and mind-body wellness programs.

Your writing style:
- Warm yet authoritative
- Evidence-informed but accessible
- Emotionally resonant without being manipulative
- Action-oriented with clear value

TheLifeCo's core beliefs:
1. True wellness integrates body, mind, and spirit
2. Detox is not just physical - it's mental and emotional too
3. Small, sustainable changes create lasting transformation
4. Everyone deserves access to wellness knowledge
5. Nature and science work together for optimal health

Content structure guidelines:
1. Hook (provided in preview) - grab attention immediately
2. Build - develop the idea with evidence, story, or insight
3. Deliver - provide the promised value or transformation
4. Close - clear call to action that feels natural, not forced

Writing rules:
- Use "you" to speak directly to the reader
- Vary sentence length for rhythm
- Use line breaks for readability on digital platforms
- Avoid jargon unless explaining it
- Show, don't just tell - use examples and scenarios
- End with forward momentum, not finality"""


def _build_generation_prompt(
    brief: ContentBrief,
    preview: ContentPreview,
    knowledge_context: Optional[str] = None,
    few_shot_examples: Optional[list[dict]] = None,
) -> str:
    """Build the prompt for full content generation.

    Args:
        brief: Content brief with strategic details
        preview: Approved preview to expand
        knowledge_context: Optional relevant knowledge base content
        few_shot_examples: Optional list of high-performing examples

    Returns:
        Formatted prompt string
    """
    prompt_parts = [
        brief.to_prompt_context(),
        "",
        "## Approved Preview",
        "",
        f"**Hook:** {preview.hook}",
        f"**Hook Type:** {preview.hook_type}",
        f"**Open Loops:** {', '.join(preview.open_loops)}",
        f"**Promise:** {preview.promise}",
        f"**Direction:** {preview.brief_summary}",
        "",
        "## Platform Guidelines",
        "",
        get_platform_guidelines(brief.platform),
        "",
    ]

    if knowledge_context:
        prompt_parts.extend([
            "## Relevant Knowledge (use to ensure accuracy)",
            "",
            knowledge_context,
            "",
        ])

    if few_shot_examples:
        prompt_parts.extend([
            "## High-Performing Examples (for style reference)",
            "",
        ])
        for i, example in enumerate(few_shot_examples[:3], 1):
            prompt_parts.extend([
                f"### Example {i} (Rating: {example.get('rating', 'N/A')}/5)",
                "",
                example.get("content", ""),
                "",
            ])

    prompt_parts.extend([
        "## Your Task",
        "",
        "Write the complete content piece following these requirements:",
        "1. Start with the approved hook (you may refine slightly for flow)",
        "2. Deliver on ALL open loops - don't leave curiosity gaps unresolved",
        "3. Fulfill the promise made in the preview",
        "4. Match the tone specified in the brief",
        "5. Include the call to action naturally",
        "6. Follow platform-specific formatting guidelines",
        "",
    ])

    if brief.keywords:
        prompt_parts.append(f"Required keywords to include: {', '.join(brief.keywords)}")

    if brief.constraints:
        prompt_parts.append(f"Constraints to respect: {brief.constraints}")

    prompt_parts.extend([
        "",
        "Write the content now. Output ONLY the content itself, no explanations or meta-commentary.",
    ])

    return "\n".join(prompt_parts)


def generate_content(
    brief: ContentBrief,
    preview: ContentPreview,
    knowledge_context: Optional[str] = None,
    few_shot_examples: Optional[list[dict]] = None,
    temperature: float = 0.7,
) -> GeneratedContent:
    """Generate full content from an approved preview.

    Args:
        brief: Content brief with strategic details
        preview: Approved preview to expand
        knowledge_context: Optional relevant knowledge base content
        few_shot_examples: Optional high-performing examples for style
        temperature: Sampling temperature

    Returns:
        GeneratedContent with full content and metadata

    Raises:
        GeneratorError: If content generation fails
    """
    prompt = _build_generation_prompt(
        brief=brief,
        preview=preview,
        knowledge_context=knowledge_context,
        few_shot_examples=few_shot_examples,
    )

    try:
        result = generate_text(
            prompt=prompt,
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            temperature=temperature,
        )

        content = result["content"].strip()

        # Clean up any meta-commentary that slipped through
        lines = content.split("\n")
        clean_lines = []
        for line in lines:
            # Skip lines that look like meta-commentary
            if line.strip().startswith("Here") and "content" in line.lower():
                continue
            if line.strip().startswith("---") and len(clean_lines) == 0:
                continue
            clean_lines.append(line)

        content = "\n".join(clean_lines).strip()

        metadata = {
            "model": result["model"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "cost_usd": result["cost_usd"],
        }

        return GeneratedContent(
            content=content,
            brief=brief,
            preview=preview,
            metadata=metadata,
        )

    except ClaudeError as e:
        raise GeneratorError(f"Failed to generate content: {e}") from e
    except Exception as e:
        raise GeneratorError(f"Unexpected error generating content: {e}") from e


def regenerate_content(
    original: GeneratedContent,
    feedback: str,
    temperature: float = 0.8,
) -> GeneratedContent:
    """Regenerate content based on feedback.

    Args:
        original: Original generated content to improve
        feedback: User feedback on what to change
        temperature: Higher temperature for variation

    Returns:
        New GeneratedContent with improvements

    Raises:
        GeneratorError: If regeneration fails
    """
    prompt = f"""
{original.brief.to_prompt_context()}

## Original Content
{original.content}

## Feedback
{feedback}

## Your Task
Rewrite the content addressing the feedback while maintaining:
- The strategic intent from the brief
- The approved hook and open loops
- Platform-appropriate formatting

Write the improved content now. Output ONLY the content itself.
"""

    try:
        result = generate_text(
            prompt=prompt,
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            temperature=temperature,
        )

        content = result["content"].strip()

        metadata = {
            "model": result["model"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "cost_usd": result["cost_usd"],
            "regeneration_feedback": feedback,
        }

        return GeneratedContent(
            content=content,
            brief=original.brief,
            preview=original.preview,
            metadata=metadata,
        )

    except ClaudeError as e:
        raise GeneratorError(f"Failed to regenerate content: {e}") from e


def estimate_generation_cost(brief: ContentBrief) -> dict:
    """Estimate the cost of generating content for a brief.

    Args:
        brief: Content brief to estimate for

    Returns:
        Dict with estimated tokens and cost
    """
    # Rough estimates based on content type
    estimates = {
        "post": {"input": 1500, "output": 500},
        "story": {"input": 1200, "output": 300},
        "reel": {"input": 1200, "output": 200},
        "carousel": {"input": 1800, "output": 800},
        "article": {"input": 2000, "output": 2000},
        "newsletter": {"input": 2000, "output": 1500},
        "thread": {"input": 1500, "output": 1000},
    }

    content_type = brief.content_type.value
    est = estimates.get(content_type, {"input": 1500, "output": 500})

    # Claude Sonnet pricing
    input_cost = (est["input"] / 1_000_000) * 3.00
    output_cost = (est["output"] / 1_000_000) * 15.00
    total_cost = input_cost + output_cost

    return {
        "estimated_input_tokens": est["input"],
        "estimated_output_tokens": est["output"],
        "estimated_cost_usd": round(total_cost, 6),
        "note": "Preview + content generation combined",
    }
