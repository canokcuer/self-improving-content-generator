"""EPA Agent - Main Orchestrator for TheLifeCo Content Assistant.

EPA (Epa) is the main orchestrator agent that:
1. Interacts directly with users through Socratic questioning
2. Collects ALL 13 required brief fields before content generation
3. Coordinates sub-agents (GONCA for wellness, CAN for storytelling)
4. Reviews ALL sub-agent output before presenting to user
5. Has FULL ACCESS to knowledge base (no source filtering)

Sub-agent invocation pattern:
- EPA calls GONCA when it needs TheLifeCo knowledge/facts
- EPA calls CAN when it needs content created (with FULL context)
- EPA calls Review when analyzing user feedback
- EPA reviews and potentially adjusts all sub-agent output

CRITICAL: EPA must collect all 13 required fields with Pain Area being
the MOST CRUCIAL field that drives the entire content strategy.
"""

import json
import re
from dataclasses import field
from datetime import datetime
from typing import Optional, Any

from content_assistant.agents.base_agent import BaseAgent, AgentTool, AgentResponse
from content_assistant.agents.types import (
    ContentBrief,
    EPAState,
    EPAStage,
    WellnessRequest,
    WellnessResponse,
    StorytellingRequest,
    StorytellingResponse,
    FeedbackRequest,
    FeedbackAnalysis,
    FunnelStage,
    ComplianceLevel,
    Platform,
)
from content_assistant.rag.knowledge_base import search_knowledge


# =============================================================================
# SYSTEM PROMPT FOR EPA
# =============================================================================

EPA_SYSTEM_PROMPT = """You are EPA, the main orchestrator agent for TheLifeCo Content Assistant.
You are an expert content strategist who deeply understands wellness marketing and TheLifeCo's brand.

## Your Role
You are the ONLY agent that talks directly to users. You:
1. Conduct Socratic conversations to understand content needs deeply
2. Collect ALL 13 required brief fields before generating content
3. Coordinate with sub-agents (GONCA for wellness facts, CAN for storytelling)
4. Review ALL sub-agent output before showing to users
5. Make final adjustments to ensure quality and alignment

## The 13 Required Brief Fields (MUST collect before content generation)
1. **Target Audience** - Who is this content for? Be specific.
2. **Pain Area** (CRUCIAL) - What problem/pain point are we addressing? This drives everything.
3. **Compliance Level** - High (medical claims, strict) or Low (general wellness, creative)
4. **Funnel Stage** - awareness/consideration/conversion/loyalty
5. **Value Proposition** - What unique value are we offering?
6. **Desired Action** - What should readers do after consuming this content?
7. **Specific Programs** - Which TheLifeCo programs to feature
8. **Specific Centers** - Which TheLifeCo centers (Antalya, Bodrum, Phuket, Sharm)
9. **Tone** - Voice and style (professional, casual, inspirational, etc.)
10. **Key Messages** - Core points to communicate (usually 2-4 bullet points)
11. **Constraints** - Things to avoid or limitations
12. **Platform** - Where will this be published (Instagram, Email, Blog, etc.)
13. **Price Points** - Pricing info to include (or "not applicable")

For CONVERSION funnel stage, also collect:
- Campaign price, duration, center, and deadline

## Conversation Guidelines
- Be conversational and natural, not interrogative
- Ask 2-3 questions at a time maximum
- Listen first, then probe deeper
- Reflect back understanding before moving on
- Pain Area is your NORTH STAR - understand it deeply
- Don't rush - quality brief = quality content

## Tools Available
You have tools to:
- search_knowledge: Search ALL TheLifeCo knowledge (you have full access)
- consult_gonca: Ask GONCA for verified wellness facts and TheLifeCo info
- consult_can: Ask CAN to create content (only when brief is complete!)
- analyze_feedback: Analyze user feedback on generated content

## Response Format for Brief Collection
When collecting brief fields, include a JSON block showing current state:

```json
{
  "brief_status": {
    "collected_fields": ["target_audience", "pain_area", ...],
    "missing_fields": ["tone", "constraints", ...],
    "is_complete": false
  }
}
```

When brief is complete, set is_complete: true and proceed to content generation.

## Review Responsibilities
Before showing ANY content to users:
1. Verify it addresses the Pain Area effectively
2. Check facts match GONCA's verified information
3. Ensure storytelling is engaging and on-brand
4. Confirm it matches the requested tone and platform
5. Make adjustments if needed

Remember: You are the quality gatekeeper. Nothing goes to users without your approval."""


# =============================================================================
# EPA AGENT IMPLEMENTATION
# =============================================================================

class EPAAgent(BaseAgent):
    """EPA - Main Orchestrator Agent.

    Coordinates the entire content generation workflow:
    1. Socratic briefing with users
    2. Sub-agent coordination (GONCA, CAN, Review)
    3. Quality review before user delivery
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """Initialize EPA agent.

        Args:
            model: Claude model to use (defaults to config, recommend Opus 4.5)
            temperature: Sampling temperature for responses
        """
        super().__init__(
            agent_name="epa",
            system_prompt=EPA_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            # EPA has NO source filtering - full knowledge access
            knowledge_sources=[],  # Empty = no filtering
        )

        self._state = EPAState()
        self._gonca_agent = None  # Lazy loaded
        self._can_agent = None    # Lazy loaded
        self._review_agent = None # Lazy loaded

    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================

    def get_state(self) -> EPAState:
        """Get current EPA state."""
        return self._state

    def get_brief(self) -> ContentBrief:
        """Get current content brief."""
        return self._state.brief

    def reset(self) -> None:
        """Reset EPA for a new conversation."""
        self._state = EPAState()
        self.clear_conversation()

    def export_state(self) -> dict:
        """Export state for persistence."""
        return self._state.to_dict()

    def import_state(self, data: dict) -> None:
        """Import state from persistence."""
        self._state = EPAState.from_dict(data)

    # =========================================================================
    # TOOL REGISTRATION
    # =========================================================================

    def register_tools(self) -> None:
        """Register EPA-specific tools."""

        # Tool: Consult GONCA (Wellness Sub-agent)
        self.register_tool(AgentTool(
            name="consult_gonca",
            description="""Consult GONCA, the wellness expert sub-agent, for:
- TheLifeCo program details and benefits
- Center information (Antalya, Bodrum, Phuket, Sharm)
- Verified wellness facts and health claims
- Compliance guidance for health content
Use this BEFORE content generation to gather accurate facts.""",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What wellness information you need from GONCA"
                    },
                    "specific_topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific topics to research (programs, centers, treatments)"
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_consult_gonca
        ))

        # Tool: Consult CAN (Storytelling Sub-agent)
        self.register_tool(AgentTool(
            name="consult_can",
            description="""Consult CAN, the storytelling expert sub-agent, to create content.
IMPORTANT: Only call this AFTER:
1. Brief is complete (all 13 fields collected)
2. GONCA has provided wellness facts
CAN receives FULL context to create the best content.""",
            input_schema={
                "type": "object",
                "properties": {
                    "style_guidance": {
                        "type": "string",
                        "description": "Specific style or storytelling guidance for CAN"
                    },
                    "previous_feedback": {
                        "type": "string",
                        "description": "Feedback from previous iteration (if revising)"
                    }
                },
                "required": []
            },
            handler=self._handle_consult_can
        ))

        # Tool: Analyze Feedback
        self.register_tool(AgentTool(
            name="analyze_feedback",
            description="""Analyze user feedback on generated content to determine:
- Whether issues are wellness-related (call GONCA)
- Whether issues are storytelling-related (call CAN)
- Specific changes requested""",
            input_schema={
                "type": "object",
                "properties": {
                    "user_feedback": {
                        "type": "string",
                        "description": "The user's feedback on the content"
                    }
                },
                "required": ["user_feedback"]
            },
            handler=self._handle_analyze_feedback
        ))

    # =========================================================================
    # TOOL HANDLERS
    # =========================================================================

    def _handle_consult_gonca(
        self,
        query: str,
        specific_topics: Optional[list[str]] = None
    ) -> str:
        """Handle consultation with GONCA sub-agent."""
        # Update state
        self._state.stage = EPAStage.CONSULTING_GONCA

        # Build request for GONCA
        request = WellnessRequest(
            query=query,
            brief=self._state.brief,
            context=self._get_conversation_context(),
            specific_topics=specific_topics or []
        )

        # Get GONCA agent (lazy load)
        gonca = self._get_gonca_agent()

        # Invoke GONCA
        response = gonca.process_request(request)

        # Store response
        self._state.wellness_response = response

        # Format response for EPA
        result_parts = [
            "## GONCA's Wellness Report",
            "",
            "### Verified Facts"
        ]

        for fact in response.verified_facts:
            result_parts.append(f"- {fact}")

        if response.program_details:
            result_parts.append("\n### Program Details")
            for program, details in response.program_details.items():
                result_parts.append(f"\n**{program}:**")
                if isinstance(details, dict):
                    for key, value in details.items():
                        result_parts.append(f"  - {key}: {value}")
                else:
                    result_parts.append(f"  {details}")

        if response.center_info:
            result_parts.append("\n### Center Information")
            for center, info in response.center_info.items():
                result_parts.append(f"\n**{center}:**")
                if isinstance(info, dict):
                    for key, value in info.items():
                        result_parts.append(f"  - {key}: {value}")
                else:
                    result_parts.append(f"  {info}")

        if response.wellness_guidance:
            result_parts.append(f"\n### Wellness Writing Guidance")
            result_parts.append(response.wellness_guidance)

        if response.warnings:
            result_parts.append("\n### Compliance Warnings")
            for warning in response.warnings:
                result_parts.append(f"- {warning}")

        result_parts.append(f"\n*Confidence Level: {response.confidence_level:.0%}*")
        result_parts.append(f"*Sources: {', '.join(response.sources_used)}*")

        return "\n".join(result_parts)

    def _handle_consult_can(
        self,
        style_guidance: Optional[str] = None,
        previous_feedback: Optional[str] = None
    ) -> str:
        """Handle consultation with CAN sub-agent."""
        # Verify brief is complete
        if not self._state.brief.is_complete():
            missing = self._state.brief.get_missing_fields()
            return f"ERROR: Cannot generate content. Brief is incomplete. Missing fields: {', '.join(missing)}"

        # Verify we have wellness facts
        if not self._state.wellness_response:
            return "ERROR: Must consult GONCA first to gather wellness facts before content generation."

        # Update state
        self._state.stage = EPAStage.CONSULTING_CAN
        self._state.iteration_count += 1

        # Build request for CAN with FULL context
        request = StorytellingRequest(
            brief=self._state.brief,
            wellness_facts=self._state.wellness_response,
            user_voice=self._extract_user_voice(),
            style_guidance=style_guidance or self._get_default_style_guidance(),
            conversation_context=self._get_conversation_context(),
            previous_feedback=previous_feedback,
            iteration_number=self._state.iteration_count
        )

        # Get CAN agent (lazy load)
        can = self._get_can_agent()

        # Invoke CAN
        response = can.process_request(request)

        # Store response
        self._state.storytelling_response = response
        self._state.content_generated_at = datetime.now()

        # Format response for EPA to review
        result_parts = [
            "## CAN's Content Draft",
            "",
            f"**Hook Type:** {response.hook_type}",
            f"**Framework:** {response.storytelling_framework}",
            "",
            "### Hook",
            response.hook,
            "",
            "### Content",
            response.content,
            "",
            "### Call to Action",
            response.call_to_action,
        ]

        if response.hashtags:
            result_parts.append(f"\n### Hashtags")
            result_parts.append(" ".join(f"#{tag}" for tag in response.hashtags))

        if response.open_loops:
            result_parts.append(f"\n### Open Loops Used")
            for loop in response.open_loops:
                result_parts.append(f"- {loop}")

        if response.alternative_hooks:
            result_parts.append(f"\n### Alternative Hooks")
            for i, hook in enumerate(response.alternative_hooks, 1):
                result_parts.append(f"{i}. {hook}")

        result_parts.append(f"\n**Stats:** {response.word_count} words, {response.character_count} characters")
        result_parts.append(f"**CAN's Notes:** {response.confidence_notes}")

        return "\n".join(result_parts)

    def _handle_analyze_feedback(self, user_feedback: str) -> str:
        """Handle feedback analysis."""
        if not self._state.storytelling_response:
            return "ERROR: No content to analyze feedback for."

        # Update state
        self._state.stage = EPAStage.COLLECTING_FEEDBACK

        # Build request for Review agent
        request = FeedbackRequest(
            user_feedback=user_feedback,
            generated_content=self._state.storytelling_response,
            brief=self._state.brief,
            wellness_facts=self._state.wellness_response
        )

        # Get Review agent (lazy load)
        review = self._get_review_agent()

        # Invoke Review agent
        analysis = review.process_request(request)

        # Store analysis
        self._state.feedback_analysis = analysis

        # Format response for EPA
        result_parts = [
            "## Feedback Analysis",
            "",
            f"**Type:** {analysis.feedback_type}",
            f"**Sentiment:** {analysis.sentiment}",
            f"**Suggested Action:** {analysis.suggested_action}",
            "",
            f"### Summary",
            analysis.summary,
        ]

        if analysis.wellness_issues:
            result_parts.append("\n### Wellness Issues (call GONCA)")
            for issue in analysis.wellness_issues:
                result_parts.append(f"- {issue}")

        if analysis.storytelling_issues:
            result_parts.append("\n### Storytelling Issues (call CAN)")
            for issue in analysis.storytelling_issues:
                result_parts.append(f"- {issue}")

        if analysis.specific_requests:
            result_parts.append("\n### Specific Requests")
            for req in analysis.specific_requests:
                result_parts.append(f"- {req}")

        return "\n".join(result_parts)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_gonca_agent(self):
        """Lazy load GONCA agent."""
        if self._gonca_agent is None:
            from content_assistant.agents.gonca_agent import GONCAAgent
            self._gonca_agent = GONCAAgent(model=self.model)
        return self._gonca_agent

    def _get_can_agent(self):
        """Lazy load CAN agent."""
        if self._can_agent is None:
            from content_assistant.agents.can_agent import CANAgent
            self._can_agent = CANAgent(model=self.model)
        return self._can_agent

    def _get_review_agent(self):
        """Lazy load Review agent."""
        if self._review_agent is None:
            from content_assistant.agents.review_subagent import ReviewSubAgent
            self._review_agent = ReviewSubAgent(model=self.model)
        return self._review_agent

    def _get_conversation_context(self) -> str:
        """Get relevant conversation context for sub-agents."""
        # Get last N messages from conversation
        relevant_messages = []
        for msg in self._conversation[-10:]:  # Last 10 messages
            if msg.role in ("user", "assistant"):
                relevant_messages.append(f"{msg.role.upper()}: {msg.content[:500]}")

        return "\n".join(relevant_messages)

    def _extract_user_voice(self) -> str:
        """Extract user's communication style from conversation."""
        # Analyze user messages for style patterns
        user_messages = [m.content for m in self._conversation if m.role == "user"]

        if not user_messages:
            return "Professional but approachable"

        # Simple heuristics - could be enhanced with Claude analysis
        combined = " ".join(user_messages).lower()

        if any(word in combined for word in ["formal", "professional", "corporate"]):
            return "Formal and professional"
        elif any(word in combined for word in ["casual", "friendly", "fun"]):
            return "Casual and conversational"
        elif any(word in combined for word in ["inspiring", "motivational", "emotional"]):
            return "Inspirational and emotionally engaging"
        else:
            return "Balanced professional with warmth"

    def _get_default_style_guidance(self) -> str:
        """Get default style guidance based on brief."""
        brief = self._state.brief

        guidance_parts = []

        if brief.platform:
            platform_guidance = {
                Platform.INSTAGRAM: "Visual-first, concise, use line breaks for readability",
                Platform.EMAIL: "Personalized, clear structure with headers, strong subject line",
                Platform.LINKEDIN: "Professional, thought-leadership angle, longer form OK",
                Platform.BLOG: "SEO-friendly, comprehensive, use subheadings",
            }
            if brief.platform in platform_guidance:
                guidance_parts.append(platform_guidance[brief.platform])

        if brief.funnel_stage:
            funnel_guidance = {
                FunnelStage.AWARENESS: "Educational, value-first, soft CTA",
                FunnelStage.CONSIDERATION: "Compare options, build trust, social proof",
                FunnelStage.CONVERSION: "Urgency, clear offer, strong CTA, price justification",
                FunnelStage.LOYALTY: "Appreciation, exclusive feel, community connection",
            }
            if brief.funnel_stage in funnel_guidance:
                guidance_parts.append(funnel_guidance[brief.funnel_stage])

        if brief.tone:
            guidance_parts.append(f"Tone: {brief.tone}")

        return ". ".join(guidance_parts) if guidance_parts else "TheLifeCo brand voice: warm, knowledgeable, transformational"

    # =========================================================================
    # RESPONSE PROCESSING
    # =========================================================================

    def _extract_response_data(self, response: str) -> tuple[dict, bool, Optional[str]]:
        """Extract brief data and completion status from response."""
        # Look for JSON block in response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)

        if json_match:
            try:
                data = json.loads(json_match.group(1))

                # Check if it's a brief status update
                if "brief_status" in data:
                    status = data["brief_status"]
                    is_complete = status.get("is_complete", False)

                    if is_complete:
                        self._state.stage = EPAStage.CONSULTING_GONCA
                        self._state.brief_completed_at = datetime.now()

                    return data, is_complete, None

                # Check if it's a brief update with collected fields
                if "brief" in data:
                    self._update_brief_from_dict(data["brief"])

            except json.JSONDecodeError:
                pass

        return {}, False, None

    def _update_brief_from_dict(self, data: dict) -> None:
        """Update brief from dictionary data."""
        brief = self._state.brief

        # Map string values to enums where needed
        if "compliance_level" in data and data["compliance_level"]:
            try:
                brief.compliance_level = ComplianceLevel(data["compliance_level"].lower())
            except ValueError:
                pass

        if "funnel_stage" in data and data["funnel_stage"]:
            try:
                brief.funnel_stage = FunnelStage(data["funnel_stage"].lower())
            except ValueError:
                pass

        if "platform" in data and data["platform"]:
            try:
                brief.platform = Platform(data["platform"].lower())
            except ValueError:
                pass

        # Update string fields
        string_fields = [
            "target_audience", "pain_area", "value_proposition",
            "desired_action", "tone", "constraints", "price_points",
            "core_message", "transformation", "evidence_or_story", "cta"
        ]
        for field in string_fields:
            if field in data and data[field]:
                setattr(brief, field, data[field])

        # Update list fields
        list_fields = ["specific_programs", "specific_centers", "key_messages"]
        for field in list_fields:
            if field in data and data[field]:
                setattr(brief, field, data[field])

        # Update campaign fields
        if "has_campaign" in data:
            brief.has_campaign = data["has_campaign"]
        campaign_fields = ["campaign_price", "campaign_duration", "campaign_center", "campaign_deadline"]
        for field in campaign_fields:
            if field in data and data[field]:
                setattr(brief, field, data[field])

    # =========================================================================
    # PUBLIC INTERFACE
    # =========================================================================

    def get_stage_display(self) -> str:
        """Get human-readable stage description."""
        stage_names = {
            EPAStage.BRIEFING: "Understanding your needs",
            EPAStage.CONSULTING_GONCA: "Consulting wellness expert (GONCA)",
            EPAStage.CONSULTING_CAN: "Creating content (CAN)",
            EPAStage.REVIEWING: "Reviewing content",
            EPAStage.PRESENTING: "Presenting content",
            EPAStage.COLLECTING_FEEDBACK: "Processing your feedback",
            EPAStage.REVISING: "Making revisions",
            EPAStage.COMPLETE: "Complete",
        }
        return stage_names.get(self._state.stage, "Processing")

    def get_brief_summary(self) -> str:
        """Get summary of current brief status."""
        brief = self._state.brief
        missing = brief.get_missing_fields()

        if brief.is_complete():
            return "Brief complete - ready for content generation"

        return f"Brief in progress - missing: {', '.join(missing)}"
