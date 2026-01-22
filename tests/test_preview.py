"""Tests for content preview generator."""

import pytest
from unittest.mock import patch

from content_assistant.generation.preview import (
    ContentPreview,
    generate_preview,
    regenerate_hook,
    HOOK_TYPES,
)
from content_assistant.generation.brief import ContentBrief, Platform, ContentType
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
        tone="warm and encouraging",
        hook_style="question",
    )


class TestContentPreview:
    """Tests for ContentPreview dataclass."""

    def test_create_preview(self):
        """Test creating a content preview."""
        preview = ContentPreview(
            hook="What if I told you 5 minutes could change your entire day?",
            hook_type="question",
            open_loops=["The science behind morning routines", "The 5-minute framework"],
            promise="A simple ritual that transforms chaotic mornings into calm clarity",
            brief_summary="Introduce TheLifeCo's morning mindfulness routine",
        )

        assert preview.hook_type == "question"
        assert len(preview.open_loops) == 2

    def test_preview_to_dict(self):
        """Test converting preview to dictionary."""
        preview = ContentPreview(
            hook="Test hook",
            hook_type="bold_claim",
            open_loops=["Loop 1", "Loop 2"],
            promise="Test promise",
            brief_summary="Test summary",
        )

        data = preview.to_dict()

        assert data["hook"] == "Test hook"
        assert data["hook_type"] == "bold_claim"
        assert len(data["open_loops"]) == 2

    def test_preview_from_dict(self):
        """Test creating preview from dictionary."""
        data = {
            "hook": "Test hook",
            "hook_type": "story",
            "open_loops": ["Loop 1"],
            "promise": "Test promise",
            "brief_summary": "Test summary",
        }

        preview = ContentPreview.from_dict(data)

        assert preview.hook == "Test hook"
        assert preview.hook_type == "story"


class TestHookTypes:
    """Tests for hook type definitions."""

    def test_all_hook_types_defined(self):
        """Test that all expected hook types are defined."""
        expected = [
            "question",
            "bold_claim",
            "story",
            "statistic",
            "contrast",
            "curiosity",
            "pain_point",
            "promise",
        ]

        assert set(expected) == set(HOOK_TYPES)


class TestGeneratePreview:
    """Tests for preview generation."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_generate_preview_returns_preview_and_metadata(self, mock_env_vars, sample_brief):
        """Test that generate_preview returns correct structure."""
        mock_response = {
            "hook": "What if 5 minutes could change your whole day?",
            "hook_type": "question",
            "open_loops": ["The morning routine mistake most people make", "The science of mindful mornings"],
            "promise": "A simple framework for calm, focused mornings",
            "brief_summary": "Introduce the 5-minute mindful morning ritual",
        }

        with patch("content_assistant.generation.preview.generate_json") as mock_gen:
            mock_gen.return_value = {
                "data": mock_response,
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 500,
                "output_tokens": 200,
                "cost_usd": 0.0045,
            }

            preview, metadata = generate_preview(sample_brief)

            assert isinstance(preview, ContentPreview)
            assert preview.hook_type == "question"
            assert len(preview.open_loops) == 2
            assert metadata["cost_usd"] == 0.0045

    def test_generate_preview_normalizes_hook_type(self, mock_env_vars, sample_brief):
        """Test that invalid hook types are normalized."""
        mock_response = {
            "hook": "Test hook",
            "hook_type": "Unknown Type",  # Invalid
            "open_loops": ["Loop 1"],
            "promise": "Test promise",
            "brief_summary": "Test summary",
        }

        with patch("content_assistant.generation.preview.generate_json") as mock_gen:
            mock_gen.return_value = {
                "data": mock_response,
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 500,
                "output_tokens": 200,
                "cost_usd": 0.0045,
            }

            preview, _ = generate_preview(sample_brief)

            # Should fall back to "curiosity"
            assert preview.hook_type == "curiosity"

    def test_generate_preview_with_knowledge_context(self, mock_env_vars, sample_brief):
        """Test that knowledge context is included in prompt."""
        mock_response = {
            "hook": "Test hook",
            "hook_type": "question",
            "open_loops": ["Loop 1"],
            "promise": "Test promise",
            "brief_summary": "Test summary",
        }

        with patch("content_assistant.generation.preview.generate_json") as mock_gen:
            mock_gen.return_value = {
                "data": mock_response,
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 500,
                "output_tokens": 200,
                "cost_usd": 0.0045,
            }

            generate_preview(sample_brief, knowledge_context="Relevant wellness info")

            # Check that the prompt includes knowledge context
            call_args = mock_gen.call_args
            prompt = call_args[1]["prompt"]
            assert "Relevant wellness info" in prompt


class TestRegenerateHook:
    """Tests for hook regeneration."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_regenerate_hook_returns_new_preview(self, mock_env_vars, sample_brief):
        """Test that regenerate_hook returns updated preview."""
        current_preview = ContentPreview(
            hook="Original hook",
            hook_type="question",
            open_loops=["Loop 1"],
            promise="Original promise",
            brief_summary="Original summary",
        )

        mock_response = {
            "hook": "New improved hook",
            "hook_type": "bold_claim",
            "open_loops": ["Loop 1"],
            "promise": "Original promise",
            "brief_summary": "Original summary",
        }

        with patch("content_assistant.generation.preview.generate_json") as mock_gen:
            mock_gen.return_value = {
                "data": mock_response,
                "model": "claude-sonnet-4-20250514",
                "input_tokens": 600,
                "output_tokens": 200,
                "cost_usd": 0.0048,
            }

            new_preview, metadata = regenerate_hook(
                brief=sample_brief,
                current_preview=current_preview,
                feedback="Make it more bold and attention-grabbing",
            )

            assert new_preview.hook == "New improved hook"
            assert new_preview.hook_type == "bold_claim"
