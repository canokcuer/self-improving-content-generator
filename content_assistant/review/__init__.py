"""Content review and signal collection module."""

from content_assistant.review.few_shot import (
    get_few_shot_examples,
    FewShotError,
)
from content_assistant.review.wellness_verifier import (
    verify_wellness_claims,
    WellnessVerificationResult,
    VerifierError,
)
from content_assistant.review.engagement import (
    analyze_engagement,
    EngagementAnalysis,
    EngagementError,
)
from content_assistant.review.signals import (
    store_generation_signals,
    get_generation_by_id,
    update_generation_rating,
    SignalError,
)
from content_assistant.review.ranker import (
    rank_examples,
    RankerError,
)
from content_assistant.review.experiments import (
    create_experiment,
    get_active_experiments,
    assign_variant,
    ExperimentError,
)

__all__ = [
    # Few-shot
    "get_few_shot_examples",
    "FewShotError",
    # Wellness verifier
    "verify_wellness_claims",
    "WellnessVerificationResult",
    "VerifierError",
    # Engagement
    "analyze_engagement",
    "EngagementAnalysis",
    "EngagementError",
    # Signals
    "store_generation_signals",
    "get_generation_by_id",
    "update_generation_rating",
    "SignalError",
    # Ranker
    "rank_examples",
    "RankerError",
    # Experiments
    "create_experiment",
    "get_active_experiments",
    "assign_variant",
    "ExperimentError",
]
