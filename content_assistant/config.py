"""Configuration management for TheLifeCo Content Assistant.

Loads configuration from environment variables with sensible defaults
and validation for required variables.
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""

    pass


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # AI Services
    anthropic_api_key: str
    voyage_api_key: str

    # Model Configuration
    claude_model: str = "claude-sonnet-4-20250514"
    voyage_model: str = "voyage-3-lite"
    embedding_dimension: int = 1024

    # Chunking Configuration
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Cost Control Limits
    max_tokens_per_call: int = 4096
    max_few_shot_examples: int = 5
    daily_generation_limit: int = 100
    monthly_budget_usd: float = 100.0
    cost_alert_threshold: float = 0.8

    # Optional Test Configuration
    test_email: Optional[str] = None
    test_password: Optional[str] = None

    # Paths
    knowledge_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge"
    ))

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self):
        """Validate required configuration values."""
        required_fields = [
            ("supabase_url", self.supabase_url),
            ("supabase_key", self.supabase_key),
            ("supabase_service_key", self.supabase_service_key),
            ("anthropic_api_key", self.anthropic_api_key),
            ("voyage_api_key", self.voyage_api_key),
        ]

        missing = [name for name, value in required_fields if not value]

        if missing:
            raise ConfigurationError(
                f"Missing required configuration: {', '.join(missing)}. "
                "Please set these environment variables or check your .env file."
            )

        # Validate embedding dimension
        if self.embedding_dimension not in [512, 1024]:
            raise ConfigurationError(
                f"Invalid embedding_dimension: {self.embedding_dimension}. "
                "Must be 512 or 1024 for Voyage AI."
            )

        # Validate chunk configuration
        if self.chunk_overlap >= self.chunk_size:
            raise ConfigurationError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than "
                f"chunk_size ({self.chunk_size})."
            )


def _get_secret(key: str, default: str = "") -> str:
    """Get secret from Streamlit secrets or environment variable."""
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            try:
                value = st.secrets.get(key)
                if value is not None:
                    return value
            except Exception:
                pass
    except Exception:
        pass
    # Fall back to environment variable
    return os.getenv(key, default)


def _load_config() -> Config:
    """Load configuration from environment variables."""
    # Load .env file if it exists
    load_dotenv()

    def get_int(key: str, default: int) -> int:
        """Get integer from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_float(key: str, default: float) -> float:
        """Get float from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    return Config(
        # Required (check st.secrets first, then env vars)
        supabase_url=_get_secret("SUPABASE_URL"),
        supabase_key=_get_secret("SUPABASE_KEY"),
        supabase_service_key=_get_secret("SUPABASE_SERVICE_KEY"),
        anthropic_api_key=_get_secret("ANTHROPIC_API_KEY"),
        voyage_api_key=_get_secret("VOYAGE_API_KEY"),
        # Model Configuration
        claude_model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
        voyage_model=os.getenv("VOYAGE_MODEL", "voyage-3-lite"),
        embedding_dimension=get_int("EMBEDDING_DIMENSION", 1024),
        # Chunking
        chunk_size=get_int("CHUNK_SIZE", 500),
        chunk_overlap=get_int("CHUNK_OVERLAP", 50),
        # Cost Control
        max_tokens_per_call=get_int("MAX_TOKENS_PER_CALL", 4096),
        max_few_shot_examples=get_int("MAX_FEW_SHOT_EXAMPLES", 5),
        daily_generation_limit=get_int("DAILY_GENERATION_LIMIT", 100),
        monthly_budget_usd=get_float("MONTHLY_BUDGET_USD", 100.0),
        cost_alert_threshold=get_float("COST_ALERT_THRESHOLD", 0.8),
        # Optional
        test_email=os.getenv("TEST_EMAIL"),
        test_password=os.getenv("TEST_PASSWORD"),
    )


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get cached configuration instance.

    Returns:
        Config: The application configuration

    Raises:
        ConfigurationError: If required configuration is missing
    """
    return _load_config()


def clear_config_cache():
    """Clear the configuration cache. Useful for testing."""
    get_config.cache_clear()
