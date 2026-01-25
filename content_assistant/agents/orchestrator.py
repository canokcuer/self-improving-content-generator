"""Orchestrator Agent for TheLifeCo Content Assistant.

The Orchestrator Agent is responsible for:
- Conducting conversational briefings with users
- Asking clarifying questions until 100% aligned
- Detecting marketing funnel stage
- Collecting campaign/pricing information when relevant
- Coordinating handoff to other agents
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from content_assistant.agents.base_agent import BaseAgent, AgentTool
from content_assistant.rag.knowledge_base import search_knowledge


@dataclass
class ContentBrief:
    """Structured content brief extracted from conversation."""

    # Essential
    core_message: Optional[str] = None
    target_audience: Optional[str] = None
    platform: Optional[str] = None
    funnel_stage: Optional[str] = None  # awareness, consideration, conversion, loyalty

    # Important
    pain_point: Optional[str] = None
    pain_area: Optional[str] = None
    compliance_level: Optional[str] = None  # high or low
    value_proposition: Optional[str] = None
    desired_action: Optional[str] = None
    key_messages: list[str] = field(default_factory=list)
    transformation: Optional[str] = None
    content_type: Optional[str] = None  # post, story, carousel, reel, article, etc.
    tone: Optional[str] = None

    # Optional
    specific_program: Optional[str] = None
    specific_programs: list[str] = field(default_factory=list)
    specific_centers: list[str] = field(default_factory=list)
    evidence_or_story: Optional[str] = None
    cta: Optional[str] = None
    constraints: Optional[str] = None
    price_point: Optional[str] = None

    # Campaign-specific (for conversion stage)
    has_campaign: bool = False
    campaign_price: Optional[str] = None
    campaign_duration: Optional[str] = None
    campaign_center: Optional[str] = None
    campaign_deadline: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if brief has minimum required information."""
        base_complete = all([
            self.core_message,
            self.target_audience,
            self.platform,
            self.funnel_stage,
            self.pain_area or self.pain_point,
            self.compliance_level,
            self.value_proposition,
            self.desired_action or self.cta,
            self.key_messages,
            self.constraints,
            self.price_point,
            self.specific_programs or self.specific_program,
            self.specific_centers,
            self.tone,
        ])
        if not base_complete:
            return False
        if self.funnel_stage == "conversion":
            return all([
                self.has_campaign,
                self.campaign_price,
                self.campaign_duration,
                self.campaign_center,
                self.campaign_deadline,
            ])
        return True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "core_message": self.core_message,
            "target_audience": self.target_audience,
            "platform": self.platform,
            "funnel_stage": self.funnel_stage,
            "pain_point": self.pain_point,
            "pain_area": self.pain_area,
            "compliance_level": self.compliance_level,
            "value_proposition": self.value_proposition,
            "desired_action": self.desired_action,
            "key_messages": self.key_messages,
            "transformation": self.transformation,
            "content_type": self.content_type,
            "tone": self.tone,
            "specific_program": self.specific_program,
            "specific_programs": self.specific_programs,
            "specific_centers": self.specific_centers,
            "evidence_or_story": self.evidence_or_story,
            "cta": self.cta,
            "constraints": self.constraints,
            "price_point": self.price_point,
            "has_campaign": self.has_campaign,
            "campaign_price": self.campaign_price,
            "campaign_duration": self.campaign_duration,
            "campaign_center": self.campaign_center,
            "campaign_deadline": self.campaign_deadline,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentBrief":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


ORCHESTRATOR_SYSTEM_PROMPT = """You are the Orchestrator Agent for TheLifeCo Content Assistant. Your role is to have a natural, helpful conversation with users to understand their content needs.

## Your Responsibilities
1. **Understand** what content the user wants to create
2. **Clarify** any ambiguous requirements through natural conversation
3. **Detect** the marketing funnel stage (awareness, consideration, conversion, loyalty)
4. **Collect** campaign details when creating conversion content (price, duration, center, deadline)
5. **Confirm** your understanding before proceeding

## Conversation Guidelines
- Be conversational, not interrogative
- Listen first, then ask follow-up questions
- Offer suggestions and options when helpful
- Validate your understanding by reflecting back
- Don't ask unnecessary questions if context is clear

## What You Need to Gather
Essential (must have before proceeding):
- Core message / what the content is about
- Target audience
- Pain area being addressed
- Compliance level (high/low)
- Funnel stage / goal (awareness, consideration, conversion, loyalty)
- Value proposition
- Desired action
- Key messages (bullet list or short list)
- Constraints / things to avoid
- Platform (Instagram, LinkedIn, Email, Blog, etc.)
- Price point
- Specific program(s)
- Specific center(s)
- Tone (professional, casual, inspirational, etc.)

Additional context to clarify when helpful:
- Desired transformation
- Content type (post, story, carousel, etc.)
- Evidence or story to support the message

For Conversion Content (ask if funnel stage is conversion):
- Is there a specific campaign/promotion?
- What's the price point?
- What duration? (3-day, 7-day, 14-day)
- Which center(s)?
- Any deadline/limited availability?

Before marking a brief complete, confirm all required fields are present. If the funnel stage is
conversion and any campaign fields are missing (campaign flag, price, duration, center, deadline),
explicitly call out what is missing and continue the conversation without setting brief_complete.

## Funnel Stage Detection
- **Awareness**: Educating new audiences, no specific offer, soft CTAs
- **Consideration**: Helping people decide, comparing options, building trust
- **Conversion**: Driving bookings, specific offers/pricing, urgency
- **Loyalty**: Engaging past guests, referrals, community

## Response Format
When you have gathered enough information, include a JSON block in your response. Only set `brief_complete` to true when all Essential fields are collected.

```json
{
  "brief_complete": true,
  "brief": {
    "core_message": "...",
    "target_audience": "...",
    "platform": "...",
    "funnel_stage": "...",
    ...
  }
}
```

If you still need more information, continue the conversation naturally without the JSON block.

## Tools Available
- search_knowledge: Search TheLifeCo knowledge base for program details, center info, etc.
- get_similar_content: Find similar past content that performed well

Use tools proactively to provide better suggestions and validate information."""


class OrchestratorAgent(BaseAgent):
    """Orchestrator Agent for conversational briefing.

    Conducts natural conversations with users to understand their content needs,
    asks clarifying questions, and prepares a structured brief for content generation.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """Initialize the Orchestrator Agent."""
        super().__init__(
            agent_name="orchestrator",
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            knowledge_sources=["orchestrator"],
        )

        self._current_brief = ContentBrief()

    def register_tools(self) -> None:
        """Register orchestrator-specific tools."""
        # Tool: Get similar content examples
        self.register_tool(AgentTool(
            name="get_similar_content",
            description="Find similar past content that performed well, to use as examples or inspiration.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic or theme to find similar content for"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform (optional)",
                        "enum": ["instagram", "linkedin", "email", "blog", "facebook", "twitter"]
                    },
                    "funnel_stage": {
                        "type": "string",
                        "description": "Marketing funnel stage (optional)",
                        "enum": ["awareness", "consideration", "conversion", "loyalty"]
                    }
                },
                "required": ["topic"]
            },
            handler=self._handle_get_similar_content
        ))

        # Tool: Get program details
        self.register_tool(AgentTool(
            name="get_program_details",
            description="Get detailed information about a specific TheLifeCo program.",
            input_schema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "Name of the program (e.g., 'Master Detox', 'Green Juice', 'Mental Wellness')"
                    }
                },
                "required": ["program_name"]
            },
            handler=self._handle_get_program_details
        ))

        # Tool: Get center information
        self.register_tool(AgentTool(
            name="get_center_info",
            description="Get information about a specific TheLifeCo center.",
            input_schema={
                "type": "object",
                "properties": {
                    "center_name": {
                        "type": "string",
                        "description": "Name of the center",
                        "enum": ["antalya", "bodrum", "phuket", "sharm"]
                    }
                },
                "required": ["center_name"]
            },
            handler=self._handle_get_center_info
        ))

    def _handle_get_similar_content(
        self,
        topic: str,
        platform: Optional[str] = None,
        funnel_stage: Optional[str] = None
    ) -> str:
        """Find similar past content."""
        # This would query content_generations table for high-rated content
        # For now, return a placeholder
        query = f"content examples for {topic}"
        if platform:
            query += f" on {platform}"
        if funnel_stage:
            query += f" for {funnel_stage} stage"

        # Search knowledge base for relevant patterns
        results = search_knowledge(
            query,
            top_k=3,
            threshold=0.4,
            sources=self.knowledge_sources,
        )

        if not results:
            return "No similar content examples found. I'll create fresh content based on best practices."

        formatted = ["Here are some relevant examples and patterns:"]
        for r in results:
            content = r.get("content", "")[:500]
            source = r.get("source", "")
            formatted.append(f"\n[From {source}]\n{content}...")

        return "\n".join(formatted)

    def _handle_get_program_details(self, program_name: str) -> str:
        """Get program details from knowledge base."""
        results = search_knowledge(
            f"TheLifeCo {program_name} program details benefits",
            top_k=3,
            threshold=0.5,
            sources=self.knowledge_sources,
        )

        if not results:
            return f"No detailed information found for '{program_name}'. Please verify the program name."

        formatted = [f"Information about {program_name}:"]
        for r in results:
            content = r.get("content", "")
            formatted.append(f"\n{content}")

        return "\n".join(formatted)

    def _handle_get_center_info(self, center_name: str) -> str:
        """Get center information from knowledge base."""
        results = search_knowledge(
            f"TheLifeCo {center_name} center location facilities",
            top_k=3,
            threshold=0.5,
            sources=self.knowledge_sources,
        )

        if not results:
            return f"No information found for center '{center_name}'."

        formatted = [f"Information about TheLifeCo {center_name.title()}:"]
        for r in results:
            content = r.get("content", "")
            formatted.append(f"\n{content}")

        return "\n".join(formatted)

    def _extract_response_data(self, response: str) -> tuple[dict, bool, Optional[str]]:
        """Extract brief data from response if present."""
        # Look for JSON block in response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)

        if json_match:
            try:
                data = json.loads(json_match.group(1))

                if data.get("brief_complete"):
                    brief_data = data.get("brief", {})
                    self._update_brief_from_dict(brief_data)
                    return brief_data, True, "wellness"

            except json.JSONDecodeError:
                pass

        # Try to find inline JSON
        try:
            # Look for {"brief_complete": true pattern
            inline_match = re.search(r'\{[^{}]*"brief_complete"\s*:\s*true[^{}]*\}', response)
            if inline_match:
                # This is a simple case, try to parse larger JSON
                start = response.find('{')
                if start != -1:
                    # Find matching closing brace
                    depth = 0
                    for i, char in enumerate(response[start:]):
                        if char == '{':
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            if depth == 0:
                                try:
                                    data = json.loads(response[start:start+i+1])
                                    if data.get("brief_complete"):
                                        brief_data = data.get("brief", {})
                                        self._update_brief_from_dict(brief_data)
                                        return brief_data, True, "wellness"
                                except json.JSONDecodeError:
                                    pass
                                break
        except Exception:
            pass

        return {}, False, None

    def _update_brief_from_dict(self, data: dict) -> None:
        """Update current brief from dictionary."""
        for key, value in data.items():
            if hasattr(self._current_brief, key) and value is not None:
                setattr(self._current_brief, key, value)

    def get_current_brief(self) -> ContentBrief:
        """Get the current content brief."""
        return self._current_brief

    def reset_brief(self) -> None:
        """Reset the content brief for a new conversation."""
        self._current_brief = ContentBrief()
        self.clear_conversation()

    def set_initial_context(self, context: dict) -> None:
        """Set initial context for the conversation.

        Use this to pre-populate known information.
        """
        self._update_brief_from_dict(context)

        # Add context to system prompt or first message
        if context:
            context_str = "Here's what I already know:\n"
            for key, value in context.items():
                if value:
                    context_str += f"- {key.replace('_', ' ').title()}: {value}\n"

            self.add_message("system", context_str)
