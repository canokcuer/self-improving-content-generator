"""Storytelling Agent for TheLifeCo Content Assistant.

The Storytelling Agent is responsible for:
- Creating engaging content with attention-grabbing hooks
- Optimizing for platform-specific requirements
- Adapting tone and style to funnel stage
- Using proven engagement patterns (open loops, emotional journey)
- Generating multiple content variations
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from content_assistant.agents.base_agent import BaseAgent, AgentTool, AgentResponse
from content_assistant.db.learnings import LearningsError, get_approved_learnings
from content_assistant.rag.knowledge_base import search_knowledge


@dataclass
class ContentPreview:
    """Preview of content before full generation."""
    hook: str
    hook_type: str  # mystery, bold_claim, story, statistic, etc.
    open_loops: list = field(default_factory=list)
    promise: str = ""
    brief_summary: str = ""


@dataclass
class GeneratedContent:
    """Final generated content."""
    content: str
    word_count: int = 0
    hashtags: list = field(default_factory=list)
    preview: Optional[ContentPreview] = None
    variations: list = field(default_factory=list)
    engagement_prediction: float = 0.0

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "word_count": self.word_count,
            "hashtags": self.hashtags,
            "preview": {
                "hook": self.preview.hook if self.preview else "",
                "hook_type": self.preview.hook_type if self.preview else "",
                "open_loops": self.preview.open_loops if self.preview else [],
                "promise": self.preview.promise if self.preview else "",
            },
            "variations": self.variations,
            "engagement_prediction": self.engagement_prediction,
        }


STORYTELLING_SYSTEM_PROMPT = """You are the Storytelling Agent for TheLifeCo Content Assistant. You are a master content creator who specializes in creating engaging, high-converting wellness content.

## Your Responsibilities
1. **Create Hooks**: Craft attention-grabbing openings that stop the scroll
2. **Build Narratives**: Structure content with compelling story arcs
3. **Drive Emotion**: Guide readers through emotional transformation
4. **Maintain Engagement**: Use open loops and curiosity gaps
5. **Optimize for Platform**: Adapt content to platform requirements
6. **Match Funnel Stage**: Adjust style based on audience readiness

## Hook Types (Use Strategically)
- **Mystery**: "The one thing 90% of people get wrong about detox..."
- **Bold Claim**: "You don't need a diet. You need a reset."
- **Story**: "Last January, Maria couldn't climb a flight of stairs..."
- **Statistic**: "73% of chronic fatigue cases are linked to toxin overload."
- **Contrast**: "Everyone talks about weight loss. Nobody talks about this."
- **Curiosity**: "What happens to your body after 72 hours of detox?"
- **Pain Point**: "Tired of feeling tired? There's a reason..."
- **Promise**: "In 7 days, you'll feel 10 years younger."

## Content Style by Funnel Stage

### Awareness Stage
- Educational and value-first
- Relatable pain points
- "Did you know" hooks
- Soft CTAs (learn more, follow)
- Build curiosity, not urgency

### Consideration Stage
- Benefits-focused
- Social proof and testimonials
- Expert positioning
- Comparison content
- Medium CTAs (learn more, get guide)

### Conversion Stage
- Action-oriented
- Specific offers with pricing
- Urgency elements
- Address objections
- Strong CTAs (book now, claim offer)
- Use campaign details provided

### Loyalty Stage
- Warm and appreciative
- Exclusive content feeling
- Community focus
- Referral encouragement
- Relationship CTAs

## Platform Guidelines
- **Instagram**: Visual-first, emoji-friendly, hashtags, 2200 char max
- **LinkedIn**: Professional tone, value-driven, no hashtags in body
- **Email**: Personal, conversational, clear CTA, subject line crucial
- **Blog**: SEO-friendly, structured with headers, 800-1500 words
- **Facebook**: Conversational, shareable, emotional triggers

## Response Format
For preview generation:
```json
{
  "preview": {
    "hook": "The attention-grabbing opening line",
    "hook_type": "mystery|bold_claim|story|statistic|etc",
    "open_loops": ["curiosity gap 1", "curiosity gap 2"],
    "promise": "What the reader will gain",
    "brief_summary": "One-line content direction"
  }
}
```

For full content generation:
```json
{
  "content": {
    "full_text": "The complete content...",
    "word_count": 150,
    "hashtags": ["#wellness", "#detox"],
    "engagement_prediction": 85
  }
}
```

## TheLifeCo Brand Voice
- Warm yet professional
- Empowering, not preachy
- Scientific backing with accessible language
- Transformational focus
- "Rest, restore, rebuild" philosophy
- Over 18 years of expertise
- 40,000+ guests served"""


class StorytellingAgent(BaseAgent):
    """Storytelling Agent for content creation.

    Creates engaging content with hooks, emotional journeys,
    and platform optimization.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.8,  # Higher temperature for creative content
    ):
        """Initialize the Storytelling Agent."""
        super().__init__(
            agent_name="storytelling",
            system_prompt=STORYTELLING_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            knowledge_sources=["storytelling", "brand"],
        )

        self._current_preview: Optional[ContentPreview] = None
        self._current_content: Optional[GeneratedContent] = None

    def register_tools(self) -> None:
        """Register storytelling-specific tools."""
        # Tool: Get hook patterns
        self.register_tool(AgentTool(
            name="get_hook_patterns",
            description="Get hook patterns and examples for a specific type or topic.",
            input_schema={
                "type": "object",
                "properties": {
                    "hook_type": {
                        "type": "string",
                        "description": "Type of hook to get patterns for",
                        "enum": ["mystery", "bold_claim", "story", "statistic", "contrast", "curiosity", "pain_point", "promise"]
                    },
                    "topic": {
                        "type": "string",
                        "description": "Topic to find relevant hooks for"
                    }
                },
                "required": []
            },
            handler=self._handle_get_hook_patterns
        ))

        # Tool: Get platform rules
        self.register_tool(AgentTool(
            name="get_platform_rules",
            description="Get content rules and best practices for a specific platform.",
            input_schema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "description": "Target platform",
                        "enum": ["instagram", "linkedin", "email", "blog", "facebook", "twitter"]
                    }
                },
                "required": ["platform"]
            },
            handler=self._handle_get_platform_rules
        ))

        # Tool: Get engagement tactics
        self.register_tool(AgentTool(
            name="get_engagement_tactics",
            description="Get engagement tactics and psychological triggers.",
            input_schema={
                "type": "object",
                "properties": {
                    "tactic_type": {
                        "type": "string",
                        "description": "Type of tactic to get",
                        "enum": ["open_loops", "emotional_triggers", "social_proof", "urgency", "curiosity"]
                    }
                },
                "required": []
            },
            handler=self._handle_get_engagement_tactics
        ))

        # Tool: Get CTA templates
        self.register_tool(AgentTool(
            name="get_cta_templates",
            description="Get call-to-action templates for a funnel stage.",
            input_schema={
                "type": "object",
                "properties": {
                    "funnel_stage": {
                        "type": "string",
                        "description": "Marketing funnel stage",
                        "enum": ["awareness", "consideration", "conversion", "loyalty"]
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform (optional)"
                    }
                },
                "required": ["funnel_stage"]
            },
            handler=self._handle_get_cta_templates
        ))

        # Tool: Get few-shot examples
        self.register_tool(AgentTool(
            name="get_few_shot_examples",
            description="Get high-performing content examples similar to the current brief.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic or theme to find examples for"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform (optional)"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of examples to return",
                        "default": 3
                    }
                },
                "required": ["topic"]
            },
            handler=self._handle_get_few_shot_examples
        ))

    def _handle_get_hook_patterns(
        self,
        hook_type: Optional[str] = None,
        topic: Optional[str] = None
    ) -> str:
        """Get hook patterns from knowledge base."""
        query = "hook patterns examples wellness"
        if hook_type:
            query = f"{hook_type} hook patterns examples"
        if topic:
            query += f" {topic}"

        results = search_knowledge(query, top_k=3, threshold=0.4)

        if not results:
            return "No hook patterns found. Using default patterns."

        patterns = ["Hook patterns and examples:"]
        for r in results:
            patterns.append(r.get("content", "")[:600])

        return "\n\n".join(patterns)

    def _handle_get_platform_rules(self, platform: str) -> str:
        """Get platform-specific rules."""
        results = search_knowledge(
            f"{platform} content rules guidelines best practices",
            top_k=3,
            threshold=0.4
        )

        if not results:
            return f"No specific rules found for {platform}. Using general best practices."

        rules = [f"Rules and guidelines for {platform}:"]
        for r in results:
            rules.append(r.get("content", "")[:600])

        return "\n\n".join(rules)

    def _handle_get_engagement_tactics(self, tactic_type: Optional[str] = None) -> str:
        """Get engagement tactics."""
        query = "engagement tactics psychology"
        if tactic_type:
            query = f"{tactic_type} engagement tactics"

        results = search_knowledge(query, top_k=3, threshold=0.4)

        if not results:
            return "No specific tactics found. Using general engagement principles."

        tactics = ["Engagement tactics:"]
        for r in results:
            tactics.append(r.get("content", "")[:600])

        return "\n\n".join(tactics)

    def _handle_get_cta_templates(
        self,
        funnel_stage: str,
        platform: Optional[str] = None
    ) -> str:
        """Get CTA templates."""
        query = f"call to action CTA {funnel_stage}"
        if platform:
            query += f" {platform}"

        results = search_knowledge(query, top_k=3, threshold=0.4)

        if not results:
            return f"No specific CTAs found for {funnel_stage}. Using general templates."

        ctas = [f"CTA templates for {funnel_stage}:"]
        for r in results:
            ctas.append(r.get("content", "")[:500])

        return "\n\n".join(ctas)

    def _handle_get_few_shot_examples(
        self,
        topic: str,
        platform: Optional[str] = None,
        count: int = 3
    ) -> str:
        """Get few-shot examples."""
        # This would ideally query content_generations for high-rated examples
        # For now, search engagement guide for examples
        query = f"content examples {topic}"
        if platform:
            query += f" {platform}"

        results = search_knowledge(query, top_k=count, threshold=0.4)

        if not results:
            return "No similar examples found. Creating fresh content."

        examples = [f"Similar content examples for {topic}:"]
        for i, r in enumerate(results, 1):
            examples.append(f"\nExample {i}:\n{r.get('content', '')[:400]}...")

        return "\n".join(examples)

    def _extract_response_data(self, response: str) -> tuple[dict, bool, Optional[str]]:
        """Extract content data from response."""
        data = {}

        # Look for JSON blocks
        json_matches = re.findall(r'```json\s*(.*?)\s*```', response, re.DOTALL)

        for json_str in json_matches:
            try:
                parsed = json.loads(json_str)

                # Check for preview
                if "preview" in parsed:
                    preview_data = parsed["preview"]
                    self._current_preview = ContentPreview(
                        hook=preview_data.get("hook", ""),
                        hook_type=preview_data.get("hook_type", ""),
                        open_loops=preview_data.get("open_loops", []),
                        promise=preview_data.get("promise", ""),
                        brief_summary=preview_data.get("brief_summary", "")
                    )
                    data["preview"] = preview_data

                # Check for full content
                if "content" in parsed:
                    content_data = parsed["content"]
                    self._current_content = GeneratedContent(
                        content=content_data.get("full_text", ""),
                        word_count=content_data.get("word_count", 0),
                        hashtags=content_data.get("hashtags", []),
                        preview=self._current_preview,
                        engagement_prediction=content_data.get("engagement_prediction", 0)
                    )
                    data["content"] = content_data
                    return data, True, "review"

            except json.JSONDecodeError:
                continue

        # Check if preview is complete (for two-stage generation)
        if self._current_preview and data.get("preview"):
            return data, False, None  # Need user approval before full generation

        return data, False, None

    def _format_approved_learnings(self, brief: dict) -> str:
        """Retrieve approved learnings to guide generation."""
        topic = brief.get("core_message") or brief.get("pain_point") or brief.get("platform")
        try:
            learnings = get_approved_learnings(
                agent_name=self.agent_name,
                topic=topic,
                limit=5,
            )
        except LearningsError:
            return ""

        if not learnings:
            return ""

        formatted = ["**Approved Learnings (apply when relevant):**"]
        for learning in learnings:
            summary = learning.get("learning_summary") or ""
            content = learning.get("learning_content") or ""
            learning_type = learning.get("learning_type") or "pattern"
            confidence = learning.get("confidence_score")
            confidence_str = f"{float(confidence):.0%}" if confidence is not None else "n/a"
            formatted.append(
                f"- ({learning_type}, confidence {confidence_str}) {summary or content}"
            )
        return "\n".join(formatted)

    def generate_preview(self, brief: dict, verified_facts: list) -> AgentResponse:
        """Generate content preview (hook + open loops + promise).

        Args:
            brief: Content brief from Orchestrator
            verified_facts: Verified facts from Wellness Agent

        Returns:
            AgentResponse with preview
        """
        facts_str = "\n".join(f"- {fact}" for fact in verified_facts[:5])
        learnings_str = self._format_approved_learnings(brief)

        preview_request = f"""Generate a content preview for the following brief:

**Core Message:** {brief.get('core_message', 'Not specified')}
**Target Audience:** {brief.get('target_audience', 'Not specified')}
**Platform:** {brief.get('platform', 'Not specified')}
**Funnel Stage:** {brief.get('funnel_stage', 'Not specified')}
**Content Type:** {brief.get('content_type', 'post')}
**Tone:** {brief.get('tone', 'warm and professional')}
**Pain Point:** {brief.get('pain_point', 'Not specified')}
**Transformation:** {brief.get('transformation', 'Not specified')}

{"**Campaign Details:**" if brief.get('has_campaign') else ""}
{f"- Price: {brief.get('campaign_price')}" if brief.get('campaign_price') else ""}
{f"- Duration: {brief.get('campaign_duration')}" if brief.get('campaign_duration') else ""}
{f"- Center: {brief.get('campaign_center')}" if brief.get('campaign_center') else ""}
{f"- Deadline: {brief.get('campaign_deadline')}" if brief.get('campaign_deadline') else ""}

**Verified Facts to Use:**
{facts_str if facts_str else "No specific facts provided"}

{learnings_str if learnings_str else ""}

Please create a compelling preview with:
1. An attention-grabbing hook appropriate for the funnel stage
2. 2-3 open loops to maintain engagement
3. A clear promise of what the reader will gain

Return in JSON format."""

        return self.process_message_sync(preview_request)

    def generate_full_content(
        self,
        brief: dict,
        preview: ContentPreview,
        verified_facts: list
    ) -> AgentResponse:
        """Generate full content based on approved preview.

        Args:
            brief: Content brief
            preview: Approved content preview
            verified_facts: Verified facts to include

        Returns:
            AgentResponse with full content
        """
        facts_str = "\n".join(f"- {fact}" for fact in verified_facts[:5])
        learnings_str = self._format_approved_learnings(brief)

        content_request = f"""Generate the full content based on this approved preview:

**Hook:** {preview.hook}
**Hook Type:** {preview.hook_type}
**Open Loops:** {', '.join(preview.open_loops)}
**Promise:** {preview.promise}

**Brief:**
- Core Message: {brief.get('core_message')}
- Audience: {brief.get('target_audience')}
- Platform: {brief.get('platform')}
- Funnel Stage: {brief.get('funnel_stage')}
- Tone: {brief.get('tone', 'warm and professional')}

{"**Campaign Details:**" if brief.get('has_campaign') else ""}
{f"- Price: {brief.get('campaign_price')}" if brief.get('campaign_price') else ""}
{f"- Duration: {brief.get('campaign_duration')}" if brief.get('campaign_duration') else ""}
{f"- Center: {brief.get('campaign_center')}" if brief.get('campaign_center') else ""}
{f"- Deadline: {brief.get('campaign_deadline')}" if brief.get('campaign_deadline') else ""}

**Verified Facts:**
{facts_str}

{learnings_str if learnings_str else ""}

Create the complete content:
1. Start with the approved hook
2. Resolve the open loops throughout
3. Deliver on the promise
4. End with an appropriate CTA for the funnel stage
5. Include hashtags if for Instagram

Return in JSON format with full_text, word_count, hashtags, and engagement_prediction."""

        return self.process_message_sync(content_request)

    def get_current_preview(self) -> Optional[ContentPreview]:
        """Get the current content preview."""
        return self._current_preview

    def get_current_content(self) -> Optional[GeneratedContent]:
        """Get the current generated content."""
        return self._current_content

    def regenerate_hook(self, brief: dict, hook_type: Optional[str] = None) -> AgentResponse:
        """Regenerate just the hook with a different approach.

        Args:
            brief: Content brief
            hook_type: Specific hook type to try (optional)

        Returns:
            AgentResponse with new hook options
        """
        hook_request = f"""Generate 3 alternative hooks for this content:

**Core Message:** {brief.get('core_message')}
**Audience:** {brief.get('target_audience')}
**Platform:** {brief.get('platform')}
**Funnel Stage:** {brief.get('funnel_stage')}

{"Use this hook type: " + hook_type if hook_type else "Try different hook types"}

Previous hook (to avoid): {self._current_preview.hook if self._current_preview else "None"}

Provide 3 different hooks with their types, ranked by predicted engagement."""

        return self.process_message_sync(hook_request)
