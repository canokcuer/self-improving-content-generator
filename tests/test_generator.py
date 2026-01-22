"""Tests for content generator module."""

import pytest
from unittest.mock import patch

from content_assistant.generation.generator import (
    GeneratedContent,
    generate_content,
    regenerate_content,
    estimate_generation_cost,
)
from content_assistant.generation.brief import ContentBrief, Platform, ContentType
from content_assistant.generation.preview import ContentPreview
from content_assistant.generation.claude_client import clear_client_cache


@pytest.fixture
def sample_brief():
    """Create a sample brief for testing."""
    return ContentBrief(
        platform=Platform.INSTAGRAM,
        content_type=ContentType.POST,
        transformation="Help readers understand the power of morning rituals",
        audience="Busy professionals who feel overwhelmed",
        pain_point="Chaotic mornings leading to stressful days",
        unique_angle="TheLifeCo's 5-minute mindful morning framework",
        core_message="A mindful morning creates a mindful day",
        call_to_action="Save this post and try it tomorrow",
    )


@pytest.fixture
def sample_preview():
    """Create a sample preview for testing."""
    return ContentPreview(
        hook="What if 5 minutes could transform your entire day?",
        hook_type="question",
        open_loops=["The morning routine mistake", "The 5-minute framework"],
        promise="A simple ritual for calm, focused mornings",
        brief_summary="Introduce TheLifeCo's morning mindfulness routine",
    )


class TestGeneratedContent:
    """Tests for GeneratedContent dataclass."""

    def test_create_content(self, sample_brief, sample_preview):
        """Test creating generated content."""
        content = GeneratedContent(
            content="What if 5 minutes could transform your entire day?\n\nHere's the truth...",
            brief=sample_brief,
            preview=sample_preview,
        )

        assert content.word_count > 0
        assert content.character_count > 0

    def test_content_extracts_hashtags(self, sample_brief, sample_preview):
        """Test that hashtags are extracted."""
        content = GeneratedContent(
            content="Great content here #wellness #morningroutine #thelifeco",
            brief=sample_brief,
            preview=sample_preview,
        )

        assert len(content.hashtags) == 3
        assert "#wellness" in content.hashtags

    def test_content_to_dict(self, sample_brief, sample_preview):
        """Test converting content to dictionary."""
        content = GeneratedContent(
            content="Test content",
            brief=sample_brief,
            preview=sample_preview,
            metadata={"cost_usd": 0.01},
        )

        data = content.to_dict()

        assert data["content"] == "Test content"
        assert "brief" in data
        assert "preview" in data
        assert data["metadata"]["cost_usd"] == 0.01


class TestGenerateContent:
    """Tests for content generation."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_generate_content_returns_generated_content(
        self, mock_env_vars, sample_brief, sample_preview
    ):
        """Test that generate_content returns proper structure."""
        with patch("content_assistant.generation.generator.generate_text") as mock_gen:
            mock_gen.return_value = {
                "content": "What if 5 minutes could transform your entire day?\n\nThe truth is...",
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 1000,
                "output_tokens": 300,
                "cost_usd": 0.0075,
            }

            result = generate_content(sample_brief, sample_preview)

            assert isinstance(result, GeneratedContent)
            assert "5 minutes" in result.content
            assert result.metadata["cost_usd"] == 0.0075

    def test_generate_content_with_knowledge_context(
        self, mock_env_vars, sample_brief, sample_preview
    ):
        """Test that knowledge context is included."""
        with patch("content_assistant.generation.generator.generate_text") as mock_gen:
            mock_gen.return_value = {
                "content": "Generated content",
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 1000,
                "output_tokens": 300,
                "cost_usd": 0.0075,
            }

            generate_content(
                sample_brief,
                sample_preview,
                knowledge_context="TheLifeCo wellness knowledge",
            )

            call_args = mock_gen.call_args
            prompt = call_args[1]["prompt"]
            assert "TheLifeCo wellness knowledge" in prompt

    def test_generate_content_with_few_shot_examples(
        self, mock_env_vars, sample_brief, sample_preview
    ):
        """Test that few-shot examples are included."""
        examples = [
            {"content": "Example 1 content", "rating": 5},
            {"content": "Example 2 content", "rating": 4},
        ]

        with patch("content_assistant.generation.generator.generate_text") as mock_gen:
            mock_gen.return_value = {
                "content": "Generated content",
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 1000,
                "output_tokens": 300,
                "cost_usd": 0.0075,
            }

            generate_content(
                sample_brief,
                sample_preview,
                few_shot_examples=examples,
            )

            call_args = mock_gen.call_args
            prompt = call_args[1]["prompt"]
            assert "Example 1" in prompt
            assert "Rating: 5" in prompt


class TestRegenerateContent:
    """Tests for content regeneration."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_regenerate_content_returns_new_content(
        self, mock_env_vars, sample_brief, sample_preview
    ):
        """Test that regenerate_content returns improved content."""
        original = GeneratedContent(
            content="Original content here",
            brief=sample_brief,
            preview=sample_preview,
        )

        with patch("content_assistant.generation.generator.generate_text") as mock_gen:
            mock_gen.return_value = {
                "content": "New improved content",
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 1200,
                "output_tokens": 350,
                "cost_usd": 0.0088,
            }

            result = regenerate_content(
                original=original,
                feedback="Make it more engaging",
            )

            assert result.content == "New improved content"
            assert result.metadata["regeneration_feedback"] == "Make it more engaging"


class TestEstimateGenerationCost:
    """Tests for cost estimation."""

    def test_estimate_post_cost(self):
        """Test cost estimation for post."""
        brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            transformation="Test",
            audience="Test",
            pain_point="Test",
            unique_angle="Test",
            core_message="Test",
            call_to_action="Test",
        )

        estimate = estimate_generation_cost(brief)

        assert "estimated_input_tokens" in estimate
        assert "estimated_output_tokens" in estimate
        assert "estimated_cost_usd" in estimate
        assert estimate["estimated_cost_usd"] > 0

    def test_estimate_article_cost_higher_than_post(self):
        """Test that article costs more than post."""
        post_brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            transformation="Test",
            audience="Test",
            pain_point="Test",
            unique_angle="Test",
            core_message="Test",
            call_to_action="Test",
        )

        article_brief = ContentBrief(
            platform=Platform.BLOG,
            content_type=ContentType.ARTICLE,
            transformation="Test",
            audience="Test",
            pain_point="Test",
            unique_angle="Test",
            core_message="Test",
            call_to_action="Test",
        )

        post_estimate = estimate_generation_cost(post_brief)
        article_estimate = estimate_generation_cost(article_brief)

        assert article_estimate["estimated_cost_usd"] > post_estimate["estimated_cost_usd"]
