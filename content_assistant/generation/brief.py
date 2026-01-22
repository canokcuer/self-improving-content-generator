"""Socratic Brief: 13-question content questionnaire.

The brief captures the strategic intent behind content through
guided questions that help define the message, audience, and goals.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class BriefError(Exception):
    """Raised when brief validation fails."""

    pass


class Platform(Enum):
    """Supported content platforms."""

    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    BLOG = "blog"
    EMAIL = "email"
    FACEBOOK = "facebook"


class ContentType(Enum):
    """Supported content types."""

    POST = "post"
    STORY = "story"
    REEL = "reel"
    CAROUSEL = "carousel"
    ARTICLE = "article"
    NEWSLETTER = "newsletter"
    THREAD = "thread"


# The 13 Socratic Questions for content briefing
SOCRATIC_QUESTIONS = [
    {
        "id": "transformation",
        "question": "What transformation do you want to create in your audience?",
        "hint": "Think about the before/after state. What shift in thinking, feeling, or behavior?",
        "required": True,
    },
    {
        "id": "audience",
        "question": "Who specifically is this content for?",
        "hint": "Be specific: job title, life stage, current struggle, aspiration",
        "required": True,
    },
    {
        "id": "pain_point",
        "question": "What pain point or desire does this address?",
        "hint": "What keeps them up at night? What do they secretly wish for?",
        "required": True,
    },
    {
        "id": "unique_angle",
        "question": "What makes TheLifeCo's perspective unique here?",
        "hint": "What do we know or believe that others don't? What's our edge?",
        "required": True,
    },
    {
        "id": "core_message",
        "question": "What's the ONE thing they should remember?",
        "hint": "If they forget everything else, what's the single takeaway?",
        "required": True,
    },
    {
        "id": "evidence",
        "question": "What evidence or story supports this message?",
        "hint": "Research, case study, personal story, analogy, or metaphor",
        "required": False,
    },
    {
        "id": "emotional_journey",
        "question": "What emotional journey should the reader experience?",
        "hint": "Curious → excited? Frustrated → hopeful? Skeptical → convinced?",
        "required": False,
    },
    {
        "id": "objections",
        "question": "What objections or doubts might they have?",
        "hint": "Why might they resist this message? What could hold them back?",
        "required": False,
    },
    {
        "id": "call_to_action",
        "question": "What action should they take next?",
        "hint": "Comment, share, visit website, book a call, reflect on X?",
        "required": True,
    },
    {
        "id": "tone",
        "question": "What tone best fits this content?",
        "hint": "Warm, authoritative, playful, urgent, inspiring, conversational?",
        "required": False,
    },
    {
        "id": "hook_style",
        "question": "What hook style would grab attention?",
        "hint": "Question, bold claim, story opening, statistic, controversy?",
        "required": False,
    },
    {
        "id": "keywords",
        "question": "What keywords or phrases must be included?",
        "hint": "SEO terms, brand language, specific offers or programs",
        "required": False,
    },
    {
        "id": "constraints",
        "question": "Any constraints or things to avoid?",
        "hint": "Competitor mentions, sensitive topics, specific claims to avoid",
        "required": False,
    },
]


@dataclass
class ContentBrief:
    """A complete content brief from the 13 Socratic questions.

    Attributes:
        platform: Target platform (instagram, linkedin, etc.)
        content_type: Type of content (post, story, reel, etc.)
        transformation: Q1 - Desired audience transformation
        audience: Q2 - Target audience description
        pain_point: Q3 - Pain point or desire being addressed
        unique_angle: Q4 - TheLifeCo's unique perspective
        core_message: Q5 - Single most important takeaway
        evidence: Q6 - Supporting evidence or story (optional)
        emotional_journey: Q7 - Intended emotional arc (optional)
        objections: Q8 - Anticipated objections (optional)
        call_to_action: Q9 - Desired next action
        tone: Q10 - Desired tone (optional)
        hook_style: Q11 - Preferred hook style (optional)
        keywords: Q12 - Required keywords (optional)
        constraints: Q13 - Things to avoid (optional)
    """

    # Platform and type
    platform: Platform
    content_type: ContentType

    # Required questions
    transformation: str
    audience: str
    pain_point: str
    unique_angle: str
    core_message: str
    call_to_action: str

    # Optional questions
    evidence: Optional[str] = None
    emotional_journey: Optional[str] = None
    objections: Optional[str] = None
    tone: Optional[str] = None
    hook_style: Optional[str] = None
    keywords: Optional[list[str]] = field(default_factory=list)
    constraints: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert brief to dictionary format.

        Returns:
            Dictionary representation of the brief
        """
        return {
            "platform": self.platform.value,
            "content_type": self.content_type.value,
            "transformation": self.transformation,
            "audience": self.audience,
            "pain_point": self.pain_point,
            "unique_angle": self.unique_angle,
            "core_message": self.core_message,
            "call_to_action": self.call_to_action,
            "evidence": self.evidence,
            "emotional_journey": self.emotional_journey,
            "objections": self.objections,
            "tone": self.tone,
            "hook_style": self.hook_style,
            "keywords": self.keywords or [],
            "constraints": self.constraints,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentBrief":
        """Create a ContentBrief from a dictionary.

        Args:
            data: Dictionary with brief fields

        Returns:
            ContentBrief instance

        Raises:
            BriefError: If required fields are missing or invalid
        """
        try:
            # Parse enums
            platform = Platform(data.get("platform", "").lower())
            content_type = ContentType(data.get("content_type", "").lower())

            return cls(
                platform=platform,
                content_type=content_type,
                transformation=data.get("transformation", ""),
                audience=data.get("audience", ""),
                pain_point=data.get("pain_point", ""),
                unique_angle=data.get("unique_angle", ""),
                core_message=data.get("core_message", ""),
                call_to_action=data.get("call_to_action", ""),
                evidence=data.get("evidence"),
                emotional_journey=data.get("emotional_journey"),
                objections=data.get("objections"),
                tone=data.get("tone"),
                hook_style=data.get("hook_style"),
                keywords=data.get("keywords", []),
                constraints=data.get("constraints"),
            )
        except ValueError as e:
            raise BriefError(f"Invalid brief data: {e}") from e

    def to_prompt_context(self) -> str:
        """Format brief for use in LLM prompts.

        Returns:
            Formatted string for prompt injection
        """
        lines = [
            "## Content Brief",
            "",
            f"**Platform:** {self.platform.value.title()}",
            f"**Content Type:** {self.content_type.value.title()}",
            "",
            "### Strategic Intent",
            "",
            f"**Transformation Goal:** {self.transformation}",
            f"**Target Audience:** {self.audience}",
            f"**Pain Point/Desire:** {self.pain_point}",
            f"**Unique Angle:** {self.unique_angle}",
            f"**Core Message:** {self.core_message}",
            f"**Call to Action:** {self.call_to_action}",
        ]

        if self.evidence:
            lines.append(f"**Supporting Evidence:** {self.evidence}")

        if self.emotional_journey:
            lines.append(f"**Emotional Journey:** {self.emotional_journey}")

        if self.objections:
            lines.append(f"**Anticipated Objections:** {self.objections}")

        if self.tone:
            lines.append(f"**Tone:** {self.tone}")

        if self.hook_style:
            lines.append(f"**Hook Style:** {self.hook_style}")

        if self.keywords:
            lines.append(f"**Required Keywords:** {', '.join(self.keywords)}")

        if self.constraints:
            lines.append(f"**Constraints:** {self.constraints}")

        return "\n".join(lines)


def validate_brief(brief: ContentBrief) -> list[str]:
    """Validate a content brief.

    Args:
        brief: ContentBrief to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required text fields are non-empty
    required_fields = [
        ("transformation", brief.transformation),
        ("audience", brief.audience),
        ("pain_point", brief.pain_point),
        ("unique_angle", brief.unique_angle),
        ("core_message", brief.core_message),
        ("call_to_action", brief.call_to_action),
    ]

    for field_name, value in required_fields:
        if not value or not value.strip():
            errors.append(f"Required field '{field_name}' is empty")

    # Check minimum length for required fields
    min_length = 10
    for field_name, value in required_fields:
        if value and len(value.strip()) < min_length:
            errors.append(
                f"Field '{field_name}' should be at least {min_length} characters"
            )

    return errors


def get_questions() -> list[dict]:
    """Get the 13 Socratic questions.

    Returns:
        List of question definitions with id, question, hint, and required flag
    """
    return SOCRATIC_QUESTIONS.copy()


def get_platform_guidelines(platform: Platform) -> str:
    """Get platform-specific content guidelines.

    Args:
        platform: Target platform

    Returns:
        Platform-specific guidelines string
    """
    guidelines = {
        Platform.INSTAGRAM: """
- Hook in first line (appears above "more")
- Use line breaks for readability
- 2-5 relevant hashtags at the end
- Emojis can increase engagement
- Character limit: 2,200 (but first 125 visible)
""",
        Platform.LINKEDIN: """
- Professional but conversational tone
- Hook in first 2 lines (shows before "see more")
- Use formatting: bullet points, line breaks
- End with a question or CTA
- Character limit: 3,000
""",
        Platform.TWITTER: """
- Punchy, concise messaging
- Thread format for longer content
- First tweet must hook and stand alone
- Character limit: 280 per tweet
""",
        Platform.BLOG: """
- SEO-optimized headline and subheadings
- Meta description 150-160 characters
- Include internal and external links
- Use headers (H2, H3) for structure
- Aim for 1,500-2,500 words for authority
""",
        Platform.EMAIL: """
- Subject line is critical (40-60 chars)
- Preview text (90-100 chars)
- Personal, direct tone
- Clear single CTA
- Mobile-friendly formatting
""",
        Platform.FACEBOOK: """
- First 1-2 sentences visible without clicking "See more"
- Questions and polls increase engagement
- Native video performs best
- Character limit: 63,206 (but shorter is better)
""",
    }

    return guidelines.get(platform, "No specific guidelines available.")
