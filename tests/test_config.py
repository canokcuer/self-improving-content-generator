"""Tests for configuration module."""

import pytest
from content_assistant.config import (
    Config,
    ConfigurationError,
    get_config,
    clear_config_cache,
)


class TestConfig:
    """Test Config dataclass."""

    def test_config_with_valid_values(self, mock_env_vars):
        """Test configuration with all valid values."""
        config = Config(
            supabase_url="https://test.supabase.co",
            supabase_key="test-key",
            supabase_service_key="test-service-key",
            anthropic_api_key="test-anthropic",
            voyage_api_key="test-voyage",
        )
        assert config.supabase_url == "https://test.supabase.co"
        assert config.claude_model == "claude-sonnet-4-20250514"
        assert config.embedding_dimension == 1024

    def test_config_missing_required_field(self, mock_env_vars):
        """Test that missing required fields raise ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            Config(
                supabase_url="",
                supabase_key="test-key",
                supabase_service_key="test-service-key",
                anthropic_api_key="test-anthropic",
                voyage_api_key="test-voyage",
            )
        assert "supabase_url" in str(exc_info.value)

    def test_config_invalid_embedding_dimension(self, mock_env_vars):
        """Test that invalid embedding dimension raises error."""
        with pytest.raises(ConfigurationError) as exc_info:
            Config(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key",
                supabase_service_key="test-service-key",
                anthropic_api_key="test-anthropic",
                voyage_api_key="test-voyage",
                embedding_dimension=2048,
            )
        assert "embedding_dimension" in str(exc_info.value)

    def test_config_invalid_chunk_overlap(self, mock_env_vars):
        """Test that chunk_overlap >= chunk_size raises error."""
        with pytest.raises(ConfigurationError) as exc_info:
            Config(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key",
                supabase_service_key="test-service-key",
                anthropic_api_key="test-anthropic",
                voyage_api_key="test-voyage",
                chunk_size=100,
                chunk_overlap=100,
            )
        assert "chunk_overlap" in str(exc_info.value)

    def test_config_defaults(self, mock_env_vars):
        """Test that defaults are applied correctly."""
        config = Config(
            supabase_url="https://test.supabase.co",
            supabase_key="test-key",
            supabase_service_key="test-service-key",
            anthropic_api_key="test-anthropic",
            voyage_api_key="test-voyage",
        )
        assert config.chunk_size == 500
        assert config.chunk_overlap == 50
        assert config.max_tokens_per_call == 4096
        assert config.daily_generation_limit == 100
        assert config.monthly_budget_usd == 100.0


class TestGetConfig:
    """Test get_config function."""

    def setup_method(self):
        """Clear config cache before each test."""
        clear_config_cache()

    def teardown_method(self):
        """Clear config cache after each test."""
        clear_config_cache()

    def test_get_config_returns_config(self, mock_env_vars):
        """Test that get_config returns a Config instance."""
        config = get_config()
        assert isinstance(config, Config)
        assert config.supabase_url == "https://test-project.supabase.co"

    def test_get_config_caches_result(self, mock_env_vars):
        """Test that get_config returns the same cached instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_clear_config_cache(self, mock_env_vars):
        """Test that clear_config_cache works."""
        config1 = get_config()
        clear_config_cache()
        config2 = get_config()
        # After clearing, should be a new instance (but equal values)
        assert config1 is not config2
        assert config1.supabase_url == config2.supabase_url
