"""Wellness Verification Agent for TheLifeCo Content Assistant.

The Wellness Agent is responsible for:
- Verifying content against TheLifeCo knowledge base
- Checking program details, center information, medical claims
- Providing verified facts to support content creation
- Flagging inaccuracies or unverified claims
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from content_assistant.agents.base_agent import BaseAgent, AgentTool, AgentResponse
from content_assistant.rag.knowledge_base import search_knowledge


@dataclass
class VerificationResult:
    """Result of wellness verification."""

    overall_score: float = 0.0  # 0-100
    verified_facts: list = field(default_factory=list)
    unverified_claims: list = field(default_factory=list)
    corrections: list = field(default_factory=list)
    supporting_knowledge: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "verified_facts": self.verified_facts,
            "unverified_claims": self.unverified_claims,
            "corrections": self.corrections,
            "supporting_knowledge": self.supporting_knowledge,
            "recommendations": self.recommendations,
        }


WELLNESS_SYSTEM_PROMPT = """You are the Wellness Verification Agent for TheLifeCo Content Assistant. Your role is to verify all facts and claims in content against TheLifeCo's knowledge base.

## Your Responsibilities
1. **Verify Facts**: Check all program names, durations, benefits against knowledge base
2. **Check Claims**: Ensure health/wellness claims are accurate and supported
3. **Validate Details**: Verify center information, services, amenities
4. **Flag Issues**: Identify unverified or potentially incorrect claims
5. **Provide Context**: Supply verified facts to support content creation

## Verification Process
For each piece of content or brief:
1. Extract all factual claims
2. Search knowledge base for supporting evidence
3. Classify each claim as: verified, partially_verified, unverified, incorrect
4. Provide corrections for incorrect claims
5. Suggest additional facts that could strengthen the content

## What to Verify
- Program names and details (Master Detox, Green Juice, etc.)
- Program durations and what's included
- Health benefits and outcomes
- Center-specific information (location, facilities, services)
- Pricing (if mentioned - note: pricing is typically provided by user)
- Medical/wellness claims

## Response Format
Always include a verification summary in JSON:

```json
{
  "verification_complete": true,
  "overall_score": 85,
  "verified_facts": ["list of verified facts"],
  "unverified_claims": ["claims that couldn't be verified"],
  "corrections": [{"original": "...", "corrected": "..."}],
  "supporting_knowledge": ["relevant facts from knowledge base"],
  "recommendations": ["suggestions to improve accuracy"]
}
```

## Important Guidelines
- Be thorough but not overly strict
- Distinguish between factual errors and creative language
- Don't block content for minor stylistic choices
- Focus on accuracy of TheLifeCo-specific claims
- Medical claims should be conservative and evidence-based
- When in doubt, flag for human review rather than rejecting"""


class WellnessAgent(BaseAgent):
    """Wellness Verification Agent.

    Verifies content against TheLifeCo knowledge base to ensure
    factual accuracy of programs, services, and wellness claims.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.3,  # Lower temperature for more precise verification
    ):
        """Initialize the Wellness Agent."""
        super().__init__(
            agent_name="wellness",
            system_prompt=WELLNESS_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            knowledge_sources=["wellness", "wellness/centers"],
        )

        self._last_verification: Optional[VerificationResult] = None

    def register_tools(self) -> None:
        """Register wellness-specific tools."""
        # Tool: Verify program information
        self.register_tool(AgentTool(
            name="verify_program",
            description="Verify information about a specific TheLifeCo program.",
            input_schema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "Name of the program to verify"
                    },
                    "claims": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of claims about the program to verify"
                    }
                },
                "required": ["program_name"]
            },
            handler=self._handle_verify_program
        ))

        # Tool: Verify center information
        self.register_tool(AgentTool(
            name="verify_center",
            description="Verify information about a specific TheLifeCo center.",
            input_schema={
                "type": "object",
                "properties": {
                    "center_name": {
                        "type": "string",
                        "description": "Name of the center (antalya, bodrum, phuket, sharm)"
                    },
                    "claims": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of claims about the center to verify"
                    }
                },
                "required": ["center_name"]
            },
            handler=self._handle_verify_center
        ))

        # Tool: Verify wellness claim
        self.register_tool(AgentTool(
            name="verify_wellness_claim",
            description="Verify a health or wellness claim against the knowledge base.",
            input_schema={
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "string",
                        "description": "The health/wellness claim to verify"
                    }
                },
                "required": ["claim"]
            },
            handler=self._handle_verify_wellness_claim
        ))

        # Tool: Get verified facts
        self.register_tool(AgentTool(
            name="get_verified_facts",
            description="Get verified facts about a topic from the knowledge base.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to get verified facts about"
                    },
                    "max_facts": {
                        "type": "integer",
                        "description": "Maximum number of facts to return",
                        "default": 5
                    }
                },
                "required": ["topic"]
            },
            handler=self._handle_get_verified_facts
        ))

    def _handle_verify_program(
        self,
        program_name: str,
        claims: Optional[list] = None
    ) -> str:
        """Verify program information."""
        results = search_knowledge(
            f"TheLifeCo {program_name} program",
            top_k=5,
            threshold=0.4
        )

        if not results:
            return f"WARNING: No knowledge found for program '{program_name}'. Cannot verify."

        knowledge = "\n".join([r.get("content", "") for r in results])

        verification = [f"Knowledge base information for {program_name}:"]
        verification.append(knowledge[:2000])

        if claims:
            verification.append("\n\nClaims to verify against this knowledge:")
            for claim in claims:
                # Simple keyword matching for now
                claim_lower = claim.lower()
                if any(word in knowledge.lower() for word in claim_lower.split()):
                    verification.append(f"- LIKELY SUPPORTED: {claim}")
                else:
                    verification.append(f"- NEEDS VERIFICATION: {claim}")

        return "\n".join(verification)

    def _handle_verify_center(
        self,
        center_name: str,
        claims: Optional[list] = None
    ) -> str:
        """Verify center information."""
        results = search_knowledge(
            f"TheLifeCo {center_name} center",
            top_k=5,
            threshold=0.4
        )

        if not results:
            return f"WARNING: No knowledge found for center '{center_name}'. Cannot verify."

        knowledge = "\n".join([r.get("content", "") for r in results])

        verification = [f"Knowledge base information for TheLifeCo {center_name.title()}:"]
        verification.append(knowledge[:2000])

        if claims:
            verification.append("\n\nClaims to verify:")
            for claim in claims:
                claim_lower = claim.lower()
                if any(word in knowledge.lower() for word in claim_lower.split()):
                    verification.append(f"- LIKELY SUPPORTED: {claim}")
                else:
                    verification.append(f"- NEEDS VERIFICATION: {claim}")

        return "\n".join(verification)

    def _handle_verify_wellness_claim(self, claim: str) -> str:
        """Verify a wellness/health claim."""
        results = search_knowledge(
            claim,
            top_k=5,
            threshold=0.5
        )

        if not results:
            return f"UNVERIFIED: No supporting evidence found for claim: '{claim}'. Consider rephrasing or removing."

        # Check relevance
        best_match = results[0]
        similarity = best_match.get("similarity", 0)

        if similarity > 0.7:
            return f"VERIFIED (confidence: {similarity:.0%}): Found supporting evidence:\n{best_match.get('content', '')[:500]}"
        elif similarity > 0.5:
            return f"PARTIALLY VERIFIED (confidence: {similarity:.0%}): Some supporting evidence found:\n{best_match.get('content', '')[:500]}"
        else:
            return f"WEAK SUPPORT (confidence: {similarity:.0%}): Limited evidence. Consider verification:\n{best_match.get('content', '')[:300]}"

    def _handle_get_verified_facts(self, topic: str, max_facts: int = 5) -> str:
        """Get verified facts about a topic."""
        results = search_knowledge(
            topic,
            top_k=max_facts,
            threshold=0.5
        )

        if not results:
            return f"No verified facts found for topic: '{topic}'"

        facts = [f"Verified facts about {topic}:"]
        for i, r in enumerate(results, 1):
            content = r.get("content", "")
            source = r.get("source", "unknown")
            facts.append(f"\n{i}. [Source: {source}]\n{content[:400]}...")

        return "\n".join(facts)

    def _extract_response_data(self, response: str) -> tuple[dict, bool, Optional[str]]:
        """Extract verification data from response."""
        # Look for JSON block
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)

        if json_match:
            try:
                data = json.loads(json_match.group(1))

                if data.get("verification_complete"):
                    self._last_verification = VerificationResult(
                        overall_score=data.get("overall_score", 0),
                        verified_facts=data.get("verified_facts", []),
                        unverified_claims=data.get("unverified_claims", []),
                        corrections=data.get("corrections", []),
                        supporting_knowledge=data.get("supporting_knowledge", []),
                        recommendations=data.get("recommendations", [])
                    )
                    return data, True, "storytelling"

            except json.JSONDecodeError:
                pass

        return {}, False, None

    def verify_brief(self, brief: dict) -> AgentResponse:
        """Verify a content brief before content generation.

        Args:
            brief: Content brief dictionary from Orchestrator

        Returns:
            AgentResponse with verification results
        """
        # Construct verification request
        verification_request = f"""Please verify the following content brief:

**Core Message:** {brief.get('core_message', 'Not specified')}
**Target Audience:** {brief.get('target_audience', 'Not specified')}
**Platform:** {brief.get('platform', 'Not specified')}
**Funnel Stage:** {brief.get('funnel_stage', 'Not specified')}
**Specific Program:** {brief.get('specific_program', 'Not specified')}
**Pain Point:** {brief.get('pain_point', 'Not specified')}
**Transformation:** {brief.get('transformation', 'Not specified')}

Please:
1. Verify any program/service names mentioned
2. Check if the claimed benefits are accurate
3. Provide relevant verified facts to support the content
4. Flag any potential issues

Return your verification results in JSON format."""

        return self.process_message_sync(verification_request)

    def verify_content(self, content: str) -> AgentResponse:
        """Verify generated content for accuracy.

        Args:
            content: Generated content text

        Returns:
            AgentResponse with verification results
        """
        verification_request = f"""Please verify the following content for accuracy:

---
{content}
---

Please:
1. Extract all factual claims from the content
2. Verify each claim against the knowledge base
3. Check program names, benefits, and center details
4. Flag any inaccurate or unverified claims
5. Suggest corrections if needed

Return your verification results in JSON format."""

        return self.process_message_sync(verification_request)

    def get_last_verification(self) -> Optional[VerificationResult]:
        """Get the last verification result."""
        return self._last_verification

    def get_supporting_facts(self, topic: str, count: int = 5) -> list[str]:
        """Get supporting facts for a topic.

        Args:
            topic: Topic to find facts for
            count: Number of facts to return

        Returns:
            List of verified facts
        """
        results = search_knowledge(topic, top_k=count, threshold=0.5)
        return [r.get("content", "") for r in results]
