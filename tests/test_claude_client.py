"""Tests for Claude client module."""

import pytest
from unittest.mock import patch, MagicMock

from content_assistant.generation.claude_client import (
    generate_text,
    generate_json,
    calculate_cost,
    clear_client_cache,
    ClaudeError,
)


class TestCalculateCost:
    """Tests for cost calculation."""

    def test_calculate_cost_sonnet(self):
        """Test cost calculation for Sonnet model."""
        cost = calculate_cost(
            model="claude-sonnet-4-20250514",
            input_tokens=1000,
            output_tokens=500,
        )

        # Input: 1000 / 1M * $3 = $0.003
        # Output: 500 / 1M * $15 = $0.0075
        # Total: $0.0105
        assert abs(cost - 0.0105) < 0.0001

    def test_calculate_cost_haiku(self):
        """Test cost calculation for Haiku model."""
        cost = calculate_cost(
            model="claude-3-5-haiku-20241022",
            input_tokens=1000,
            output_tokens=500,
        )

        # Input: 1000 / 1M * $0.80 = $0.0008
        # Output: 500 / 1M * $4.00 = $0.002
        # Total: $0.0028
        assert abs(cost - 0.0028) < 0.0001

    def test_calculate_cost_unknown_model_uses_default(self):
        """Test that unknown models use default pricing."""
        cost = calculate_cost(
            model="unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )

        # Should use default Sonnet pricing
        assert abs(cost - 0.0105) < 0.0001


class TestGenerateText:
    """Tests for generate_text function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_generate_text_returns_content(self, mock_env_vars):
        """Test that generate_text returns proper response."""
        with patch("content_assistant.generation.claude_client.anthropic.Anthropic") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Generated content")]
            mock_response.usage.input_tokens = 100
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = generate_text("Test prompt")

            assert result["content"] == "Generated content"
            assert result["input_tokens"] == 100
            assert result["output_tokens"] == 50
            assert "cost_usd" in result
            assert "model" in result

    def test_generate_text_empty_prompt_raises(self, mock_env_vars):
        """Test that empty prompt raises error."""
        with pytest.raises(ClaudeError):
            generate_text("")

        with pytest.raises(ClaudeError):
            generate_text("   ")

    def test_generate_text_with_system_prompt(self, mock_env_vars):
        """Test that system prompt is passed correctly."""
        with patch("content_assistant.generation.claude_client.anthropic.Anthropic") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Response")]
            mock_response.usage.input_tokens = 100
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            generate_text("Test prompt", system_prompt="Be helpful")

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["system"] == "Be helpful"


class TestGenerateJson:
    """Tests for generate_json function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_generate_json_parses_response(self, mock_env_vars):
        """Test that JSON is properly parsed."""
        with patch("content_assistant.generation.claude_client.anthropic.Anthropic") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='{"key": "value", "number": 42}')]
            mock_response.usage.input_tokens = 100
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = generate_json("Return JSON")

            assert result["data"] == {"key": "value", "number": 42}
            assert "input_tokens" in result
            assert "cost_usd" in result

    def test_generate_json_handles_code_blocks(self, mock_env_vars):
        """Test that JSON in code blocks is extracted."""
        with patch("content_assistant.generation.claude_client.anthropic.Anthropic") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='```json\n{"key": "value"}\n```')]
            mock_response.usage.input_tokens = 100
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = generate_json("Return JSON")

            assert result["data"] == {"key": "value"}

    def test_generate_json_invalid_json_raises(self, mock_env_vars):
        """Test that invalid JSON raises error."""
        with patch("content_assistant.generation.claude_client.anthropic.Anthropic") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="not valid json")]
            mock_response.usage.input_tokens = 100
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ClaudeError) as exc_info:
                generate_json("Return JSON")

            assert "Failed to parse JSON" in str(exc_info.value)
