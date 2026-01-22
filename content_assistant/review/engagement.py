"""Engagement analysis for content quality evaluation.

Analyzes content hooks, retention patterns, and engagement potential
to help optimize content before publishing.
"""

from dataclasses import dataclass, field

from content_assistant.generation.claude_client import generate_json, ClaudeError


class EngagementError(Exception):
    """Raised when engagement analysis fails."""

    pass


@dataclass
class EngagementAnalysis:
    """Analysis of content engagement potential.

    Attributes:
        overall_score: Overall engagement score (0-100)
        hook_strength: Hook effectiveness score (0-100)
        hook_analysis: Detailed hook analysis
        retention_score: Predicted content retention (0-100)
        clarity_score: Message clarity score (0-100)
        cta_effectiveness: Call-to-action effectiveness (0-100)
        strengths: List of content strengths
        improvements: List of suggested improvements
        platform_fit: How well content fits the target platform (0-100)
    """

    overall_score: int
    hook_strength: int
    hook_analysis: str
    retention_score: int
    clarity_score: int
    cta_effectiveness: int
    strengths: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    platform_fit: int = 80

    def to_dict(self) -> dict:
        """Convert analysis to dictionary."""
        return {
            "overall_score": self.overall_score,
            "hook_strength": self.hook_strength,
            "hook_analysis": self.hook_analysis,
            "retention_score": self.retention_score,
            "clarity_score": self.clarity_score,
            "cta_effectiveness": self.cta_effectiveness,
            "strengths": self.strengths,
            "improvements": self.improvements,
            "platform_fit": self.platform_fit,
        }


ENGAGEMENT_SYSTEM_PROMPT = """You are a content engagement analyst specializing in wellness and lifestyle content.

Your expertise includes:
- Social media algorithm optimization
- Hook psychology and attention capture
- Content retention patterns
- Call-to-action optimization
- Platform-specific best practices

When analyzing content, consider:
1. Hook - Does it stop the scroll? Create curiosity? Promise value?
2. Flow - Is the content easy to follow? Does it maintain interest?
3. Value - Does the reader get what was promised?
4. Action - Is the CTA clear and compelling?
5. Platform - Does it follow platform best practices?

Be specific and actionable in your feedback. Focus on what will actually improve engagement."""


def analyze_engagement(
    content: str,
    platform: str = "instagram",
    content_type: str = "post",
) -> EngagementAnalysis:
    """Analyze content for engagement potential.

    Args:
        content: Content text to analyze
        platform: Target platform (instagram, linkedin, etc.)
        content_type: Type of content (post, article, etc.)

    Returns:
        EngagementAnalysis with detailed metrics and suggestions

    Raises:
        EngagementError: If analysis fails
    """
    if not content or not content.strip():
        return EngagementAnalysis(
            overall_score=0,
            hook_strength=0,
            hook_analysis="No content provided",
            retention_score=0,
            clarity_score=0,
            cta_effectiveness=0,
        )

    prompt = f"""Analyze this content for engagement potential on {platform}.

Content Type: {content_type}
Platform: {platform}

Content:
{content}

Provide a comprehensive engagement analysis. Return a JSON object with:

- overall_score: number 0-100 (overall engagement potential)
- hook_strength: number 0-100 (how effective is the opening hook?)
- hook_analysis: string (detailed analysis of the hook - what works, what doesn't)
- retention_score: number 0-100 (will readers finish the content?)
- clarity_score: number 0-100 (how clear is the core message?)
- cta_effectiveness: number 0-100 (how compelling is the call to action?)
- platform_fit: number 0-100 (how well does it fit {platform} best practices?)
- strengths: array of strings (3-5 specific things done well)
- improvements: array of strings (3-5 specific, actionable improvements)

Be specific and constructive. Scores should reflect genuine quality, not just positivity."""

    try:
        result = generate_json(
            prompt=prompt,
            system_prompt=ENGAGEMENT_SYSTEM_PROMPT,
            temperature=0.4,
        )

        data = result["data"]

        return EngagementAnalysis(
            overall_score=data.get("overall_score", 50),
            hook_strength=data.get("hook_strength", 50),
            hook_analysis=data.get("hook_analysis", ""),
            retention_score=data.get("retention_score", 50),
            clarity_score=data.get("clarity_score", 50),
            cta_effectiveness=data.get("cta_effectiveness", 50),
            strengths=data.get("strengths", []),
            improvements=data.get("improvements", []),
            platform_fit=data.get("platform_fit", 50),
        )

    except ClaudeError as e:
        raise EngagementError(f"Failed to analyze engagement: {e}") from e
    except Exception as e:
        raise EngagementError(f"Unexpected error during analysis: {e}") from e


def analyze_hook(hook: str, platform: str = "instagram") -> dict:
    """Specifically analyze a content hook.

    Args:
        hook: The hook/opening text to analyze
        platform: Target platform

    Returns:
        Dict with hook analysis details

    Raises:
        EngagementError: If analysis fails
    """
    prompt = f"""Analyze this content hook for {platform}:

"{hook}"

Return a JSON object with:
- strength: number 0-100
- hook_type: string (question, bold_claim, story, statistic, etc.)
- scroll_stop_power: number 0-100 (would this stop someone scrolling?)
- curiosity_gap: number 0-100 (does it create curiosity to read more?)
- emotional_impact: string (what emotion does it evoke?)
- improvements: array of strings (specific ways to make it stronger)
- alternative_hooks: array of strings (2-3 alternative hook versions)"""

    try:
        result = generate_json(
            prompt=prompt,
            system_prompt=ENGAGEMENT_SYSTEM_PROMPT,
            temperature=0.6,
        )

        return result["data"]

    except ClaudeError as e:
        raise EngagementError(f"Failed to analyze hook: {e}") from e


def get_engagement_summary(analysis: EngagementAnalysis) -> str:
    """Generate a human-readable engagement summary.

    Args:
        analysis: Engagement analysis to summarize

    Returns:
        Formatted summary string
    """
    # Determine grade
    score = analysis.overall_score
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    lines = [
        f"## Engagement Analysis: {grade} ({score}/100)",
        "",
        "### Scores",
        f"- Hook Strength: {analysis.hook_strength}/100",
        f"- Retention: {analysis.retention_score}/100",
        f"- Clarity: {analysis.clarity_score}/100",
        f"- CTA Effectiveness: {analysis.cta_effectiveness}/100",
        f"- Platform Fit: {analysis.platform_fit}/100",
        "",
    ]

    if analysis.hook_analysis:
        lines.extend([
            "### Hook Analysis",
            analysis.hook_analysis,
            "",
        ])

    if analysis.strengths:
        lines.extend([
            "### Strengths",
            *[f"- {s}" for s in analysis.strengths],
            "",
        ])

    if analysis.improvements:
        lines.extend([
            "### Suggested Improvements",
            *[f"- {i}" for i in analysis.improvements],
            "",
        ])

    return "\n".join(lines)


def compare_content_versions(
    version_a: str,
    version_b: str,
    platform: str = "instagram",
) -> dict:
    """Compare two versions of content for engagement.

    Args:
        version_a: First content version
        version_b: Second content version
        platform: Target platform

    Returns:
        Dict with comparison results

    Raises:
        EngagementError: If comparison fails
    """
    prompt = f"""Compare these two content versions for {platform} engagement potential.

VERSION A:
{version_a}

VERSION B:
{version_b}

Return a JSON object with:
- winner: string ("A" or "B" or "tie")
- confidence: number 0-100 (how confident in the winner)
- version_a_score: number 0-100
- version_b_score: number 0-100
- key_differences: array of strings (main differences between versions)
- recommendation: string (which to use and why)"""

    try:
        result = generate_json(
            prompt=prompt,
            system_prompt=ENGAGEMENT_SYSTEM_PROMPT,
            temperature=0.4,
        )

        return result["data"]

    except ClaudeError as e:
        raise EngagementError(f"Failed to compare versions: {e}") from e
