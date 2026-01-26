"""Review Sub-Agent - Feedback Analyzer for TheLifeCo Content Assistant.

Review sub-agent analyzes user feedback on generated content to:
1. Determine if issues are wellness-related (route to GONCA)
2. Determine if issues are storytelling-related (route to CAN)
3. Extract specific change requests
4. Provide structured feedback analysis for EPA

This is invoked by EPA when users provide feedback on generated content.
"""

from dataclasses import dataclass
from typing import Optional, Any

from content_assistant.agents.base_agent import BaseAgent, AgentTool, AgentResponse
from content_assistant.agents.types import (
    FeedbackRequest,
    FeedbackAnalysis,
    ContentBrief,
    StorytellingResponse,
    WellnessResponse,
)


# =============================================================================
# SYSTEM PROMPT FOR REVIEW SUB-AGENT
# =============================================================================

REVIEW_SYSTEM_PROMPT = """You are the Review sub-agent for TheLifeCo Content Assistant.
You analyze user feedback on generated content to help EPA decide next steps.

## Your Role
When users provide feedback on generated content, you:
1. Categorize the feedback (wellness-related, storytelling-related, or both)
2. Identify specific issues and requests
3. Recommend which sub-agent should handle revisions
4. Provide structured analysis for EPA

## Feedback Categories

**Wellness Issues** (route to GONCA):
- Factual inaccuracies about programs/centers
- Missing important information
- Compliance concerns
- Health claim issues
- Wanting more specific program details

**Storytelling Issues** (route to CAN):
- Tone doesn't match requested style
- Hook isn't engaging enough
- Content too long/short
- Structure issues
- CTA not compelling
- Doesn't resonate emotionally
- Platform format issues

**Both** (route to both GONCA then CAN):
- Need different facts AND different presentation
- Major rewrite needed

**Approved** (no changes needed):
- User is satisfied with the content
- Minor tweaks EPA can handle directly

## Response Format
Analyze the feedback and provide:

FEEDBACK_TYPE: [wellness/storytelling/both/approved]
SENTIMENT: [positive/negative/mixed]
WELLNESS_ISSUES: [bullet list or "None"]
STORYTELLING_ISSUES: [bullet list or "None"]
SPECIFIC_REQUESTS: [bullet list of specific changes requested]
SUGGESTED_ACTION: [revise_wellness/revise_storytelling/revise_both/finalize]
SUMMARY: [Brief summary of the feedback for EPA]

## Important
- Be thorough in identifying all issues
- Look for implicit feedback (not just explicit requests)
- Consider the original brief when evaluating feedback
- Help EPA make the right decision about next steps"""


# =============================================================================
# REVIEW SUB-AGENT IMPLEMENTATION
# =============================================================================

class ReviewSubAgent(BaseAgent):
    """Review Sub-Agent - Feedback Analyzer.

    Analyzes user feedback to determine routing and extract
    actionable insights for content revision.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.3,  # Lower temperature for analytical work
    ):
        """Initialize Review sub-agent.

        Args:
            model: Claude model to use (defaults to config)
            temperature: Lower temperature for accurate analysis
        """
        super().__init__(
            agent_name="review",
            system_prompt=REVIEW_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            knowledge_sources=[],
        )

    def register_tools(self) -> None:
        """Register Review-specific tools.

        Review sub-agent doesn't need special tools - it analyzes
        feedback using its understanding of content and context.
        """
        pass  # No additional tools needed

    # =========================================================================
    # MAIN PROCESSING METHOD
    # =========================================================================

    def process_request(self, request: FeedbackRequest) -> FeedbackAnalysis:
        """Process feedback analysis request from EPA.

        Args:
            request: FeedbackRequest with user feedback and context

        Returns:
            FeedbackAnalysis with categorized feedback and recommendations
        """
        # Build the analysis prompt
        prompt = self._build_prompt(request)

        # Add as user message and get response
        response = self.process_message_sync(prompt)

        # Parse the response into FeedbackAnalysis
        return self._parse_response(response.content)

    def _build_prompt(self, request: FeedbackRequest) -> str:
        """Build prompt for feedback analysis."""
        brief = request.brief
        content = request.generated_content
        wellness = request.wellness_facts

        prompt_parts = [
            "# Feedback Analysis Request",
            "",
            "## User's Feedback",
            f'"{request.user_feedback}"',
            "",
            "## Original Content Brief",
            f"- Target Audience: {brief.target_audience}",
            f"- Pain Area: {brief.pain_area}",
            f"- Tone: {brief.tone}",
            f"- Platform: {brief.platform.value if brief.platform else 'Not specified'}",
            f"- Funnel Stage: {brief.funnel_stage.value if brief.funnel_stage else 'Not specified'}",
            "",
            "## Generated Content",
            f"**Hook ({content.hook_type}):** {content.hook}",
            "",
            f"**Content:** {content.content[:500]}..." if len(content.content) > 500 else f"**Content:** {content.content}",
            "",
            f"**CTA:** {content.call_to_action}",
            f"**Framework:** {content.storytelling_framework}",
            "",
            "## Wellness Facts Used",
        ]

        for fact in wellness.verified_facts[:5]:
            prompt_parts.append(f"- {fact}")

        prompt_parts.extend([
            "",
            "## Your Task",
            "Analyze the user's feedback and provide:",
            "1. FEEDBACK_TYPE: wellness/storytelling/both/approved",
            "2. SENTIMENT: positive/negative/mixed",
            "3. WELLNESS_ISSUES: List of wellness-related issues (or 'None')",
            "4. STORYTELLING_ISSUES: List of storytelling-related issues (or 'None')",
            "5. SPECIFIC_REQUESTS: List of specific changes the user wants",
            "6. SUGGESTED_ACTION: revise_wellness/revise_storytelling/revise_both/finalize",
            "7. SUMMARY: Brief summary for EPA",
        ])

        return "\n".join(prompt_parts)

    def _parse_response(self, response_text: str) -> FeedbackAnalysis:
        """Parse Review agent's response into FeedbackAnalysis."""
        # Initialize defaults
        feedback_type = "storytelling"
        sentiment = "mixed"
        wellness_issues = []
        storytelling_issues = []
        specific_requests = []
        suggested_action = "revise_storytelling"
        summary = ""

        # Parse sections
        lines = response_text.split("\n")
        current_section = None
        current_items = []

        for line in lines:
            line_stripped = line.strip()
            line_upper = line_stripped.upper()

            if line_upper.startswith("FEEDBACK_TYPE:"):
                feedback_type = line_stripped.split(":", 1)[1].strip().lower()
            elif line_upper.startswith("SENTIMENT:"):
                sentiment = line_stripped.split(":", 1)[1].strip().lower()
            elif line_upper.startswith("WELLNESS_ISSUES:"):
                if current_section and current_items:
                    self._assign_items(current_section, current_items, locals())
                rest = line_stripped.split(":", 1)[1].strip()
                if rest.lower() != "none" and rest:
                    wellness_issues = [rest]
                current_section = "wellness"
                current_items = []
            elif line_upper.startswith("STORYTELLING_ISSUES:"):
                if current_section == "wellness" and current_items:
                    wellness_issues.extend(current_items)
                rest = line_stripped.split(":", 1)[1].strip()
                if rest.lower() != "none" and rest:
                    storytelling_issues = [rest]
                current_section = "storytelling"
                current_items = []
            elif line_upper.startswith("SPECIFIC_REQUESTS:"):
                if current_section == "storytelling" and current_items:
                    storytelling_issues.extend(current_items)
                rest = line_stripped.split(":", 1)[1].strip()
                if rest and rest.lower() != "none":
                    specific_requests = [rest]
                current_section = "requests"
                current_items = []
            elif line_upper.startswith("SUGGESTED_ACTION:"):
                if current_section == "requests" and current_items:
                    specific_requests.extend(current_items)
                suggested_action = line_stripped.split(":", 1)[1].strip().lower()
                current_section = None
                current_items = []
            elif line_upper.startswith("SUMMARY:"):
                summary = line_stripped.split(":", 1)[1].strip()
                current_section = "summary"
                current_items = []
            elif current_section:
                # Collect bullet points
                if line_stripped.startswith(("-", "*", "•")):
                    current_items.append(line_stripped[1:].strip())
                elif line_stripped and current_section == "summary":
                    summary += " " + line_stripped

        # Assign remaining items
        if current_section == "wellness" and current_items:
            wellness_issues.extend(current_items)
        elif current_section == "storytelling" and current_items:
            storytelling_issues.extend(current_items)
        elif current_section == "requests" and current_items:
            specific_requests.extend(current_items)

        # Clean up lists - remove "None" entries
        wellness_issues = [i for i in wellness_issues if i.lower() != "none"]
        storytelling_issues = [i for i in storytelling_issues if i.lower() != "none"]
        specific_requests = [i for i in specific_requests if i.lower() != "none"]

        # Map suggested action to valid values
        action_map = {
            "revise_wellness": "revise_wellness",
            "revise_storytelling": "revise_storytelling",
            "revise_both": "revise_both",
            "finalize": "finalize",
            "approved": "finalize",
            "wellness": "revise_wellness",
            "storytelling": "revise_storytelling",
            "both": "revise_both",
        }
        suggested_action = action_map.get(suggested_action, "revise_storytelling")

        return FeedbackAnalysis(
            feedback_type=feedback_type,
            sentiment=sentiment,
            wellness_issues=wellness_issues,
            storytelling_issues=storytelling_issues,
            specific_requests=specific_requests,
            suggested_action=suggested_action,
            summary=summary.strip() if summary else "Feedback analyzed",
        )

    def _assign_items(self, section: str, items: list, local_vars: dict) -> None:
        """Helper to assign accumulated items to the right list."""
        # This is a workaround since we can't modify locals() directly
        pass


# =============================================================================
# RATING COLLECTOR (Optional Enhancement)
# =============================================================================

class RatingCollector:
    """Helper class to collect and structure user ratings.

    Can be used by EPA to collect structured ratings before
    passing to Review sub-agent for analysis.
    """

    @staticmethod
    def format_rating_prompt() -> str:
        """Get prompt for collecting ratings from user."""
        return """How would you rate this content?

1. **Accuracy** (facts and information): 1-5
2. **Engagement** (hook and storytelling): 1-5
3. **Tone** (matches requested style): 1-5
4. **Overall**: 1-5

And any specific feedback or changes you'd like?"""

    @staticmethod
    def parse_ratings(user_response: str) -> dict:
        """Parse ratings from user response."""
        import re

        ratings = {
            "accuracy": None,
            "engagement": None,
            "tone": None,
            "overall": None,
            "feedback": "",
        }

        # Try to extract numbers
        numbers = re.findall(r'\b([1-5])\b', user_response)

        if len(numbers) >= 4:
            ratings["accuracy"] = int(numbers[0])
            ratings["engagement"] = int(numbers[1])
            ratings["tone"] = int(numbers[2])
            ratings["overall"] = int(numbers[3])

        # Rest of response is feedback
        # Remove the numbers pattern and keep the text
        feedback = re.sub(r'\b[1-5]\b', '', user_response)
        feedback = re.sub(r'(accuracy|engagement|tone|overall|rating)[:\s]*', '', feedback, flags=re.IGNORECASE)
        ratings["feedback"] = feedback.strip()

        return ratings
