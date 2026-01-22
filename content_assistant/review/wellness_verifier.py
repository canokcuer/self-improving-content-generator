"""Wellness content verifier.

Checks generated content against TheLifeCo's knowledge base
to ensure claims are accurate and aligned with brand guidelines.
"""

from dataclasses import dataclass, field

from content_assistant.rag.knowledge_base import search_knowledge, KnowledgeBaseError
from content_assistant.generation.claude_client import generate_json, ClaudeError


class VerifierError(Exception):
    """Raised when wellness verification fails."""

    pass


@dataclass
class WellnessVerificationResult:
    """Result of wellness content verification.

    Attributes:
        is_verified: Whether all claims passed verification
        score: Overall verification score (0-100)
        claims_found: List of claims extracted from content
        verified_claims: Claims that match knowledge base
        unverified_claims: Claims without knowledge base support
        concerns: List of potential issues found
        suggestions: List of improvement suggestions
        supporting_knowledge: Relevant knowledge chunks used
    """

    is_verified: bool
    score: int
    claims_found: list[str] = field(default_factory=list)
    verified_claims: list[str] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    supporting_knowledge: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "is_verified": self.is_verified,
            "score": self.score,
            "claims_found": self.claims_found,
            "verified_claims": self.verified_claims,
            "unverified_claims": self.unverified_claims,
            "concerns": self.concerns,
            "suggestions": self.suggestions,
            "supporting_knowledge": [
                {"content": k.get("content", ""), "source": k.get("source", "")}
                for k in self.supporting_knowledge
            ],
        }


VERIFIER_SYSTEM_PROMPT = """You are a wellness content verifier for TheLifeCo, a holistic wellness company.

Your task is to verify that content claims are:
1. Factually accurate based on the provided knowledge base
2. Aligned with TheLifeCo's brand values and approach
3. Not making unsubstantiated health claims
4. Responsible and ethical in wellness messaging

TheLifeCo's approach:
- Evidence-informed, not pseudoscience
- Holistic but grounded
- Empowering, not fear-based
- Honest about what can and cannot be claimed

When evaluating claims:
- Medical claims require strong evidence
- "May help" or "can support" is different from "will cure"
- Personal experiences and testimonials should be framed appropriately
- Avoid absolute statements without evidence"""


def _extract_claims(content: str) -> list[str]:
    """Extract verifiable claims from content.

    Args:
        content: Content text to analyze

    Returns:
        List of claims found in the content
    """
    prompt = f"""Extract all factual claims and health-related statements from this content that could be verified.

Content:
{content}

Return a JSON object with:
- claims: array of strings (each claim as a separate item)

Only include statements that make factual or health-related claims, not opinions or subjective statements."""

    try:
        result = generate_json(
            prompt=prompt,
            system_prompt="Extract factual claims from wellness content. Be thorough but only include verifiable statements.",
            temperature=0.3,
        )

        return result["data"].get("claims", [])

    except ClaudeError:
        # If extraction fails, return empty list
        return []


def verify_wellness_claims(
    content: str,
    strict_mode: bool = False,
) -> WellnessVerificationResult:
    """Verify wellness claims in content against knowledge base.

    Args:
        content: Content text to verify
        strict_mode: If True, require explicit knowledge base support

    Returns:
        WellnessVerificationResult with verification details

    Raises:
        VerifierError: If verification fails
    """
    if not content or not content.strip():
        return WellnessVerificationResult(
            is_verified=True,
            score=100,
            claims_found=[],
        )

    try:
        # Extract claims from content
        claims = _extract_claims(content)

        if not claims:
            return WellnessVerificationResult(
                is_verified=True,
                score=100,
                claims_found=[],
            )

        # Search knowledge base for relevant content
        knowledge_results = []
        try:
            # Search using the full content for broad context
            knowledge_results = search_knowledge(
                query=content[:1000],  # Limit query length
                match_threshold=0.6,
                match_count=10,
            )
        except KnowledgeBaseError:
            # Knowledge base might not be set up yet
            pass

        # Build context from knowledge base
        knowledge_context = "\n\n".join([
            f"Source: {k.get('source', 'unknown')}\n{k.get('content', '')}"
            for k in knowledge_results
        ])

        # Verify claims against knowledge
        verification_prompt = f"""Verify each claim against the knowledge base.

Claims to verify:
{chr(10).join(f"- {claim}" for claim in claims)}

Knowledge Base Content:
{knowledge_context if knowledge_context else "No knowledge base content available."}

For each claim, determine if it is:
1. VERIFIED - Supported by knowledge base
2. UNVERIFIED - Not found in knowledge base (may still be true)
3. CONCERNING - Potentially problematic claim

Return a JSON object with:
- verified_claims: array of verified claim strings
- unverified_claims: array of unverified claim strings
- concerns: array of objects with "claim" and "reason" fields
- suggestions: array of improvement suggestions
- overall_score: number 0-100 representing verification confidence
"""

        result = generate_json(
            prompt=verification_prompt,
            system_prompt=VERIFIER_SYSTEM_PROMPT,
            temperature=0.3,
        )

        data = result["data"]

        verified = data.get("verified_claims", [])
        unverified = data.get("unverified_claims", [])
        concerns = data.get("concerns", [])
        suggestions = data.get("suggestions", [])
        score = data.get("overall_score", 50)

        # Extract concern descriptions
        concern_descriptions = []
        for c in concerns:
            if isinstance(c, dict):
                concern_descriptions.append(f"{c.get('claim', 'Unknown')}: {c.get('reason', '')}")
            else:
                concern_descriptions.append(str(c))

        # Determine if verified based on mode and results
        if strict_mode:
            is_verified = len(unverified) == 0 and len(concerns) == 0
        else:
            is_verified = len(concerns) == 0 and score >= 60

        return WellnessVerificationResult(
            is_verified=is_verified,
            score=score,
            claims_found=claims,
            verified_claims=verified,
            unverified_claims=unverified,
            concerns=concern_descriptions,
            suggestions=suggestions,
            supporting_knowledge=knowledge_results,
        )

    except ClaudeError as e:
        raise VerifierError(f"Failed to verify claims: {e}") from e
    except Exception as e:
        raise VerifierError(f"Unexpected error during verification: {e}") from e


def get_verification_summary(result: WellnessVerificationResult) -> str:
    """Generate a human-readable verification summary.

    Args:
        result: Verification result to summarize

    Returns:
        Formatted summary string
    """
    lines = [
        f"## Wellness Verification {'PASSED' if result.is_verified else 'NEEDS REVIEW'}",
        f"Score: {result.score}/100",
        "",
    ]

    if result.verified_claims:
        lines.extend([
            "### Verified Claims",
            *[f"- {c}" for c in result.verified_claims],
            "",
        ])

    if result.unverified_claims:
        lines.extend([
            "### Unverified Claims (may need review)",
            *[f"- {c}" for c in result.unverified_claims],
            "",
        ])

    if result.concerns:
        lines.extend([
            "### Concerns",
            *[f"- {c}" for c in result.concerns],
            "",
        ])

    if result.suggestions:
        lines.extend([
            "### Suggestions",
            *[f"- {s}" for s in result.suggestions],
            "",
        ])

    return "\n".join(lines)
