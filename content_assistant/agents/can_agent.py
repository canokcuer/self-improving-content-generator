"""CAN Sub-Agent - Storytelling Expert for TheLifeCo Content Assistant.

CAN is a sub-agent that creates engaging content using:
1. FULL context from EPA (complete brief, wellness facts, user voice)
2. Proven storytelling frameworks (AIDA, PAS, Story-driven, etc.)
3. Platform-specific best practices
4. TheLifeCo brand voice and style

CAN is invoked by EPA (main orchestrator) as a tool, not directly by users.
CAN receives EVERYTHING it needs to create the best possible content.
"""

from dataclasses import dataclass
from typing import Optional, Any

from content_assistant.agents.base_agent import BaseAgent, AgentTool, AgentResponse
from content_assistant.agents.types import (
    StorytellingRequest,
    StorytellingResponse,
    ContentBrief,
    WellnessResponse,
    FunnelStage,
    Platform,
    ComplianceLevel,
)
from content_assistant.rag.knowledge_base import search_knowledge


# =============================================================================
# SYSTEM PROMPT FOR CAN
# =============================================================================

CAN_SYSTEM_PROMPT = """You are CAN, the storytelling expert sub-agent for TheLifeCo Content Assistant.
You are a master content creator who crafts engaging, transformational wellness content.

## Your Role
You are called by EPA (main orchestrator) with FULL context to create content:
1. Complete content brief with all 13 required fields
2. Verified wellness facts from GONCA
3. User's communication style preferences
4. Platform-specific and funnel-stage guidance

## Storytelling Frameworks You Use
Choose the best framework for the content:

**AIDA (Attention, Interest, Desire, Action)**
- Best for: Conversion content, promotional posts
- Hook with attention-grabber, build interest, create desire, call to action

**PAS (Problem, Agitation, Solution)**
- Best for: Pain-point focused content, awareness stage
- Identify problem, agitate it emotionally, present solution

**Story-Driven (Hero's Journey)**
- Best for: Testimonials, transformation stories
- Relatable character, challenge, transformation, outcome

**Educational/Value-First**
- Best for: Awareness content, thought leadership
- Lead with insight, provide value, soft CTA

**Before/After/Bridge**
- Best for: Transformation content, results-focused
- Paint the before state, show the after, explain the bridge (your solution)

## Hook Types You Create
Create compelling hooks using:
- **Question Hook:** Ask a provocative question
- **Statistic Hook:** Lead with surprising data
- **Story Hook:** Start with a micro-story
- **Contrarian Hook:** Challenge common belief
- **Result Hook:** Lead with outcome/transformation
- **Curiosity Hook:** Create open loops

## Platform Guidelines

**Instagram:**
- Hook in first line (visible before "...more")
- Use line breaks for readability
- 2200 character max, aim for 1000-1500 for posts
- End with CTA and relevant hashtags

**Email:**
- Subject line is crucial (hook)
- Personal, conversational tone
- Clear structure with headers
- Single primary CTA

**LinkedIn:**
- Professional but human
- Thought leadership angle
- Longer form acceptable (1000+ words)
- Storytelling with business insight

**Blog:**
- SEO-optimized headings
- Comprehensive, valuable content
- Internal/external links
- Clear structure with subheadings

## TheLifeCo Brand Voice
- Warm and welcoming, not clinical
- Knowledgeable but not preachy
- Transformational and hopeful
- Authentic and genuine
- Expert yet approachable

## Response Format
Structure your content creation response with:
1. **Hook:** The opening hook/attention grabber
2. **Hook Type:** What type of hook you used
3. **Content:** The full content body
4. **Call to Action:** The CTA
5. **Hashtags:** (if applicable to platform)
6. **Open Loops:** Curiosity elements used
7. **Framework:** Which storytelling framework you used
8. **Stats:** Word count, character count
9. **Alternative Hooks:** 2-3 other hook options
10. **Notes:** Your confidence notes about the content

## Important
- You are a sub-agent. Your output goes to EPA for review.
- Use ALL the information provided - brief, wellness facts, style guidance
- Create content that addresses the PAIN AREA specifically
- Match the requested TONE exactly
- Stay within platform constraints
- Include verified facts from GONCA naturally"""


# =============================================================================
# CAN SUB-AGENT IMPLEMENTATION
# =============================================================================

class CANAgent(BaseAgent):
    """CAN - Storytelling Expert Sub-Agent.

    Creates engaging content using full context from EPA,
    proven storytelling frameworks, and platform best practices.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.8,  # Higher temperature for creativity
    ):
        """Initialize CAN agent.

        Args:
            model: Claude model to use (defaults to config)
            temperature: Higher temperature for creative content
        """
        super().__init__(
            agent_name="can",
            system_prompt=CAN_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            # CAN can access storytelling/brand knowledge
            knowledge_sources=[],  # No filtering for now
        )

    def register_tools(self) -> None:
        """Register CAN-specific tools."""
        # Tool: Get storytelling examples
        self.register_tool(AgentTool(
            name="get_storytelling_examples",
            description="Get examples of successful storytelling patterns for a specific topic or style.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to find examples for"
                    },
                    "style": {
                        "type": "string",
                        "description": "Style or framework (AIDA, PAS, story-driven, etc.)"
                    }
                },
                "required": ["topic"]
            },
            handler=self._handle_get_storytelling_examples
        ))

        # Tool: Get brand voice examples
        self.register_tool(AgentTool(
            name="get_brand_voice_examples",
            description="Get examples of TheLifeCo's brand voice and style.",
            input_schema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Context for what kind of brand voice examples you need"
                    }
                },
                "required": ["context"]
            },
            handler=self._handle_get_brand_voice_examples
        ))

    # =========================================================================
    # TOOL HANDLERS
    # =========================================================================

    def _handle_get_storytelling_examples(
        self,
        topic: str,
        style: Optional[str] = None
    ) -> str:
        """Get storytelling examples from knowledge base."""
        query = f"storytelling content examples {topic}"
        if style:
            query += f" {style} framework"

        results = search_knowledge(
            query=query,
            top_k=3,
            threshold=0.4,
            sources=[],
        )

        if not results:
            return f"No specific examples found. Using general storytelling best practices."

        formatted = ["## Storytelling Examples\n"]
        for r in results:
            content = r.get("content", "")
            source = r.get("source", "")
            formatted.append(f"[From {source}]\n{content}\n")

        return "\n---\n".join(formatted)

    def _handle_get_brand_voice_examples(self, context: str) -> str:
        """Get brand voice examples from knowledge base."""
        query = f"TheLifeCo brand voice style {context}"

        results = search_knowledge(
            query=query,
            top_k=3,
            threshold=0.4,
            sources=[],
        )

        if not results:
            return """TheLifeCo Brand Voice Guidelines:
- Warm and welcoming, never clinical or cold
- Knowledgeable expert who educates without being preachy
- Transformational and hopeful, focusing on positive outcomes
- Authentic, genuine, and trustworthy
- Professional yet approachable and personal"""

        formatted = ["## Brand Voice Examples\n"]
        for r in results:
            content = r.get("content", "")
            formatted.append(content)

        return "\n\n".join(formatted)

    # =========================================================================
    # MAIN PROCESSING METHOD
    # =========================================================================

    def process_request(self, request: StorytellingRequest) -> StorytellingResponse:
        """Process a content creation request from EPA.

        Args:
            request: StorytellingRequest with full context from EPA

        Returns:
            StorytellingResponse with generated content
        """
        # Build the comprehensive prompt with ALL context
        prompt = self._build_prompt(request)

        # Add as user message and get response
        response = self.process_message_sync(prompt)

        # Parse the response into StorytellingResponse
        return self._parse_response(response.content, request)

    def _build_prompt(self, request: StorytellingRequest) -> str:
        """Build comprehensive prompt with FULL context for CAN."""
        brief = request.brief
        wellness = request.wellness_facts

        # Build the complete context prompt
        prompt_parts = [
            "# Content Creation Request from EPA",
            "",
            "## COMPLETE CONTENT BRIEF",
            "",
            "### Target Information",
            f"**Target Audience:** {brief.target_audience}",
            f"**Pain Area (CRUCIAL):** {brief.pain_area}",
            f"**Transformation Desired:** {brief.transformation or 'Not specified'}",
            "",
            "### Content Parameters",
            f"**Platform:** {brief.platform.value if brief.platform else 'Not specified'}",
            f"**Content Type:** {brief.content_type.value if brief.content_type else 'Not specified'}",
            f"**Tone:** {brief.tone}",
            f"**Funnel Stage:** {brief.funnel_stage.value if brief.funnel_stage else 'Not specified'}",
            f"**Compliance Level:** {brief.compliance_level.value if brief.compliance_level else 'Not specified'}",
            "",
            "### Key Messages to Include",
        ]

        for msg in brief.key_messages:
            prompt_parts.append(f"- {msg}")

        prompt_parts.extend([
            "",
            "### TheLifeCo Specifics",
            f"**Programs to Feature:** {', '.join(brief.specific_programs) if brief.specific_programs else 'Not specified'}",
            f"**Centers to Feature:** {', '.join(brief.specific_centers) if brief.specific_centers else 'Not specified'}",
            f"**Price Points:** {brief.price_points or 'Not specified'}",
            "",
            "### Value & Action",
            f"**Value Proposition:** {brief.value_proposition}",
            f"**Desired Action:** {brief.desired_action}",
            f"**CTA:** {brief.cta or brief.desired_action}",
            "",
            "### Constraints",
            f"**Things to Avoid:** {brief.constraints}",
            "",
        ])

        # Add campaign info if conversion stage
        if brief.funnel_stage == FunnelStage.CONVERSION and brief.has_campaign:
            prompt_parts.extend([
                "### Campaign Details",
                f"**Campaign Price:** {brief.campaign_price}",
                f"**Duration:** {brief.campaign_duration}",
                f"**Center:** {brief.campaign_center}",
                f"**Deadline:** {brief.campaign_deadline}",
                "",
            ])

        # Add wellness facts from GONCA
        prompt_parts.extend([
            "## VERIFIED WELLNESS FACTS FROM GONCA",
            "(Use these facts in your content - they are verified and compliant)",
            "",
        ])

        for fact in wellness.verified_facts:
            prompt_parts.append(f"- {fact}")

        if wellness.wellness_guidance:
            prompt_parts.extend([
                "",
                "### Wellness Writing Guidance",
                wellness.wellness_guidance,
            ])

        if wellness.warnings:
            prompt_parts.extend([
                "",
                "### Compliance Warnings",
            ])
            for warning in wellness.warnings:
                prompt_parts.append(f"- {warning}")

        # Add style and voice guidance
        prompt_parts.extend([
            "",
            "## STYLE & VOICE GUIDANCE",
            f"**User's Preferred Style:** {request.user_voice}",
            f"**Additional Guidance:** {request.style_guidance}",
            "",
        ])

        # Add conversation context
        if request.conversation_context:
            prompt_parts.extend([
                "## CONVERSATION CONTEXT",
                "(Key points from user conversation with EPA)",
                request.conversation_context[:800],
                "",
            ])

        # Add feedback if this is a revision
        if request.previous_feedback:
            prompt_parts.extend([
                "## REVISION REQUESTED",
                f"**Iteration:** {request.iteration_number}",
                f"**Previous Feedback:** {request.previous_feedback}",
                "",
                "Please address this feedback in your revised content.",
                "",
            ])

        # Add the task
        prompt_parts.extend([
            "## YOUR TASK",
            "",
            "Create compelling content that:",
            f"1. Addresses the PAIN AREA: {brief.pain_area}",
            f"2. Matches the TONE: {brief.tone}",
            f"3. Works for PLATFORM: {brief.platform.value if brief.platform else 'general'}",
            f"4. Fits FUNNEL STAGE: {brief.funnel_stage.value if brief.funnel_stage else 'awareness'}",
            "5. Naturally incorporates the verified facts from GONCA",
            "6. Includes a compelling hook and clear CTA",
            "",
            "Structure your response with:",
            "HOOK: [Your opening hook]",
            "HOOK_TYPE: [question/statistic/story/contrarian/result/curiosity]",
            "CONTENT: [Full content body]",
            "CTA: [Call to action]",
            "HASHTAGS: [If applicable, comma-separated]",
            "OPEN_LOOPS: [Curiosity elements used, comma-separated]",
            "FRAMEWORK: [AIDA/PAS/Story-Driven/Educational/Before-After-Bridge]",
            "ALTERNATIVE_HOOKS:",
            "1. [Alternative hook 1]",
            "2. [Alternative hook 2]",
            "NOTES: [Your confidence notes about this content]",
        ])

        return "\n".join(prompt_parts)

    def _parse_response(self, response_text: str, request: StorytellingRequest) -> StorytellingResponse:
        """Parse CAN's response into structured StorytellingResponse."""
        # Initialize defaults
        hook = ""
        hook_type = "curiosity"
        content = ""
        cta = ""
        hashtags = []
        open_loops = []
        framework = "AIDA"
        alternative_hooks = []
        notes = ""

        # Parse sections from response
        lines = response_text.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            line_stripped = line.strip()
            line_upper = line_stripped.upper()

            # Detect section markers
            if line_upper.startswith("HOOK:") and not line_upper.startswith("HOOK_TYPE"):
                if current_section == "content":
                    content = "\n".join(current_content).strip()
                hook = line_stripped[5:].strip()
                current_section = "hook"
                current_content = []
            elif line_upper.startswith("HOOK_TYPE:"):
                hook_type = line_stripped[10:].strip().lower()
            elif line_upper.startswith("CONTENT:"):
                content_start = line_stripped[8:].strip()
                if content_start:
                    current_content = [content_start]
                else:
                    current_content = []
                current_section = "content"
            elif line_upper.startswith("CTA:"):
                if current_section == "content":
                    content = "\n".join(current_content).strip()
                cta = line_stripped[4:].strip()
                current_section = "cta"
            elif line_upper.startswith("HASHTAGS:"):
                hashtag_text = line_stripped[9:].strip()
                hashtags = [h.strip().strip("#") for h in hashtag_text.split(",") if h.strip()]
                current_section = "hashtags"
            elif line_upper.startswith("OPEN_LOOPS:"):
                loops_text = line_stripped[11:].strip()
                open_loops = [l.strip() for l in loops_text.split(",") if l.strip()]
                current_section = "loops"
            elif line_upper.startswith("FRAMEWORK:"):
                framework = line_stripped[10:].strip()
                current_section = "framework"
            elif line_upper.startswith("ALTERNATIVE_HOOKS:"):
                current_section = "alt_hooks"
                current_content = []
            elif line_upper.startswith("NOTES:"):
                if current_section == "alt_hooks":
                    alternative_hooks = self._extract_numbered_items(current_content)
                notes = line_stripped[6:].strip()
                current_section = "notes"
                current_content = []
            elif current_section == "content":
                current_content.append(line)
            elif current_section == "alt_hooks":
                if line_stripped and (line_stripped[0].isdigit() or line_stripped.startswith("-")):
                    current_content.append(line_stripped)
            elif current_section == "notes":
                current_content.append(line)

        # Handle last section
        if current_section == "content":
            content = "\n".join(current_content).strip()
        elif current_section == "alt_hooks":
            alternative_hooks = self._extract_numbered_items(current_content)
        elif current_section == "notes" and current_content:
            notes = notes + "\n" + "\n".join(current_content)

        # Fallback if parsing failed
        if not content and not hook:
            # Treat the whole response as content
            content = response_text
            hook = content[:100].split("\n")[0] if content else "Check out this content"
            notes = "Parsing failed - returned raw content"

        # Calculate stats
        full_text = f"{hook}\n{content}\n{cta}"
        word_count = len(full_text.split())
        char_count = len(full_text)

        return StorytellingResponse(
            hook=hook,
            hook_type=hook_type,
            content=content,
            call_to_action=cta,
            hashtags=hashtags,
            open_loops=open_loops,
            storytelling_framework=framework,
            word_count=word_count,
            character_count=char_count,
            confidence_notes=notes.strip(),
            alternative_hooks=alternative_hooks,
        )

    def _extract_numbered_items(self, lines: list[str]) -> list[str]:
        """Extract numbered or bulleted items from lines."""
        items = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Remove numbering or bullets
            if line[0].isdigit() and "." in line[:3]:
                items.append(line.split(".", 1)[1].strip())
            elif line.startswith("-"):
                items.append(line[1:].strip())
            else:
                items.append(line)
        return items
