"""Review & Learning Agent for TheLifeCo Content Assistant.

The Review Agent is responsible for:
- Collecting user feedback on generated content
- Extracting learnings from feedback
- Managing admin review queue
- Applying approved learnings to future generations
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

from content_assistant.agents.base_agent import BaseAgent, AgentTool, AgentResponse


class FeedbackCategory(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_WORK = "needs_work"
    POOR = "poor"


class LearningType(str, Enum):
    PATTERN = "pattern"
    PREFERENCE = "preference"
    CORRECTION = "correction"
    FEEDBACK = "feedback"
    STYLE = "style"


@dataclass
class UserFeedback:
    """User feedback on generated content."""
    generation_id: str
    rating: int  # 1-5
    feedback_text: Optional[str] = None
    what_worked: list = field(default_factory=list)
    what_needs_work: list = field(default_factory=list)
    hook_feedback: Optional[FeedbackCategory] = None
    facts_feedback: Optional[str] = None
    tone_feedback: Optional[FeedbackCategory] = None
    cta_feedback: Optional[FeedbackCategory] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "generation_id": self.generation_id,
            "rating": self.rating,
            "feedback_text": self.feedback_text,
            "what_worked": self.what_worked,
            "what_needs_work": self.what_needs_work,
            "hook_feedback": self.hook_feedback.value if self.hook_feedback else None,
            "facts_feedback": self.facts_feedback,
            "tone_feedback": self.tone_feedback.value if self.tone_feedback else None,
            "cta_feedback": self.cta_feedback.value if self.cta_feedback else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ExtractedLearning:
    """Learning extracted from feedback."""
    learning_type: LearningType
    content: str
    summary: str
    confidence: float  # 0-1
    source_feedback_id: Optional[str] = None
    tags: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "learning_type": self.learning_type.value,
            "content": self.content,
            "summary": self.summary,
            "confidence": self.confidence,
            "source_feedback_id": self.source_feedback_id,
            "tags": self.tags,
        }


REVIEW_SYSTEM_PROMPT = """You are the Review & Learning Agent for TheLifeCo Content Assistant. Your role is to collect feedback, extract learnings, and improve the system over time.

## Your Responsibilities
1. **Collect Feedback**: Gather structured and open-ended feedback from users
2. **Extract Learnings**: Identify actionable patterns from feedback
3. **Queue for Review**: Flag important learnings for admin approval
4. **Apply Learnings**: Use approved learnings in future generations
5. **Analyze Patterns**: Identify trends across multiple feedback instances

## Feedback Collection
Ask about:
- Overall satisfaction (1-5 stars)
- What worked well (hook, facts, tone, CTA)
- What needs improvement
- Open-ended feedback for context
- Would they use this content?

## Learning Extraction
From feedback, extract:
- **Pattern Learning**: "Users prefer shorter hooks on Instagram"
- **Preference Learning**: "User X prefers formal tone"
- **Correction Learning**: "Don't say X, say Y instead"
- **Style Learning**: "Wellness content works better with statistics"

## Learning Format
```json
{
  "learnings": [
    {
      "type": "pattern|preference|correction|style",
      "content": "Detailed learning description",
      "summary": "Short summary for display",
      "confidence": 0.8,
      "tags": ["hook", "instagram", "engagement"]
    }
  ],
  "admin_review_needed": true,
  "review_reason": "Significant pattern detected across 5+ feedback instances"
}
```

## Admin Review Triggers
Flag for admin when:
- Learning contradicts existing approved learning
- Confidence score below 0.6
- Learning affects core brand guidelines
- New pattern detected across multiple users
- Negative feedback pattern identified

## Feedback Summary Format
After collecting feedback, provide:
```json
{
  "feedback_summary": {
    "rating": 4,
    "strengths": ["engaging hook", "accurate facts"],
    "improvements": ["CTA could be stronger"],
    "learnings_extracted": 2,
    "admin_review_needed": false
  }
}
```"""


class ReviewAgent(BaseAgent):
    """Review & Learning Agent.

    Collects feedback, extracts learnings, and manages
    the admin review queue for continuous improvement.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.5,
    ):
        """Initialize the Review Agent."""
        super().__init__(
            agent_name="review",
            system_prompt=REVIEW_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            knowledge_sources=[],  # Review agent doesn't need knowledge base
        )

        self._current_feedback: Optional[UserFeedback] = None
        self._extracted_learnings: list[ExtractedLearning] = []

    def register_tools(self) -> None:
        """Register review-specific tools."""
        # Tool: Store feedback
        self.register_tool(AgentTool(
            name="store_feedback",
            description="Store user feedback in the database.",
            input_schema={
                "type": "object",
                "properties": {
                    "generation_id": {
                        "type": "string",
                        "description": "ID of the content generation"
                    },
                    "rating": {
                        "type": "integer",
                        "description": "Rating from 1-5",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "feedback_text": {
                        "type": "string",
                        "description": "Open-ended feedback"
                    },
                    "what_worked": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of things that worked well"
                    },
                    "what_needs_work": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of things that need improvement"
                    }
                },
                "required": ["generation_id", "rating"]
            },
            handler=self._handle_store_feedback
        ))

        # Tool: Extract learning
        self.register_tool(AgentTool(
            name="extract_learning",
            description="Extract and store a learning from feedback.",
            input_schema={
                "type": "object",
                "properties": {
                    "learning_type": {
                        "type": "string",
                        "description": "Type of learning",
                        "enum": ["pattern", "preference", "correction", "style"]
                    },
                    "content": {
                        "type": "string",
                        "description": "Detailed learning content"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Short summary"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score 0-1",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Categorization tags"
                    }
                },
                "required": ["learning_type", "content", "summary", "confidence"]
            },
            handler=self._handle_extract_learning
        ))

        # Tool: Queue for admin review
        self.register_tool(AgentTool(
            name="queue_for_review",
            description="Queue a learning or feedback for admin review.",
            input_schema={
                "type": "object",
                "properties": {
                    "item_type": {
                        "type": "string",
                        "description": "Type of item to queue",
                        "enum": ["learning", "feedback", "pattern"]
                    },
                    "item_id": {
                        "type": "string",
                        "description": "ID of the item"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for admin review"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level",
                        "enum": ["low", "medium", "high"]
                    }
                },
                "required": ["item_type", "reason"]
            },
            handler=self._handle_queue_for_review
        ))

        # Tool: Get approved learnings
        self.register_tool(AgentTool(
            name="get_approved_learnings",
            description="Get approved learnings relevant to a topic.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to find learnings for"
                    },
                    "learning_type": {
                        "type": "string",
                        "description": "Filter by learning type",
                        "enum": ["pattern", "preference", "correction", "style"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max learnings to return",
                        "default": 5
                    }
                },
                "required": []
            },
            handler=self._handle_get_approved_learnings
        ))

    def _handle_store_feedback(
        self,
        generation_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        what_worked: Optional[list] = None,
        what_needs_work: Optional[list] = None
    ) -> str:
        """Store feedback (placeholder - would write to database)."""
        self._current_feedback = UserFeedback(
            generation_id=generation_id,
            rating=rating,
            feedback_text=feedback_text,
            what_worked=what_worked or [],
            what_needs_work=what_needs_work or []
        )

        # In production, this would write to Supabase
        return f"Feedback stored successfully. Rating: {rating}/5, Items that worked: {len(what_worked or [])}, Items to improve: {len(what_needs_work or [])}"

    def _handle_extract_learning(
        self,
        learning_type: str,
        content: str,
        summary: str,
        confidence: float,
        tags: Optional[list] = None
    ) -> str:
        """Extract and store a learning."""
        learning = ExtractedLearning(
            learning_type=LearningType(learning_type),
            content=content,
            summary=summary,
            confidence=confidence,
            tags=tags or []
        )

        self._extracted_learnings.append(learning)

        # Determine if admin review needed
        needs_review = confidence < 0.7 or learning_type == "correction"
        review_status = "queued for admin review" if needs_review else "stored"

        return f"Learning extracted and {review_status}. Type: {learning_type}, Confidence: {confidence:.0%}"

    def _handle_queue_for_review(
        self,
        item_type: str,
        reason: str,
        item_id: Optional[str] = None,
        priority: str = "medium"
    ) -> str:
        """Queue item for admin review."""
        # In production, this would write to admin review queue
        return f"Queued for admin review. Type: {item_type}, Priority: {priority}, Reason: {reason}"

    def _handle_get_approved_learnings(
        self,
        topic: Optional[str] = None,
        learning_type: Optional[str] = None,
        limit: int = 5
    ) -> str:
        """Get approved learnings (placeholder)."""
        # In production, this would query agent_learnings table
        return "No approved learnings found matching criteria. (Database query would return results in production)"

    def _extract_response_data(self, response: str) -> tuple[dict, bool, Optional[str]]:
        """Extract feedback/learning data from response."""
        data = {}

        # Look for JSON blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group(1))

                if "feedback_summary" in parsed:
                    data["feedback_summary"] = parsed["feedback_summary"]
                    return data, True, None  # Feedback collection complete

                if "learnings" in parsed:
                    data["learnings"] = parsed["learnings"]
                    data["admin_review_needed"] = parsed.get("admin_review_needed", False)

            except json.JSONDecodeError:
                pass

        return data, False, None

    def collect_feedback(
        self,
        generation_id: str,
        content: str,
        brief: dict
    ) -> AgentResponse:
        """Start feedback collection conversation.

        Args:
            generation_id: ID of the content generation
            content: The generated content
            brief: Original content brief

        Returns:
            AgentResponse with feedback questions
        """
        feedback_request = f"""I'd like to collect your feedback on this content.

**Generated Content:**
---
{content[:1000]}{"..." if len(content) > 1000 else ""}
---

**Original Brief:**
- Core Message: {brief.get('core_message', 'N/A')}
- Platform: {brief.get('platform', 'N/A')}
- Audience: {brief.get('target_audience', 'N/A')}

Please help me understand:
1. How would you rate this content overall? (1-5 stars)
2. What worked well? (hook, facts, tone, CTA, overall message)
3. What could be improved?
4. Any specific feedback or suggestions?
5. Would you use this content as-is, with minor edits, or does it need major changes?

Generation ID: {generation_id}"""

        return self.process_message_sync(feedback_request)

    def process_feedback_response(self, user_response: str) -> AgentResponse:
        """Process user's feedback response.

        Args:
            user_response: User's feedback

        Returns:
            AgentResponse with extracted learnings
        """
        return self.process_message_sync(user_response)

    def analyze_feedback_patterns(self, feedback_list: list[dict]) -> AgentResponse:
        """Analyze multiple feedback instances for patterns.

        Args:
            feedback_list: List of feedback dictionaries

        Returns:
            AgentResponse with identified patterns
        """
        feedback_summary = json.dumps(feedback_list, indent=2)

        analysis_request = f"""Analyze these feedback instances for patterns:

{feedback_summary}

Identify:
1. Common positive patterns (what consistently works)
2. Common improvement areas (recurring issues)
3. Platform-specific patterns
4. Audience-specific preferences
5. Any learnings that should be flagged for admin review

Extract actionable learnings that can improve future content generation."""

        return self.process_message_sync(analysis_request)

    def get_current_feedback(self) -> Optional[UserFeedback]:
        """Get the current feedback being collected."""
        return self._current_feedback

    def get_extracted_learnings(self) -> list[ExtractedLearning]:
        """Get all learnings extracted in this session."""
        return self._extracted_learnings

    def clear_session(self) -> None:
        """Clear session data."""
        self._current_feedback = None
        self._extracted_learnings = []
        self.clear_conversation()
