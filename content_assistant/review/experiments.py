"""A/B Experiment framework for content generation.

Manages experiment definitions, variant assignment, and
signal collection for comparing different generation strategies.
"""

from typing import Optional
from uuid import UUID

from content_assistant.db.supabase_client import get_admin_client


class ExperimentError(Exception):
    """Raised when experiment operations fail."""

    pass


def create_experiment(
    name: str,
    description: str,
    variants: dict,
    traffic_split: Optional[dict] = None,
) -> str:
    """Create a new A/B experiment.

    Args:
        name: Experiment name
        description: What the experiment tests
        variants: Dict of variant configs, e.g., {"control": {...}, "treatment": {...}}
        traffic_split: Dict of variant -> percentage, e.g., {"control": 0.5, "treatment": 0.5}

    Returns:
        str: UUID of the created experiment

    Raises:
        ExperimentError: If creation fails
    """
    if not name or not name.strip():
        raise ExperimentError("Experiment name is required")

    if not variants or len(variants) < 2:
        raise ExperimentError("At least 2 variants are required")

    # Default to equal split
    if traffic_split is None:
        equal_share = 1.0 / len(variants)
        traffic_split = {v: equal_share for v in variants.keys()}

    # Validate traffic split sums to 1
    total_traffic = sum(traffic_split.values())
    if abs(total_traffic - 1.0) > 0.01:
        raise ExperimentError(f"Traffic split must sum to 1.0, got {total_traffic}")

    try:
        client = get_admin_client()

        data = {
            "name": name,
            "description": description,
            "variants": variants,
            "traffic_split": traffic_split,
            "status": "draft",
        }

        result = client.table("experiments").insert(data).execute()

        if not result.data:
            raise ExperimentError("No data returned after insert")

        return result.data[0]["id"]

    except ExperimentError:
        raise
    except Exception as e:
        raise ExperimentError(f"Failed to create experiment: {e}") from e


def get_experiment(experiment_id: str | UUID) -> Optional[dict]:
    """Get an experiment by ID.

    Args:
        experiment_id: UUID of the experiment

    Returns:
        Experiment data dict or None if not found

    Raises:
        ExperimentError: If query fails
    """
    try:
        client = get_admin_client()

        result = (
            client.table("experiments")
            .select("*")
            .eq("id", str(experiment_id))
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    except Exception as e:
        raise ExperimentError(f"Failed to get experiment: {e}") from e


def get_active_experiments() -> list[dict]:
    """Get all active (running) experiments.

    Returns:
        List of active experiment dicts

    Raises:
        ExperimentError: If query fails
    """
    try:
        client = get_admin_client()

        result = (
            client.table("experiments")
            .select("*")
            .eq("status", "running")
            .execute()
        )

        return result.data or []

    except Exception as e:
        raise ExperimentError(f"Failed to get active experiments: {e}") from e


def start_experiment(experiment_id: str | UUID) -> bool:
    """Start an experiment (set status to running).

    Args:
        experiment_id: UUID of the experiment

    Returns:
        True if started successfully

    Raises:
        ExperimentError: If update fails
    """
    try:
        from datetime import datetime

        client = get_admin_client()

        result = (
            client.table("experiments")
            .update({
                "status": "running",
                "start_date": datetime.utcnow().isoformat(),
            })
            .eq("id", str(experiment_id))
            .execute()
        )

        return len(result.data) > 0

    except Exception as e:
        raise ExperimentError(f"Failed to start experiment: {e}") from e


def stop_experiment(experiment_id: str | UUID) -> bool:
    """Stop an experiment (set status to completed).

    Args:
        experiment_id: UUID of the experiment

    Returns:
        True if stopped successfully

    Raises:
        ExperimentError: If update fails
    """
    try:
        from datetime import datetime

        client = get_admin_client()

        result = (
            client.table("experiments")
            .update({
                "status": "completed",
                "end_date": datetime.utcnow().isoformat(),
            })
            .eq("id", str(experiment_id))
            .execute()
        )

        return len(result.data) > 0

    except Exception as e:
        raise ExperimentError(f"Failed to stop experiment: {e}") from e


def assign_variant(
    experiment_id: str | UUID,
    user_id: str,
) -> str:
    """Assign a user to an experiment variant.

    Uses consistent hashing to ensure the same user always
    gets the same variant for a given experiment.

    Args:
        experiment_id: UUID of the experiment
        user_id: User identifier

    Returns:
        str: Assigned variant name

    Raises:
        ExperimentError: If assignment fails
    """
    try:
        client = get_admin_client()

        # Check for existing assignment
        existing = (
            client.table("experiment_assignments")
            .select("variant")
            .eq("experiment_id", str(experiment_id))
            .eq("user_id", user_id)
            .execute()
        )

        if existing.data:
            return existing.data[0]["variant"]

        # Get experiment for traffic split
        experiment = get_experiment(experiment_id)
        if not experiment:
            raise ExperimentError(f"Experiment {experiment_id} not found")

        if experiment["status"] != "running":
            raise ExperimentError(f"Experiment is not running (status: {experiment['status']})")

        # Assign based on traffic split
        traffic_split = experiment.get("traffic_split", {})

        # Use consistent hash for deterministic assignment
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = hash(hash_input) % 10000 / 10000.0  # 0-1 range

        cumulative = 0.0
        assigned_variant = None
        for variant, percentage in traffic_split.items():
            cumulative += percentage
            if hash_value < cumulative:
                assigned_variant = variant
                break

        if assigned_variant is None:
            # Fallback to first variant
            assigned_variant = list(traffic_split.keys())[0]

        # Store assignment
        client.table("experiment_assignments").insert({
            "experiment_id": str(experiment_id),
            "user_id": user_id,
            "variant": assigned_variant,
        }).execute()

        return assigned_variant

    except ExperimentError:
        raise
    except Exception as e:
        raise ExperimentError(f"Failed to assign variant: {e}") from e


def get_variant_config(
    experiment_id: str | UUID,
    variant: str,
) -> Optional[dict]:
    """Get the configuration for a specific variant.

    Args:
        experiment_id: UUID of the experiment
        variant: Variant name

    Returns:
        Variant configuration dict or None

    Raises:
        ExperimentError: If query fails
    """
    experiment = get_experiment(experiment_id)
    if not experiment:
        return None

    variants = experiment.get("variants", {})
    return variants.get(variant)


def get_experiment_results(experiment_id: str | UUID) -> dict:
    """Get aggregated results for an experiment.

    Args:
        experiment_id: UUID of the experiment

    Returns:
        Dict with variant-level statistics

    Raises:
        ExperimentError: If query fails
    """
    try:
        client = get_admin_client()

        # Get all generations for this experiment
        result = (
            client.table("content_generations")
            .select("variant, rating, was_approved")
            .eq("experiment_id", str(experiment_id))
            .execute()
        )

        generations = result.data or []

        # Aggregate by variant
        variant_stats = {}
        for gen in generations:
            variant = gen.get("variant", "unknown")
            if variant not in variant_stats:
                variant_stats[variant] = {
                    "count": 0,
                    "approved": 0,
                    "ratings": [],
                }

            variant_stats[variant]["count"] += 1

            if gen.get("was_approved"):
                variant_stats[variant]["approved"] += 1

            if gen.get("rating"):
                variant_stats[variant]["ratings"].append(gen["rating"])

        # Calculate metrics
        results = {}
        for variant, stats in variant_stats.items():
            avg_rating = (
                sum(stats["ratings"]) / len(stats["ratings"])
                if stats["ratings"] else 0
            )
            approval_rate = (
                stats["approved"] / stats["count"] * 100
                if stats["count"] > 0 else 0
            )

            results[variant] = {
                "total_generations": stats["count"],
                "approved_count": stats["approved"],
                "approval_rate": round(approval_rate, 2),
                "average_rating": round(avg_rating, 2),
                "rated_count": len(stats["ratings"]),
            }

        return results

    except Exception as e:
        raise ExperimentError(f"Failed to get results: {e}") from e


def get_winning_variant(experiment_id: str | UUID) -> Optional[str]:
    """Determine the winning variant based on results.

    Uses a combination of approval rate and average rating.

    Args:
        experiment_id: UUID of the experiment

    Returns:
        Winning variant name or None if inconclusive

    Raises:
        ExperimentError: If calculation fails
    """
    results = get_experiment_results(experiment_id)

    if not results:
        return None

    # Score each variant
    scores = {}
    for variant, stats in results.items():
        # Need minimum sample size
        if stats["total_generations"] < 5:
            continue

        # Combined score: 60% approval rate, 40% average rating
        approval_score = stats["approval_rate"] / 100
        rating_score = stats["average_rating"] / 5

        scores[variant] = 0.6 * approval_score + 0.4 * rating_score

    if not scores:
        return None

    # Return highest scoring variant
    return max(scores, key=scores.get)
