"""TheLifeCo Content Assistant Agents.

This module contains the agentic architecture for content generation.

NEW ARCHITECTURE (EPA-GONCA-ALP):
- EPA Agent: Main orchestrator that interacts with users, collects briefs,
             coordinates sub-agents, and reviews all output
- GONCA Agent: Wellness expert sub-agent for TheLifeCo knowledge
- ALP Agent: Storytelling expert sub-agent for content creation
- Review Sub-Agent: Feedback analyzer for routing revisions

LEGACY ARCHITECTURE (deprecated, kept for backward compatibility):
- Orchestrator Agent: Conversational briefing and coordination
- Wellness Agent: Fact verification against knowledge base
- Storytelling Agent: Content creation with engagement optimization
- Review Agent: Feedback collection and learning extraction
"""

# Base classes
from content_assistant.agents.base_agent import BaseAgent, AgentResponse, AgentTool
from content_assistant.agents.subagent_base import SubAgentBase, SubAgentTool, SubAgentError

# NEW: EPA Architecture types
from content_assistant.agents.types import (
    ContentBrief,
    EPAState,
    EPAStage,
    FunnelStage,
    ComplianceLevel,
    Platform,
    ContentType,
    WellnessRequest,
    WellnessResponse,
    StorytellingRequest,
    StorytellingResponse,
    FeedbackRequest,
    FeedbackAnalysis,
)

# NEW: EPA Architecture agents
from content_assistant.agents.epa_agent import EPAAgent
from content_assistant.agents.gonca_agent import GONCAAgent
from content_assistant.agents.alp_agent import ALPAgent
from content_assistant.agents.review_subagent import ReviewSubAgent

# LEGACY: Old architecture (deprecated)
from content_assistant.agents.orchestrator import OrchestratorAgent
from content_assistant.agents.orchestrator import ContentBrief as LegacyContentBrief
from content_assistant.agents.wellness_agent import WellnessAgent, VerificationResult
from content_assistant.agents.storytelling_agent import StorytellingAgent, ContentPreview, GeneratedContent
from content_assistant.agents.review_agent import ReviewAgent, UserFeedback, ExtractedLearning
from content_assistant.agents.coordinator import AgentCoordinator, AgentStage, CoordinatorState

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentResponse",
    "AgentTool",
    "SubAgentBase",
    "SubAgentTool",
    "SubAgentError",

    # NEW: EPA Architecture types
    "ContentBrief",
    "EPAState",
    "EPAStage",
    "FunnelStage",
    "ComplianceLevel",
    "Platform",
    "ContentType",
    "WellnessRequest",
    "WellnessResponse",
    "StorytellingRequest",
    "StorytellingResponse",
    "FeedbackRequest",
    "FeedbackAnalysis",

    # NEW: EPA Architecture agents
    "EPAAgent",
    "GONCAAgent",
    "ALPAgent",
    "ReviewSubAgent",

    # LEGACY: Old architecture (deprecated)
    "OrchestratorAgent",
    "LegacyContentBrief",
    "WellnessAgent",
    "VerificationResult",
    "StorytellingAgent",
    "ContentPreview",
    "GeneratedContent",
    "ReviewAgent",
    "UserFeedback",
    "ExtractedLearning",
    "AgentCoordinator",
    "AgentStage",
    "CoordinatorState",
]
