"""Type definitions for EPA-GONCA-ALP agent architecture.

This module defines the data structures used for communication between
EPA (main orchestrator) and its sub-agents (GONCA, ALP, Review).

Architecture Overview:
- EPA: Main orchestrator agent that interacts with users, collects briefs,
       coordinates sub-agents, and reviews all output before delivery.
- GONCA: Wellness sub-agent that provides TheLifeCo knowledge and verified facts.
- ALP: Storytelling sub-agent that creates content with full context from EPA.
- Review: Feedback collection sub-agent that analyzes user feedback.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any


class FunnelStage(str, Enum):
    """Marketing funnel stages."""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    LOYALTY = "loyalty"


class ComplianceLevel(str, Enum):
    """Content compliance level."""
    HIGH = "high"  # Strict medical/health claims, needs careful review
    LOW = "low"    # General wellness content, more creative freedom


class Platform(str, Enum):
    """Content platforms."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    EMAIL = "email"
    BLOG = "blog"
    WEBSITE = "website"


class ContentType(str, Enum):
    """Types of content."""
    POST = "post"
    STORY = "story"
    CAROUSEL = "carousel"
    REEL = "reel"
    ARTICLE = "article"
    NEWSLETTER = "newsletter"
    LANDING_PAGE = "landing_page"


# =============================================================================
# CONTENT BRIEF - The 13 Required Fields
# =============================================================================

@dataclass
class ContentBrief:
    """Structured content brief with all 13 required fields.

    EPA must collect ALL of these fields before initiating content generation.
    Pain Area is the MOST CRUCIAL field - it drives the entire content strategy.

    Required Fields:
    1. target_audience: Who is this content for?
    2. pain_area: What problem/pain point are we addressing? (CRUCIAL)
    3. compliance_level: High (medical claims) or Low (general wellness)
    4. funnel_stage: awareness/consideration/conversion/loyalty
    5. value_proposition: What unique value are we offering?
    6. desired_action: What should the reader do after consuming content?
    7. specific_programs: Which TheLifeCo programs to feature
    8. specific_centers: Which TheLifeCo centers to feature
    9. tone: Voice and style of the content
    10. key_messages: Core points to communicate (list)
    11. constraints: Things to avoid or limitations
    12. platform: Where will this content be published?
    13. price_points: Pricing information to include (if any)
    """

    # REQUIRED FIELDS (13 total)
    target_audience: Optional[str] = None
    pain_area: Optional[str] = None  # CRUCIAL - drives content strategy
    compliance_level: Optional[ComplianceLevel] = None
    funnel_stage: Optional[FunnelStage] = None
    value_proposition: Optional[str] = None
    desired_action: Optional[str] = None
    specific_programs: list[str] = field(default_factory=list)
    specific_centers: list[str] = field(default_factory=list)
    tone: Optional[str] = None
    key_messages: list[str] = field(default_factory=list)
    constraints: Optional[str] = None
    platform: Optional[Platform] = None
    price_points: Optional[str] = None

    # OPTIONAL CONTEXT FIELDS
    core_message: Optional[str] = None
    transformation: Optional[str] = None
    content_type: Optional[ContentType] = None
    evidence_or_story: Optional[str] = None
    cta: Optional[str] = None  # Specific call-to-action text

    # CAMPAIGN FIELDS (required for conversion funnel stage)
    has_campaign: bool = False
    campaign_price: Optional[str] = None
    campaign_duration: Optional[str] = None
    campaign_center: Optional[str] = None
    campaign_deadline: Optional[str] = None

    def get_missing_fields(self) -> list[str]:
        """Get list of required fields that are still missing."""
        missing = []

        # Check all 13 required fields
        if not self.target_audience:
            missing.append("target_audience")
        if not self.pain_area:
            missing.append("pain_area (CRUCIAL)")
        if not self.compliance_level:
            missing.append("compliance_level")
        if not self.funnel_stage:
            missing.append("funnel_stage")
        if not self.value_proposition:
            missing.append("value_proposition")
        if not self.desired_action:
            missing.append("desired_action")
        if not self.specific_programs:
            missing.append("specific_programs")
        if not self.specific_centers:
            missing.append("specific_centers")
        if not self.tone:
            missing.append("tone")
        if not self.key_messages:
            missing.append("key_messages")
        if not self.constraints:
            missing.append("constraints")
        if not self.platform:
            missing.append("platform")
        if not self.price_points:
            missing.append("price_points")

        # For conversion stage, check campaign fields
        if self.funnel_stage == FunnelStage.CONVERSION:
            if not self.has_campaign:
                missing.append("has_campaign")
            if self.has_campaign:
                if not self.campaign_price:
                    missing.append("campaign_price")
                if not self.campaign_duration:
                    missing.append("campaign_duration")
                if not self.campaign_center:
                    missing.append("campaign_center")
                if not self.campaign_deadline:
                    missing.append("campaign_deadline")

        return missing

    def is_complete(self) -> bool:
        """Check if all required fields are present."""
        return len(self.get_missing_fields()) == 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            # Required fields
            "target_audience": self.target_audience,
            "pain_area": self.pain_area,
            "compliance_level": self.compliance_level.value if self.compliance_level else None,
            "funnel_stage": self.funnel_stage.value if self.funnel_stage else None,
            "value_proposition": self.value_proposition,
            "desired_action": self.desired_action,
            "specific_programs": self.specific_programs,
            "specific_centers": self.specific_centers,
            "tone": self.tone,
            "key_messages": self.key_messages,
            "constraints": self.constraints,
            "platform": self.platform.value if self.platform else None,
            "price_points": self.price_points,
            # Optional fields
            "core_message": self.core_message,
            "transformation": self.transformation,
            "content_type": self.content_type.value if self.content_type else None,
            "evidence_or_story": self.evidence_or_story,
            "cta": self.cta,
            # Campaign fields
            "has_campaign": self.has_campaign,
            "campaign_price": self.campaign_price,
            "campaign_duration": self.campaign_duration,
            "campaign_center": self.campaign_center,
            "campaign_deadline": self.campaign_deadline,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentBrief":
        """Create from dictionary."""
        # Handle enum conversions
        compliance = data.get("compliance_level")
        if compliance and isinstance(compliance, str):
            compliance = ComplianceLevel(compliance)

        funnel = data.get("funnel_stage")
        if funnel and isinstance(funnel, str):
            funnel = FunnelStage(funnel)

        platform = data.get("platform")
        if platform and isinstance(platform, str):
            platform = Platform(platform)

        content_type = data.get("content_type")
        if content_type and isinstance(content_type, str):
            content_type = ContentType(content_type)

        return cls(
            target_audience=data.get("target_audience"),
            pain_area=data.get("pain_area"),
            compliance_level=compliance,
            funnel_stage=funnel,
            value_proposition=data.get("value_proposition"),
            desired_action=data.get("desired_action"),
            specific_programs=data.get("specific_programs", []),
            specific_centers=data.get("specific_centers", []),
            tone=data.get("tone"),
            key_messages=data.get("key_messages", []),
            constraints=data.get("constraints"),
            platform=platform,
            price_points=data.get("price_points"),
            core_message=data.get("core_message"),
            transformation=data.get("transformation"),
            content_type=content_type,
            evidence_or_story=data.get("evidence_or_story"),
            cta=data.get("cta"),
            has_campaign=data.get("has_campaign", False),
            campaign_price=data.get("campaign_price"),
            campaign_duration=data.get("campaign_duration"),
            campaign_center=data.get("campaign_center"),
            campaign_deadline=data.get("campaign_deadline"),
        )


# =============================================================================
# SUB-AGENT REQUEST/RESPONSE TYPES
# =============================================================================

@dataclass
class WellnessRequest:
    """Request to GONCA (Wellness sub-agent).

    EPA sends this when it needs TheLifeCo knowledge, program details,
    center information, or verified wellness facts.
    """
    query: str  # What information EPA needs
    brief: ContentBrief  # Full brief context
    context: str  # Additional context from conversation
    specific_topics: list[str] = field(default_factory=list)  # Specific areas to research


@dataclass
class WellnessResponse:
    """Response from GONCA (Wellness sub-agent).

    Contains verified TheLifeCo information that ALP will use
    for content creation.
    """
    verified_facts: list[str]  # List of verified facts to include
    program_details: dict[str, Any]  # Details about specific programs
    center_info: dict[str, Any]  # Details about specific centers
    wellness_guidance: str  # Compliance and wellness writing guidance
    sources_used: list[str]  # Knowledge base sources referenced
    confidence_level: float  # 0-1, how confident GONCA is in the info
    warnings: list[str] = field(default_factory=list)  # Any compliance warnings


@dataclass
class StorytellingRequest:
    """Request to ALP (Storytelling sub-agent).

    EPA sends this with FULL CONTEXT so ALP can create the best content.
    ALP receives everything it needs - brief, wellness facts, style guidance.
    """
    brief: ContentBrief  # Complete content brief with all 13 fields
    wellness_facts: WellnessResponse  # Verified facts from GONCA
    user_voice: str  # User's communication style/preferences
    style_guidance: str  # Brand voice and storytelling guidelines
    conversation_context: str  # Relevant parts of user conversation
    previous_feedback: Optional[str] = None  # Feedback from previous iteration
    iteration_number: int = 1  # Which iteration of content this is


@dataclass
class StorytellingResponse:
    """Response from ALP (Storytelling sub-agent).

    Contains the generated content for EPA to review before
    presenting to the user.
    """
    hook: str  # Opening hook/attention grabber
    hook_type: str  # Type of hook used (question, story, statistic, etc.)
    content: str  # Full content body
    call_to_action: str  # CTA text
    hashtags: list[str]  # Relevant hashtags (if applicable)
    open_loops: list[str]  # Curiosity elements used
    storytelling_framework: str  # Framework used (AIDA, PAS, etc.)
    word_count: int
    character_count: int
    confidence_notes: str  # ALP's notes on the content
    alternative_hooks: list[str] = field(default_factory=list)  # Other hook options


@dataclass
class FeedbackRequest:
    """Request to Review sub-agent for feedback analysis."""
    user_feedback: str  # Raw feedback from user
    generated_content: StorytellingResponse  # The content being reviewed
    brief: ContentBrief  # Original brief for context
    wellness_facts: WellnessResponse  # Facts that were used


@dataclass
class FeedbackAnalysis:
    """Response from Review sub-agent analyzing user feedback.

    EPA uses this to decide whether to call GONCA (wellness issues)
    or ALP (storytelling issues) for revisions.
    """
    feedback_type: str  # "wellness", "storytelling", "both", or "approved"
    sentiment: str  # "positive", "negative", "mixed"
    wellness_issues: list[str]  # Issues related to facts/accuracy
    storytelling_issues: list[str]  # Issues related to style/engagement
    specific_requests: list[str]  # Specific changes requested
    suggested_action: str  # "revise_wellness", "revise_storytelling", "revise_both", "finalize"
    summary: str  # Brief summary of feedback


# =============================================================================
# EPA STATE MANAGEMENT
# =============================================================================

class EPAStage(str, Enum):
    """Stages of EPA workflow."""
    BRIEFING = "briefing"  # Collecting the 13 required fields
    CONSULTING_GONCA = "consulting_gonca"  # Getting wellness facts
    CONSULTING_ALP = "consulting_alp"  # Getting content draft
    REVIEWING = "reviewing"  # EPA reviewing sub-agent output
    PRESENTING = "presenting"  # Presenting content to user
    COLLECTING_FEEDBACK = "collecting_feedback"  # Getting user feedback
    REVISING = "revising"  # Processing revisions
    COMPLETE = "complete"  # Workflow complete


@dataclass
class EPAState:
    """State management for EPA agent.

    Tracks the current stage, brief, and sub-agent responses.
    """
    stage: EPAStage = EPAStage.BRIEFING
    brief: ContentBrief = field(default_factory=ContentBrief)

    # Sub-agent responses
    wellness_response: Optional[WellnessResponse] = None
    storytelling_response: Optional[StorytellingResponse] = None
    feedback_analysis: Optional[FeedbackAnalysis] = None

    # Iteration tracking
    iteration_count: int = 0
    max_iterations: int = 3

    # Conversation tracking
    messages_in_briefing: int = 0
    total_messages: int = 0

    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    brief_completed_at: Optional[datetime] = None
    content_generated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        return {
            "stage": self.stage.value,
            "brief": self.brief.to_dict(),
            "wellness_response": self._serialize_wellness_response(),
            "storytelling_response": self._serialize_storytelling_response(),
            "feedback_analysis": self._serialize_feedback_analysis(),
            "iteration_count": self.iteration_count,
            "max_iterations": self.max_iterations,
            "messages_in_briefing": self.messages_in_briefing,
            "total_messages": self.total_messages,
            "started_at": self.started_at.isoformat(),
            "brief_completed_at": self.brief_completed_at.isoformat() if self.brief_completed_at else None,
            "content_generated_at": self.content_generated_at.isoformat() if self.content_generated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def _serialize_wellness_response(self) -> Optional[dict]:
        if not self.wellness_response:
            return None
        return {
            "verified_facts": self.wellness_response.verified_facts,
            "program_details": self.wellness_response.program_details,
            "center_info": self.wellness_response.center_info,
            "wellness_guidance": self.wellness_response.wellness_guidance,
            "sources_used": self.wellness_response.sources_used,
            "confidence_level": self.wellness_response.confidence_level,
            "warnings": self.wellness_response.warnings,
        }

    def _serialize_storytelling_response(self) -> Optional[dict]:
        if not self.storytelling_response:
            return None
        return {
            "hook": self.storytelling_response.hook,
            "hook_type": self.storytelling_response.hook_type,
            "content": self.storytelling_response.content,
            "call_to_action": self.storytelling_response.call_to_action,
            "hashtags": self.storytelling_response.hashtags,
            "open_loops": self.storytelling_response.open_loops,
            "storytelling_framework": self.storytelling_response.storytelling_framework,
            "word_count": self.storytelling_response.word_count,
            "character_count": self.storytelling_response.character_count,
            "confidence_notes": self.storytelling_response.confidence_notes,
            "alternative_hooks": self.storytelling_response.alternative_hooks,
        }

    def _serialize_feedback_analysis(self) -> Optional[dict]:
        if not self.feedback_analysis:
            return None
        return {
            "feedback_type": self.feedback_analysis.feedback_type,
            "sentiment": self.feedback_analysis.sentiment,
            "wellness_issues": self.feedback_analysis.wellness_issues,
            "storytelling_issues": self.feedback_analysis.storytelling_issues,
            "specific_requests": self.feedback_analysis.specific_requests,
            "suggested_action": self.feedback_analysis.suggested_action,
            "summary": self.feedback_analysis.summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EPAState":
        """Create from dictionary."""
        state = cls()
        state.stage = EPAStage(data.get("stage", "briefing"))
        state.brief = ContentBrief.from_dict(data.get("brief", {}))
        state.iteration_count = data.get("iteration_count", 0)
        state.max_iterations = data.get("max_iterations", 3)
        state.messages_in_briefing = data.get("messages_in_briefing", 0)
        state.total_messages = data.get("total_messages", 0)

        # Timestamps
        if data.get("started_at"):
            state.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("brief_completed_at"):
            state.brief_completed_at = datetime.fromisoformat(data["brief_completed_at"])
        if data.get("content_generated_at"):
            state.content_generated_at = datetime.fromisoformat(data["content_generated_at"])
        if data.get("completed_at"):
            state.completed_at = datetime.fromisoformat(data["completed_at"])

        # Sub-agent responses would need to be deserialized separately
        # as they contain complex nested structures

        return state
