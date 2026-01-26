"""GONCA Sub-Agent - Wellness Expert for TheLifeCo Content Assistant.

GONCA is a sub-agent that provides:
1. Verified TheLifeCo program information
2. Center details (Antalya, Bodrum, Phuket, Sharm)
3. Wellness facts and health claims
4. Compliance guidance for wellness content

GONCA is invoked by EPA (main orchestrator) as a tool, not directly by users.
GONCA has FULL access to the knowledge base (no source filtering).
"""

from dataclasses import dataclass
from typing import Optional, Any

from content_assistant.agents.base_agent import BaseAgent, AgentTool, AgentResponse
from content_assistant.agents.types import (
    WellnessRequest,
    WellnessResponse,
    ContentBrief,
)
from content_assistant.rag.knowledge_base import search_knowledge


# =============================================================================
# SYSTEM PROMPT FOR GONCA
# =============================================================================

GONCA_SYSTEM_PROMPT = """You are GONCA, the wellness expert sub-agent for TheLifeCo Content Assistant.
You are a deep expert on TheLifeCo's programs, centers, and wellness offerings.

## Your Role
You are called by EPA (main orchestrator) to provide:
1. Verified facts about TheLifeCo programs and services
2. Accurate center information (Antalya, Bodrum, Phuket, Sharm)
3. Wellness and health guidance that's compliant with regulations
4. Program benefits, processes, and outcomes

## Your Knowledge Areas
- **Programs:** Master Detox, Weight Loss, Anti-Aging, Mental Wellness, Optimal Health, etc.
- **Centers:** Each center's unique features, accommodations, and offerings
- **Treatments:** Therapies, modalities, medical services available
- **Philosophy:** TheLifeCo's approach to holistic wellness

## Compliance Guidelines
For HIGH compliance level content:
- Use hedging language ("may help", "can support", "has been shown to")
- Avoid definitive medical claims
- Reference generally accepted wellness principles
- Add appropriate disclaimers when needed

For LOW compliance level content:
- More creative freedom with language
- Still avoid false or misleading claims
- Can use stronger benefit statements
- Focus on transformation and experience

## Response Format
You must respond with verified information structured as:
1. **Verified Facts:** List of facts to include in content
2. **Program Details:** Relevant program information
3. **Center Info:** Relevant center information
4. **Guidance:** Wellness writing guidance and compliance notes
5. **Warnings:** Any compliance warnings
6. **Confidence:** How confident you are in the information (0-1)
7. **Sources:** Which knowledge base sources you used

Search the knowledge base thoroughly before responding. If you cannot find
specific information, say so clearly rather than making assumptions.

## Important
- You are a sub-agent, not user-facing. Your output goes to EPA for review.
- Be thorough and accurate. EPA relies on your expertise.
- If asked about something outside your knowledge, say so clearly.
- Always cite which sources your information comes from."""


# =============================================================================
# GONCA SUB-AGENT IMPLEMENTATION
# =============================================================================

class GONCAAgent(BaseAgent):
    """GONCA - Wellness Expert Sub-Agent.

    Provides verified TheLifeCo information and wellness guidance
    to EPA for content generation.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.3,  # Lower temperature for factual accuracy
    ):
        """Initialize GONCA agent.

        Args:
            model: Claude model to use (defaults to config)
            temperature: Lower temperature for more factual responses
        """
        super().__init__(
            agent_name="gonca",
            system_prompt=GONCA_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            # GONCA has FULL knowledge access - no filtering
            knowledge_sources=[],
        )

    def register_tools(self) -> None:
        """Register GONCA-specific tools.

        GONCA uses the built-in search_knowledge tool and adds
        specialized tools for program and center lookups.
        """
        # Tool: Get detailed program information
        self.register_tool(AgentTool(
            name="get_program_details",
            description="Get detailed information about a specific TheLifeCo program including benefits, duration, activities, and outcomes.",
            input_schema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "Name of the program (e.g., 'Master Detox', 'Weight Loss', 'Mental Wellness')"
                    },
                    "aspects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific aspects to look up: 'benefits', 'duration', 'activities', 'outcomes', 'inclusions'"
                    }
                },
                "required": ["program_name"]
            },
            handler=self._handle_get_program_details
        ))

        # Tool: Get center information
        self.register_tool(AgentTool(
            name="get_center_info",
            description="Get detailed information about a TheLifeCo center including location, facilities, and unique features.",
            input_schema={
                "type": "object",
                "properties": {
                    "center_name": {
                        "type": "string",
                        "description": "Center name: 'antalya', 'bodrum', 'phuket', 'sharm'"
                    },
                    "aspects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific aspects: 'location', 'facilities', 'accommodations', 'unique_features', 'activities'"
                    }
                },
                "required": ["center_name"]
            },
            handler=self._handle_get_center_info
        ))

        # Tool: Get treatment information
        self.register_tool(AgentTool(
            name="get_treatment_info",
            description="Get information about specific treatments or therapies offered at TheLifeCo.",
            input_schema={
                "type": "object",
                "properties": {
                    "treatment_name": {
                        "type": "string",
                        "description": "Name of treatment (e.g., 'colon hydrotherapy', 'IV therapy', 'ozone therapy')"
                    }
                },
                "required": ["treatment_name"]
            },
            handler=self._handle_get_treatment_info
        ))

    # =========================================================================
    # TOOL HANDLERS
    # =========================================================================

    def _handle_get_program_details(
        self,
        program_name: str,
        aspects: Optional[list[str]] = None
    ) -> str:
        """Get detailed program information from knowledge base."""
        # Build comprehensive query
        aspect_str = " ".join(aspects) if aspects else "benefits duration activities inclusions outcomes"
        query = f"TheLifeCo {program_name} program {aspect_str}"

        results = search_knowledge(
            query=query,
            top_k=5,
            threshold=0.4,
            sources=[],  # No filtering
        )

        if not results:
            return f"No detailed information found for program '{program_name}'. Please verify the program name."

        formatted = [f"## {program_name} Program Information\n"]
        for r in results:
            source = r.get("source", "unknown")
            content = r.get("content", "")
            similarity = r.get("similarity", 0)
            formatted.append(f"[Source: {source}, Relevance: {similarity:.2f}]\n{content}\n")

        return "\n---\n".join(formatted)

    def _handle_get_center_info(
        self,
        center_name: str,
        aspects: Optional[list[str]] = None
    ) -> str:
        """Get center information from knowledge base."""
        center_name = center_name.lower()
        valid_centers = ["antalya", "bodrum", "phuket", "sharm"]

        if center_name not in valid_centers:
            return f"Unknown center '{center_name}'. Valid centers: {', '.join(valid_centers)}"

        aspect_str = " ".join(aspects) if aspects else "location facilities accommodations features"
        query = f"TheLifeCo {center_name} center {aspect_str}"

        results = search_knowledge(
            query=query,
            top_k=5,
            threshold=0.4,
            sources=[],
        )

        if not results:
            return f"No detailed information found for center '{center_name}'."

        formatted = [f"## TheLifeCo {center_name.title()} Center\n"]
        for r in results:
            source = r.get("source", "unknown")
            content = r.get("content", "")
            similarity = r.get("similarity", 0)
            formatted.append(f"[Source: {source}, Relevance: {similarity:.2f}]\n{content}\n")

        return "\n---\n".join(formatted)

    def _handle_get_treatment_info(self, treatment_name: str) -> str:
        """Get treatment information from knowledge base."""
        query = f"TheLifeCo {treatment_name} treatment therapy benefits process"

        results = search_knowledge(
            query=query,
            top_k=3,
            threshold=0.4,
            sources=[],
        )

        if not results:
            return f"No information found for treatment '{treatment_name}'."

        formatted = [f"## {treatment_name.title()} Treatment\n"]
        for r in results:
            source = r.get("source", "unknown")
            content = r.get("content", "")
            formatted.append(f"[Source: {source}]\n{content}\n")

        return "\n---\n".join(formatted)

    # =========================================================================
    # MAIN PROCESSING METHOD
    # =========================================================================

    def process_request(self, request: WellnessRequest) -> WellnessResponse:
        """Process a wellness information request from EPA.

        Args:
            request: WellnessRequest with query and context from EPA

        Returns:
            WellnessResponse with verified facts and guidance
        """
        # Build the prompt for GONCA with full context
        prompt = self._build_prompt(request)

        # Add as user message and get response
        response = self.process_message_sync(prompt)

        # Parse the response into WellnessResponse
        return self._parse_response(response.content, request)

    def _build_prompt(self, request: WellnessRequest) -> str:
        """Build prompt for GONCA from request."""
        brief = request.brief

        prompt_parts = [
            "## Request from EPA",
            "",
            f"**Query:** {request.query}",
            "",
            "## Content Brief Context",
            f"- **Pain Area:** {brief.pain_area or 'Not specified'}",
            f"- **Target Audience:** {brief.target_audience or 'Not specified'}",
            f"- **Programs:** {', '.join(brief.specific_programs) if brief.specific_programs else 'Not specified'}",
            f"- **Centers:** {', '.join(brief.specific_centers) if brief.specific_centers else 'Not specified'}",
            f"- **Compliance Level:** {brief.compliance_level.value if brief.compliance_level else 'Not specified'}",
            f"- **Funnel Stage:** {brief.funnel_stage.value if brief.funnel_stage else 'Not specified'}",
            "",
        ]

        if request.specific_topics:
            prompt_parts.append("## Specific Topics to Research")
            for topic in request.specific_topics:
                prompt_parts.append(f"- {topic}")
            prompt_parts.append("")

        if request.context:
            prompt_parts.append("## Conversation Context")
            prompt_parts.append(request.context[:1000])  # Limit context length
            prompt_parts.append("")

        prompt_parts.extend([
            "## Your Task",
            "Search the knowledge base and provide verified information for the topics above.",
            "Structure your response with:",
            "1. VERIFIED FACTS: (bullet list of facts to use in content)",
            "2. PROGRAM DETAILS: (if applicable)",
            "3. CENTER INFO: (if applicable)",
            "4. WELLNESS GUIDANCE: (how to write about this topic compliantly)",
            "5. WARNINGS: (any compliance concerns)",
            "6. CONFIDENCE: (your confidence level 0-100%)",
            "7. SOURCES: (which knowledge base files you used)",
        ])

        return "\n".join(prompt_parts)

    def _parse_response(self, response_text: str, request: WellnessRequest) -> WellnessResponse:
        """Parse GONCA's response into structured WellnessResponse."""
        # Default response structure
        verified_facts = []
        program_details = {}
        center_info = {}
        wellness_guidance = ""
        warnings = []
        confidence = 0.7
        sources = []

        # Parse sections from response
        current_section = None
        current_content = []

        for line in response_text.split("\n"):
            line_lower = line.lower().strip()

            # Detect section headers
            if "verified facts" in line_lower or "verified information" in line_lower:
                current_section = "facts"
                current_content = []
            elif "program details" in line_lower or "program information" in line_lower:
                if current_section == "facts":
                    verified_facts = self._extract_bullet_points(current_content)
                current_section = "program"
                current_content = []
            elif "center info" in line_lower or "center information" in line_lower:
                if current_section == "program":
                    program_details = {"details": "\n".join(current_content)}
                current_section = "center"
                current_content = []
            elif "wellness guidance" in line_lower or "writing guidance" in line_lower:
                if current_section == "center":
                    center_info = {"details": "\n".join(current_content)}
                current_section = "guidance"
                current_content = []
            elif "warning" in line_lower:
                if current_section == "guidance":
                    wellness_guidance = "\n".join(current_content)
                current_section = "warnings"
                current_content = []
            elif "confidence" in line_lower:
                if current_section == "warnings":
                    warnings = self._extract_bullet_points(current_content)
                current_section = "confidence"
                # Try to extract confidence percentage
                import re
                match = re.search(r'(\d+)\s*%', line)
                if match:
                    confidence = int(match.group(1)) / 100
            elif "source" in line_lower:
                current_section = "sources"
                current_content = []
            else:
                current_content.append(line)

        # Handle last section
        if current_section == "facts":
            verified_facts = self._extract_bullet_points(current_content)
        elif current_section == "guidance":
            wellness_guidance = "\n".join(current_content)
        elif current_section == "warnings":
            warnings = self._extract_bullet_points(current_content)
        elif current_section == "sources":
            sources = self._extract_bullet_points(current_content)

        # Fallback: if no structured parsing, treat whole response as facts
        if not verified_facts and not wellness_guidance:
            verified_facts = [response_text[:500]]
            wellness_guidance = "Review content for accuracy and compliance."

        return WellnessResponse(
            verified_facts=verified_facts,
            program_details=program_details,
            center_info=center_info,
            wellness_guidance=wellness_guidance,
            sources_used=sources or ["knowledge_base"],
            confidence_level=confidence,
            warnings=warnings,
        )

    def _extract_bullet_points(self, lines: list[str]) -> list[str]:
        """Extract bullet points from lines."""
        bullets = []
        for line in lines:
            line = line.strip()
            if line.startswith(("-", "*", "•")):
                bullets.append(line[1:].strip())
            elif line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                bullets.append(line[2:].strip())
            elif line and not line.startswith("#"):
                # Non-empty line that's not a header
                bullets.append(line)
        return [b for b in bullets if b]  # Filter empty strings
