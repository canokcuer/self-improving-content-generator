"""Agent Coordinator for TheLifeCo Content Assistant.

The Coordinator manages the sequential execution of agents:
1. Orchestrator → Conversational briefing
2. Wellness → Fact verification
3. Storytelling → Content creation
4. Review → Feedback collection

It handles handoffs between agents and maintains state across the flow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable
import json

from content_assistant.agents.orchestrator import OrchestratorAgent, ContentBrief
from content_assistant.agents.wellness_agent import WellnessAgent, VerificationResult
from content_assistant.agents.storytelling_agent import StorytellingAgent, ContentPreview, GeneratedContent
from content_assistant.agents.review_agent import ReviewAgent, UserFeedback


class AgentStage(str, Enum):
    """Current stage in the agent pipeline."""
    ORCHESTRATOR = "orchestrator"
    WELLNESS = "wellness"
    STORYTELLING_PREVIEW = "storytelling_preview"
    STORYTELLING_CONTENT = "storytelling_content"
    REVIEW = "review"
    COMPLETE = "complete"


@dataclass
class AgentHandoff:
    """Data passed between agents."""
    from_agent: str
    to_agent: str
    data: dict
    timestamp: datetime = field(default_factory=datetime.now)
    user_approved: bool = True


@dataclass
class CoordinatorState:
    """Current state of the coordinator."""
    stage: AgentStage = AgentStage.ORCHESTRATOR
    brief: Optional[ContentBrief] = None
    verification: Optional[VerificationResult] = None
    preview: Optional[ContentPreview] = None
    content: Optional[GeneratedContent] = None
    feedback: Optional[UserFeedback] = None
    handoffs: list = field(default_factory=list)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    generation_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert state to dictionary for storage."""
        return {
            "stage": self.stage.value,
            "brief": self.brief.to_dict() if self.brief else None,
            "verification": self.verification.to_dict() if self.verification else None,
            "preview": {
                "hook": self.preview.hook,
                "hook_type": self.preview.hook_type,
                "open_loops": self.preview.open_loops,
                "promise": self.preview.promise,
            } if self.preview else None,
            "content": self.content.to_dict() if self.content else None,
            "feedback": self.feedback.to_dict() if self.feedback else None,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "generation_id": self.generation_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CoordinatorState":
        """Create state from dictionary."""
        state = cls()
        state.stage = AgentStage(data.get("stage", "orchestrator"))
        if data.get("brief"):
            state.brief = ContentBrief.from_dict(data["brief"])
        state.conversation_id = data.get("conversation_id")
        state.user_id = data.get("user_id")
        state.generation_id = data.get("generation_id")
        return state


class AgentCoordinator:
    """Coordinates the sequential execution of agents.

    Manages the flow:
    Orchestrator → Wellness → Storytelling (Preview) → Storytelling (Content) → Review

    Handles:
    - Agent initialization
    - Message routing
    - Handoffs between agents
    - State management
    - User intervention points
    """

    def __init__(
        self,
        model: Optional[str] = None,
        on_stage_change: Optional[Callable[[AgentStage], None]] = None,
    ):
        """Initialize the coordinator.

        Args:
            model: Claude model to use (defaults to config)
            on_stage_change: Callback when stage changes
        """
        self.model = model
        self.on_stage_change = on_stage_change

        # Initialize agents
        self.orchestrator = OrchestratorAgent(model=model)
        self.wellness = WellnessAgent(model=model)
        self.storytelling = StorytellingAgent(model=model)
        self.review = ReviewAgent(model=model)

        # State
        self.state = CoordinatorState()

    def reset(self) -> None:
        """Reset the coordinator for a new content generation."""
        self.orchestrator.reset_brief()
        self.orchestrator.clear_conversation()
        self.wellness.clear_conversation()
        self.storytelling.clear_conversation()
        self.review.clear_session()
        self.state = CoordinatorState()

    def set_user_context(self, user_id: str, conversation_id: Optional[str] = None) -> None:
        """Set user context for the session."""
        self.state.user_id = user_id
        self.state.conversation_id = conversation_id

    def get_current_stage(self) -> AgentStage:
        """Get the current stage in the pipeline."""
        return self.state.stage

    def get_stage_description(self) -> str:
        """Get human-readable description of current stage."""
        descriptions = {
            AgentStage.ORCHESTRATOR: "Understanding your content needs",
            AgentStage.WELLNESS: "Verifying facts and gathering information",
            AgentStage.STORYTELLING_PREVIEW: "Creating content preview",
            AgentStage.STORYTELLING_CONTENT: "Generating full content",
            AgentStage.REVIEW: "Collecting your feedback",
            AgentStage.COMPLETE: "Content generation complete",
        }
        return descriptions.get(self.state.stage, "Processing")

    def _change_stage(self, new_stage: AgentStage) -> None:
        """Change to a new stage and notify callback."""
        self.state.stage = new_stage
        if self.on_stage_change:
            self.on_stage_change(new_stage)

    def process_message(self, message: str) -> dict:
        """Process a user message based on current stage.

        Routes the message to the appropriate agent and handles transitions.

        Args:
            message: User's message

        Returns:
            dict with:
            - response: Agent's response text
            - stage: Current stage
            - stage_complete: Whether current stage is complete
            - next_action: What happens next
            - data: Any relevant data (brief, preview, content, etc.)
        """
        stage = self.state.stage

        if stage == AgentStage.ORCHESTRATOR:
            return self._process_orchestrator(message)
        elif stage == AgentStage.WELLNESS:
            return self._process_wellness(message)
        elif stage == AgentStage.STORYTELLING_PREVIEW:
            return self._process_storytelling_preview(message)
        elif stage == AgentStage.STORYTELLING_CONTENT:
            return self._process_storytelling_content(message)
        elif stage == AgentStage.REVIEW:
            return self._process_review(message)
        else:
            return {
                "response": "Content generation is complete. Start a new conversation to create more content.",
                "stage": stage.value,
                "stage_complete": True,
                "next_action": "start_new",
                "data": {}
            }

    def _process_orchestrator(self, message: str) -> dict:
        """Process message in orchestrator stage."""
        response = self.orchestrator.process_message_sync(message)

        if response.is_complete:
            # Brief is complete, move to wellness verification
            self.state.brief = self.orchestrator.get_current_brief()

            # Record handoff
            self.state.handoffs.append(AgentHandoff(
                from_agent="orchestrator",
                to_agent="wellness",
                data=response.brief_data
            ))

            self._change_stage(AgentStage.WELLNESS)

            return {
                "response": response.content,
                "stage": AgentStage.ORCHESTRATOR.value,
                "stage_complete": True,
                "next_action": "verify_brief",
                "data": {
                    "brief": response.brief_data,
                    "message": "I've gathered all the information I need. Let me verify the facts before we create your content."
                }
            }

        return {
            "response": response.content,
            "stage": AgentStage.ORCHESTRATOR.value,
            "stage_complete": False,
            "next_action": "continue_briefing",
            "data": {}
        }

    def _process_wellness(self, message: str) -> dict:
        """Process wellness verification stage."""
        # If this is the first call to wellness, verify the brief
        if not self.state.verification:
            brief_dict = self.state.brief.to_dict() if self.state.brief else {}
            response = self.wellness.verify_brief(brief_dict)

            if response.is_complete:
                self.state.verification = self.wellness.get_last_verification()

                # Record handoff
                self.state.handoffs.append(AgentHandoff(
                    from_agent="wellness",
                    to_agent="storytelling",
                    data=response.brief_data
                ))

                self._change_stage(AgentStage.STORYTELLING_PREVIEW)

                return {
                    "response": response.content,
                    "stage": AgentStage.WELLNESS.value,
                    "stage_complete": True,
                    "next_action": "create_preview",
                    "data": {
                        "verification": self.state.verification.to_dict() if self.state.verification else {},
                        "message": "Facts verified! Now let me create some hook options for your content."
                    }
                }

        # Continue wellness conversation if needed
        response = self.wellness.process_message_sync(message)

        return {
            "response": response.content,
            "stage": AgentStage.WELLNESS.value,
            "stage_complete": response.is_complete,
            "next_action": "verify_more" if not response.is_complete else "create_preview",
            "data": {}
        }

    def _process_storytelling_preview(self, message: str) -> dict:
        """Process storytelling preview stage."""
        # If this is the first call, generate preview
        if not self.state.preview:
            brief_dict = self.state.brief.to_dict() if self.state.brief else {}
            verified_facts = []
            if self.state.verification:
                verified_facts = self.state.verification.verified_facts

            response = self.storytelling.generate_preview(brief_dict, verified_facts)

            self.state.preview = self.storytelling.get_current_preview()

            return {
                "response": response.content,
                "stage": AgentStage.STORYTELLING_PREVIEW.value,
                "stage_complete": False,
                "next_action": "approve_preview",
                "data": {
                    "preview": {
                        "hook": self.state.preview.hook if self.state.preview else "",
                        "hook_type": self.state.preview.hook_type if self.state.preview else "",
                        "open_loops": self.state.preview.open_loops if self.state.preview else [],
                        "promise": self.state.preview.promise if self.state.preview else "",
                    },
                    "message": "Here's a preview of your content. Do you like this direction, or would you like me to try a different approach?"
                }
            }

        # Check if user approved preview
        approval_keywords = ["yes", "approve", "looks good", "love it", "perfect", "go ahead", "proceed"]
        rejection_keywords = ["no", "different", "another", "try again", "change", "don't like"]

        message_lower = message.lower()

        if any(kw in message_lower for kw in approval_keywords):
            # User approved, move to full content generation
            self._change_stage(AgentStage.STORYTELLING_CONTENT)

            return {
                "response": "Great! Let me create the full content based on this preview.",
                "stage": AgentStage.STORYTELLING_PREVIEW.value,
                "stage_complete": True,
                "next_action": "generate_content",
                "data": {}
            }

        elif any(kw in message_lower for kw in rejection_keywords):
            # User wants different preview
            brief_dict = self.state.brief.to_dict() if self.state.brief else {}
            response = self.storytelling.regenerate_hook(brief_dict)
            self.state.preview = self.storytelling.get_current_preview()

            return {
                "response": response.content,
                "stage": AgentStage.STORYTELLING_PREVIEW.value,
                "stage_complete": False,
                "next_action": "approve_preview",
                "data": {
                    "preview": {
                        "hook": self.state.preview.hook if self.state.preview else "",
                        "hook_type": self.state.preview.hook_type if self.state.preview else "",
                    }
                }
            }

        # Continue conversation
        response = self.storytelling.process_message_sync(message)

        return {
            "response": response.content,
            "stage": AgentStage.STORYTELLING_PREVIEW.value,
            "stage_complete": False,
            "next_action": "approve_preview",
            "data": {}
        }

    def _process_storytelling_content(self, message: str) -> dict:
        """Process full content generation stage."""
        # Generate full content if not done yet
        if not self.state.content:
            brief_dict = self.state.brief.to_dict() if self.state.brief else {}
            verified_facts = []
            if self.state.verification:
                verified_facts = self.state.verification.verified_facts

            response = self.storytelling.generate_full_content(
                brief_dict,
                self.state.preview,
                verified_facts
            )

            self.state.content = self.storytelling.get_current_content()

            # Record handoff
            self.state.handoffs.append(AgentHandoff(
                from_agent="storytelling",
                to_agent="review",
                data={"content": self.state.content.content if self.state.content else ""}
            ))

            self._change_stage(AgentStage.REVIEW)

            return {
                "response": response.content,
                "stage": AgentStage.STORYTELLING_CONTENT.value,
                "stage_complete": True,
                "next_action": "collect_feedback",
                "data": {
                    "content": self.state.content.to_dict() if self.state.content else {},
                    "message": "Here's your content! I'd love to get your feedback to help improve future generations."
                }
            }

        return {
            "response": "Content has been generated. Please provide your feedback.",
            "stage": AgentStage.STORYTELLING_CONTENT.value,
            "stage_complete": True,
            "next_action": "collect_feedback",
            "data": {}
        }

    def _process_review(self, message: str) -> dict:
        """Process review/feedback stage."""
        # Collect feedback
        response = self.review.process_message_sync(message)

        # Check if feedback is complete
        if response.is_complete:
            self.state.feedback = self.review.get_current_feedback()
            self._change_stage(AgentStage.COMPLETE)

            return {
                "response": response.content,
                "stage": AgentStage.REVIEW.value,
                "stage_complete": True,
                "next_action": "complete",
                "data": {
                    "feedback": self.state.feedback.to_dict() if self.state.feedback else {},
                    "learnings": [l.to_dict() for l in self.review.get_extracted_learnings()],
                    "message": "Thank you for your feedback! This helps us improve."
                }
            }

        return {
            "response": response.content,
            "stage": AgentStage.REVIEW.value,
            "stage_complete": False,
            "next_action": "continue_feedback",
            "data": {}
        }

    def skip_to_stage(self, stage: AgentStage) -> dict:
        """Skip to a specific stage (for testing or recovery).

        Args:
            stage: Stage to skip to

        Returns:
            dict with stage info
        """
        self._change_stage(stage)

        return {
            "response": f"Skipped to {stage.value} stage.",
            "stage": stage.value,
            "stage_complete": False,
            "next_action": "continue",
            "data": {}
        }

    def go_back(self) -> dict:
        """Go back to the previous stage.

        Returns:
            dict with new stage info
        """
        stage_order = [
            AgentStage.ORCHESTRATOR,
            AgentStage.WELLNESS,
            AgentStage.STORYTELLING_PREVIEW,
            AgentStage.STORYTELLING_CONTENT,
            AgentStage.REVIEW,
            AgentStage.COMPLETE,
        ]

        current_idx = stage_order.index(self.state.stage)
        if current_idx > 0:
            new_stage = stage_order[current_idx - 1]
            self._change_stage(new_stage)

            return {
                "response": f"Going back to {new_stage.value} stage.",
                "stage": new_stage.value,
                "stage_complete": False,
                "next_action": "continue",
                "data": {}
            }

        return {
            "response": "Already at the first stage.",
            "stage": self.state.stage.value,
            "stage_complete": False,
            "next_action": "continue",
            "data": {}
        }

    def get_state_summary(self) -> dict:
        """Get a summary of the current state."""
        return {
            "stage": self.state.stage.value,
            "stage_description": self.get_stage_description(),
            "has_brief": self.state.brief is not None,
            "brief_complete": self.state.brief.is_complete() if self.state.brief else False,
            "has_verification": self.state.verification is not None,
            "has_preview": self.state.preview is not None,
            "has_content": self.state.content is not None,
            "has_feedback": self.state.feedback is not None,
            "conversation_id": self.state.conversation_id,
            "user_id": self.state.user_id,
        }

    def export_state(self) -> dict:
        """Export full state for persistence."""
        return self.state.to_dict()

    def import_state(self, state_dict: dict) -> None:
        """Import state from persistence."""
        self.state = CoordinatorState.from_dict(state_dict)

    def get_total_cost(self) -> float:
        """Get total API cost across all agents."""
        return (
            self.orchestrator.get_stats()["total_cost_usd"] +
            self.wellness.get_stats()["total_cost_usd"] +
            self.storytelling.get_stats()["total_cost_usd"] +
            self.review.get_stats()["total_cost_usd"]
        )

    def get_total_tokens(self) -> int:
        """Get total tokens used across all agents."""
        return (
            self.orchestrator.get_stats()["total_tokens"] +
            self.wellness.get_stats()["total_tokens"] +
            self.storytelling.get_stats()["total_tokens"] +
            self.review.get_stats()["total_tokens"]
        )
