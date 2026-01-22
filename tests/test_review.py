"""Tests for the review module."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from content_assistant.review.few_shot import (
    get_few_shot_examples,
    format_examples_for_prompt,
)
from content_assistant.review.wellness_verifier import (
    WellnessVerificationResult,
    verify_wellness_claims,
    get_verification_summary,
)
from content_assistant.review.engagement import (
    EngagementAnalysis,
    analyze_engagement,
    get_engagement_summary,
)
from content_assistant.review.signals import (
    store_generation_signals,
    update_generation_rating,
)
from content_assistant.review.ranker import (
    rank_examples,
)
from content_assistant.review.experiments import (
    create_experiment,
    assign_variant,
)


class TestFewShot:
    """Tests for few-shot retrieval."""

    def test_get_few_shot_examples_empty_brief(self, mock_env_vars):
        """Test that empty brief returns empty list."""
        result = get_few_shot_examples("")
        assert result == []

        result = get_few_shot_examples("   ")
        assert result == []

    def test_format_examples_for_prompt_empty(self):
        """Test formatting with no examples."""
        result = format_examples_for_prompt([])
        assert result == ""

    def test_format_examples_for_prompt_with_examples(self):
        """Test formatting with examples."""
        examples = [
            {"content": "Example content 1", "rating": 5, "platform": "instagram"},
            {"content": "Example content 2", "rating": 4, "platform": "linkedin"},
        ]

        result = format_examples_for_prompt(examples)

        assert "Example 1" in result
        assert "Example 2" in result
        assert "Example content 1" in result
        assert "Rating: 5/5" in result


class TestWellnessVerifier:
    """Tests for wellness verification."""

    def test_verification_result_to_dict(self):
        """Test converting verification result to dict."""
        result = WellnessVerificationResult(
            is_verified=True,
            score=85,
            claims_found=["Claim 1", "Claim 2"],
            verified_claims=["Claim 1"],
            unverified_claims=["Claim 2"],
        )

        data = result.to_dict()

        assert data["is_verified"] is True
        assert data["score"] == 85
        assert len(data["claims_found"]) == 2

    def test_verify_empty_content(self, mock_env_vars):
        """Test verifying empty content."""
        result = verify_wellness_claims("")

        assert result.is_verified is True
        assert result.score == 100
        assert result.claims_found == []

    def test_get_verification_summary_passed(self):
        """Test summary for passed verification."""
        result = WellnessVerificationResult(
            is_verified=True,
            score=90,
            verified_claims=["Detox helps reset the body"],
        )

        summary = get_verification_summary(result)

        assert "PASSED" in summary
        assert "90/100" in summary


class TestEngagement:
    """Tests for engagement analysis."""

    def test_engagement_analysis_to_dict(self):
        """Test converting analysis to dict."""
        analysis = EngagementAnalysis(
            overall_score=75,
            hook_strength=80,
            hook_analysis="Strong opening question",
            retention_score=70,
            clarity_score=85,
            cta_effectiveness=60,
            strengths=["Good hook", "Clear message"],
            improvements=["Stronger CTA needed"],
        )

        data = analysis.to_dict()

        assert data["overall_score"] == 75
        assert len(data["strengths"]) == 2
        assert len(data["improvements"]) == 1

    def test_analyze_empty_content(self, mock_env_vars):
        """Test analyzing empty content."""
        result = analyze_engagement("")

        assert result.overall_score == 0
        assert result.hook_analysis == "No content provided"

    def test_get_engagement_summary(self):
        """Test engagement summary generation."""
        analysis = EngagementAnalysis(
            overall_score=85,
            hook_strength=90,
            hook_analysis="Excellent hook",
            retention_score=80,
            clarity_score=85,
            cta_effectiveness=75,
            platform_fit=90,
            strengths=["Great hook"],
            improvements=["Could improve CTA"],
        )

        summary = get_engagement_summary(analysis)

        assert "B (85/100)" in summary  # Grade B for 85
        assert "Hook Strength: 90/100" in summary
        assert "Great hook" in summary


class TestSignals:
    """Tests for signal storage."""

    def test_store_generation_signals_validates_data(self, mock_env_vars):
        """Test that signal storage works with mocked client."""
        with patch("content_assistant.review.signals.get_admin_client") as mock_client:
            mock_response = MagicMock()
            mock_response.data = [{"id": "test-uuid-123"}]
            mock_client.return_value.table.return_value.insert.return_value.execute.return_value = mock_response

            with patch("content_assistant.review.signals.embed_text") as mock_embed:
                mock_embed.return_value = [0.1] * 1024

                result = store_generation_signals(
                    brief={"transformation": "Test"},
                    preview={"hook": "Test hook"},
                    content="Test content",
                    platform="instagram",
                    content_type="post",
                )

                assert result == "test-uuid-123"

    def test_update_rating_validates_range(self, mock_env_vars):
        """Test that rating validation works."""
        from content_assistant.review.signals import SignalError

        with pytest.raises(SignalError) as exc_info:
            update_generation_rating("test-id", rating=6)

        assert "between 1 and 5" in str(exc_info.value)

        with pytest.raises(SignalError) as exc_info:
            update_generation_rating("test-id", rating=0)

        assert "between 1 and 5" in str(exc_info.value)


class TestRanker:
    """Tests for example ranking."""

    def test_rank_empty_candidates(self, mock_env_vars):
        """Test ranking empty list."""
        result = rank_examples("test query", [])
        assert result == []

    def test_rank_by_combined_score(self, mock_env_vars):
        """Test that ranking uses combined score."""
        now = datetime.utcnow()

        candidates = [
            {
                "content": "Low rated",
                "rating": 2,
                "similarity": 0.9,
                "created_at": (now - timedelta(days=30)).isoformat(),
            },
            {
                "content": "High rated",
                "rating": 5,
                "similarity": 0.8,
                "created_at": now.isoformat(),
            },
            {
                "content": "Medium rated",
                "rating": 3,
                "similarity": 0.85,
                "created_at": (now - timedelta(days=15)).isoformat(),
            },
        ]

        with patch("content_assistant.review.ranker.embed_query") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            ranked = rank_examples(
                "test query",
                candidates,
                similarity_weight=0.3,
                rating_weight=0.5,
                recency_weight=0.2,
            )

            # High rated should be first due to high rating weight
            assert ranked[0]["content"] == "High rated"
            assert "combined_score" in ranked[0]


class TestExperiments:
    """Tests for experiment framework."""

    def test_create_experiment_requires_name(self, mock_env_vars):
        """Test that experiment requires name."""
        from content_assistant.review.experiments import ExperimentError

        with pytest.raises(ExperimentError) as exc_info:
            create_experiment(
                name="",
                description="Test",
                variants={"control": {}, "treatment": {}},
            )

        assert "name is required" in str(exc_info.value)

    def test_create_experiment_requires_two_variants(self, mock_env_vars):
        """Test that experiment requires at least 2 variants."""
        from content_assistant.review.experiments import ExperimentError

        with pytest.raises(ExperimentError) as exc_info:
            create_experiment(
                name="Test",
                description="Test",
                variants={"control": {}},  # Only 1 variant
            )

        assert "2 variants" in str(exc_info.value)

    def test_create_experiment_validates_traffic_split(self, mock_env_vars):
        """Test that traffic split must sum to 1."""
        from content_assistant.review.experiments import ExperimentError

        with pytest.raises(ExperimentError) as exc_info:
            create_experiment(
                name="Test",
                description="Test",
                variants={"control": {}, "treatment": {}},
                traffic_split={"control": 0.3, "treatment": 0.3},  # Sum = 0.6
            )

        assert "sum to 1.0" in str(exc_info.value)

    def test_assign_variant_returns_existing(self, mock_env_vars):
        """Test that existing assignment is returned."""
        with patch("content_assistant.review.experiments.get_admin_client") as mock_client:
            # Mock existing assignment
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
                {"variant": "treatment"}
            ]

            result = assign_variant("exp-123", "user-456")

            assert result == "treatment"
