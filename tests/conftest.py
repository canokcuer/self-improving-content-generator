"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("SUPABASE_URL", "https://test-project.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-anon-key")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("VOYAGE_API_KEY", "test-voyage-key")


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    with patch("content_assistant.db.supabase_client.create_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_voyage_client():
    """Mock Voyage AI client for testing."""
    with patch("voyageai.Client") as mock:
        client = MagicMock()
        # Return 1024-dimensional embeddings
        client.embed.return_value.embeddings = [[0.1] * 1024]
        mock.return_value = client
        yield client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch("anthropic.Anthropic") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_brief():
    """Sample content brief for testing."""
    return {
        "target_audience": "Health-conscious professionals aged 35-55",
        "pain_area": "Chronic fatigue and burnout",
        "compliance_level": "high",
        "funnel_stage": "consideration",
        "value_proposition": "Restore energy through medically-supervised detox",
        "desired_action": "Book a free consultation",
        "specific_programs": ["Master Detox", "Mental Wellness"],
        "specific_centers": ["Bodrum", "Antalya"],
        "tone": "warm, educational, hopeful",
        "key_messages": ["Rest, restore, rebuild", "Evidence-based transformation"],
        "constraints": "No medical claims, emphasize 'support' not 'cure'",
        "platform": "instagram_post",
        "price_point": "premium",
    }


@pytest.fixture
def sample_knowledge_chunk():
    """Sample knowledge chunk for testing."""
    return {
        "content": "TheLifeCo Method is built on two powerful foundations: Detoxing/Cleansing and Mental-Emotional Regulation.",
        "source": "thelifeco_method.md",
        "chunk_index": 0,
        "metadata": {"section": "Overview"},
    }


@pytest.fixture
def sample_embedding():
    """Sample 1024-dimensional embedding."""
    return [0.1] * 1024
