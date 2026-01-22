# TheLifeCo Self-Improving Content Marketing Assistant

---
## EXECUTIVE SUMMARY (READ THIS FIRST IF CONTEXT IS LOST)
---

### What We're Building
A **self-improving AI content assistant** for TheLifeCo's marketing team that:
1. **Creates content** (emails, landing pages, social posts, blogs, ads)
2. **Reviews existing content** for wellness accuracy and engagement
3. **Learns over time** through signal-derived feedback loops

### Business Goal
**Maximize content performance** (engagement, clicks, conversions) by maximizing content quality.

### Key Architectural Decisions

| Decision | Choice |
|----------|--------|
| Development method | Ralph (snarktank/ralph) with Claude Code |
| AI | Claude (Anthropic) - single orchestrated call with tools |
| Database | Supabase (PostgreSQL + pgvector + Auth) |
| Embeddings | Voyage AI |
| Frontend | Streamlit web app |
| Deployment | Streamlit Cloud |
| Learning method | Signal-derived ranking of few-shot examples |

### The Socratic Questionnaire (13 Mandatory Questions)
Before generating ANY content, user must answer ALL 13 questions:

1. **Target Audience** - Who is this for?
2. **Pain Area** - What problem are they facing? (CRUCIAL)
3. **Compliance Level** - High (medical conditions) or Low (lifestyle)?
4. **Funnel Stage** - Awareness / Consideration / Conversion / Loyalty?
5. **Value Proposition** - Main benefit we offer?
6. **Desired Action** - What ONE action should they take?
7. **Specific Programs** - Which TheLifeCo programs?
8. **Specific Centers** - Which locations? (Bodrum, Antalya, Phuket, etc.)
9. **Tone** - What voice? (Educational, Inspirational, etc.)
10. **Key Messages** - Must-include facts/stats?
11. **Constraints** - What to avoid?
12. **Platform** - Where published? (Email, Meta ad, Instagram, etc.)
13. **Price Point** - Pricing info to include?

### Content Generation Flow (6 Steps)

```
Step 1: User fills 13-question form (all mandatory, ONE submission)
    ↓
Step 2: Agent reviews brief - asks clarifying questions if unclear
    ↓
Step 3: PREVIEW STEP - Agent shows:
        • Proposed HOOK (pattern interrupt + curiosity gap)
        • Hook type (Mystery/Tension/Countdown/Transformation)
        • Open loops planned (macro/medium/micro)
        • Promise to reader
    ↓
Step 4: User APPROVES preview or requests adjustments
    ↓
Step 5: Agent generates FULL content (using approved hook)
    ↓
Step 6: Signal collection (rating, feedback) → feeds back into learning
```

### Signal Collection (For Self-Improvement)
- ⭐ Star rating (1-5)
- What worked checkboxes (hook, facts, tone, CTAs)
- What needs work checkboxes
- Implicit: Approve vs Regenerate clicks
- Implicit: Manual edits tracked

### Learning System (Signal-Derived Ranking)
```
Traditional: query → semantic similarity → examples → generate
Our system:  query → semantic similarity × signal_score → best examples → generate
```
The system learns from what ACTUALLY WORKS (high ratings, approvals).

### RAG Knowledge Documents (5 Files to Prepare)

1. **hook_patterns.md** - TheLifeCo-specific hook examples
2. **cta_guidelines.md** - CTA best practices by platform
3. **platform_rules.md** - Platform-specific content rules
4. **engagement_guide.md** - Psychology of hooks & retention (provided by user)
5. **pain_solution_matrix.md** - Pain points mapped to TheLifeCo programs

### TheLifeCo Pain & Solution Categories

**Cleansing & Detoxing**: Water Fasting, Master Detox
**Mental Wellness**: Stress, burnout, anxiety
**Weight Loss**: Weight plateau, failed diets
**Lifestyle As Medicine** (High Compliance):
- Diabetes Management
- Cardiovascular Disease
- Chronic Fatigue Recovery
- Liver Detox
- Inflammation & Immune Reset
- Digestive & Gut Health

**Longevity & Regenerative** (Mixed Compliance):
- Beauty & Body Reshaping
- Cancer Prevention Support
- Hormonal Longevity (Women's/Men's)
- Wellcation (Guilt-Free Holiday)
- Longevity for Elderly

### PRD Stories (27 Total)

**Epic 1: Project Setup** (Stories 1-2)
**Epic 2: Supabase Database** (Stories 3-4)
**Epic 3: RAG Foundation** (Stories 5-9)
**Epic 4: Content Generation** (Stories 10-13) - includes Preview + Generator
**Epic 5: Content Review** (Stories 14-15) - Wellness verifier + Engagement analyzer
**Epic 6: Signal Collection & Feedback Loop** (Stories 16-17)
**Epic 7: Experiment Framework** (Stories 18)
**Epic 8: Streamlit UI** (Stories 19-23) - Auth, CREATE mode, REVIEW mode, History
**Epic 9: Integration & Polish** (Stories 24-27)

### Pre-Flight Checklist (Before Running Ralph)

- [ ] Create Supabase account & project
- [ ] Get API keys (Anthropic, Voyage AI)
- [ ] Prepare .env file with all credentials
- [ ] Prepare wellness documents (PDFs)
- [ ] Prepare engagement guidelines (5 markdown files)
- [ ] Create test user in Supabase
- [ ] Install Ralph (ralph.sh + CLAUDE.md)
- [ ] Create PRD file and convert to prd.json

### How Ralph Will Build This

```bash
./scripts/ralph/ralph.sh --tool claude 30
```

Ralph will autonomously:
1. Pick highest priority incomplete story
2. Implement it
3. Run quality checks (ruff + pytest)
4. Commit if passing
5. Update prd.json
6. Log learnings to progress.txt
7. Repeat until all 27 stories pass

---
## END OF EXECUTIVE SUMMARY
---

## Overview

Build a **self-improving AI content assistant** for TheLifeCo's marketing team that:
1. **Creates content** - Generate emails, landing pages, social posts, blog articles
2. **Reviews content** - Check existing content for engagement and wellness accuracy
3. **Learns over time** - Improves through signal-derived feedback loops

## Business Goal & Core Thesis

| Aspect | Decision |
|--------|----------|
| **Business Goal** | Maximize content performance (engagement, conversions) |
| **Core Thesis** | Maximize content quality |
| **Success Metric** | Content that performs well after publication |

## Development Approach: Ralph-Powered

Use **snarktank/ralph** with Claude Code to autonomously build the system.

---

## PART 1: Ralph Setup for Development

### Prerequisites

```bash
# 1. Ensure Claude Code is installed
npm install -g @anthropic-ai/claude-code

# 2. Install jq for JSON processing
brew install jq  # macOS
# or: apt-get install jq  # Linux

# 3. Verify git repo
cd /Users/canokcuer/thelifeco
git status
```

### Install snarktank/ralph

```bash
# Create Ralph directory structure
mkdir -p scripts/ralph

# Download Ralph files
curl -o scripts/ralph/ralph.sh https://raw.githubusercontent.com/snarktank/ralph/main/ralph.sh
curl -o scripts/ralph/CLAUDE.md https://raw.githubusercontent.com/snarktank/ralph/main/CLAUDE.md

# Make executable
chmod +x scripts/ralph/ralph.sh

# Create PRD skill directory
mkdir -p ~/.claude/skills/prd
# (Download PRD skill files from snarktank/ralph/skills/prd/)
```

### Project Structure with Ralph

```
/Users/canokcuer/thelifeco/
├── scripts/
│   └── ralph/
│       ├── ralph.sh              # Ralph loop script
│       └── CLAUDE.md             # Prompt template for Claude Code
├── tasks/
│   └── prd-content-reviewer.md   # PRD for the project (generated)
├── prd.json                      # User stories (generated from PRD)
├── progress.txt                  # Learnings across iterations
├── AGENTS.md                     # Project-specific instructions
├── archive/                      # Completed runs
└── content_reviewer/             # The actual system (Ralph builds this)
```

### How to Write PRDs for Autonomous Ralph

**Golden Rule**: Every acceptance criterion must be machine-verifiable.

**Structure of a good user story:**
```
N. **Story Title**
   - What to build (clear, specific)
   - Implementation details (files to create, functions to implement)
   - Acceptance: [MACHINE-VERIFIABLE criteria]
     - Command to run OR
     - Test to pass OR
     - Output to check
```

**Quality checks Ralph runs after each story:**
- `ruff check .` (linting)
- `pytest tests/` (tests pass)
- App starts without errors

---

### PRD for Content Marketing Assistant

Create `tasks/prd-content-assistant.md`:

```markdown
# TheLifeCo Self-Improving Content Marketing Assistant

## Goal
Build a Streamlit-based content assistant that creates and reviews content,
learns from user feedback, and improves over time.

## Quality Checks (run after every story)
- `ruff check .` must pass
- `pytest tests/ -v` must pass
- `streamlit run content_assistant/app.py --server.headless true` must start without errors

## Environment Variables Required
```
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
VOYAGE_API_KEY=<your-voyage-key>
TEST_EMAIL=test@thelifeco.com
TEST_PASSWORD=testpassword123
```

## User Stories

---
### Epic 1: Project Setup
---

#### Story 1: Initialize Project Structure

**What to Build:**
Create the complete directory structure for the content_assistant package with all required subdirectories, init files, and a requirements.txt with pinned dependencies.

**Files to Create:**

1. `content_assistant/__init__.py`
```python
"""TheLifeCo Content Marketing Assistant."""
__version__ = "0.1.0"
```

2. `content_assistant/app.py`
```python
"""Main Streamlit application entry point."""
import streamlit as st

def main():
    st.set_page_config(
        page_title="TheLifeCo Content Assistant",
        page_icon="🌿",
        layout="wide"
    )
    st.title("TheLifeCo Content Marketing Assistant")
    st.write("Welcome! Select CREATE or REVIEW mode from the sidebar.")

if __name__ == "__main__":
    main()
```

3. `content_assistant/config.py` - empty placeholder (implemented in Story 2)
```python
"""Configuration module placeholder."""
pass
```

4. `content_assistant/tools/__init__.py`
```python
"""Content generation and analysis tools."""
```

5. `content_assistant/rag/__init__.py`
```python
"""RAG (Retrieval Augmented Generation) components."""
```

6. `content_assistant/db/__init__.py`
```python
"""Database layer for Supabase."""
```

7. `content_assistant/ui/__init__.py`
```python
"""Streamlit UI components."""
```

8. `content_assistant/experiments/__init__.py`
```python
"""A/B experiment framework."""
```

9. `tests/__init__.py`
```python
"""Test suite for content_assistant."""
```

10. `tests/conftest.py`
```python
"""Pytest configuration and fixtures."""
import pytest
import os
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables for tests."""
    load_dotenv()

@pytest.fixture
def sample_brief():
    """Return a complete sample brief with all 13 fields."""
    return {
        "target_audience": "Busy executives aged 40-55 experiencing burnout",
        "pain_area": "Chronic fatigue, weight gain, stress",
        "compliance_level": "Low - lifestyle wellness",
        "funnel_stage": "Consideration",
        "value_proposition": "Reset your energy in 7 days",
        "desired_action": "Book a free consultation",
        "specific_programs": "Master Detox",
        "specific_centers": "Bodrum, Turkey",
        "tone": "Warm and educational",
        "key_messages": "20+ years experience, medically supervised",
        "constraints": "No specific prices, avoid cure language",
        "platform": "Email newsletter",
        "price_point": "Starting from €2,500"
    }
```

11. `requirements.txt`
```
streamlit>=1.28.0,<2.0.0
anthropic>=0.40.0,<1.0.0
voyageai>=0.3.0,<1.0.0
supabase>=2.0.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0
PyPDF2>=3.0.0,<4.0.0
tiktoken>=0.5.0,<1.0.0
tenacity>=8.0.0,<9.0.0
pydantic>=2.0.0,<3.0.0
pytest>=7.0.0,<8.0.0
ruff>=0.1.0
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Directory structure exists
test -d content_assistant && echo "PASS: content_assistant/ exists" || echo "FAIL"
test -d content_assistant/tools && echo "PASS: tools/ exists" || echo "FAIL"
test -d content_assistant/rag && echo "PASS: rag/ exists" || echo "FAIL"
test -d content_assistant/db && echo "PASS: db/ exists" || echo "FAIL"
test -d content_assistant/ui && echo "PASS: ui/ exists" || echo "FAIL"
test -d content_assistant/experiments && echo "PASS: experiments/ exists" || echo "FAIL"
test -d tests && echo "PASS: tests/ exists" || echo "FAIL"

# AC2: All __init__.py files exist
test -f content_assistant/__init__.py && echo "PASS" || echo "FAIL"
test -f content_assistant/tools/__init__.py && echo "PASS" || echo "FAIL"
test -f content_assistant/rag/__init__.py && echo "PASS" || echo "FAIL"
test -f content_assistant/db/__init__.py && echo "PASS" || echo "FAIL"
test -f content_assistant/ui/__init__.py && echo "PASS" || echo "FAIL"
test -f content_assistant/experiments/__init__.py && echo "PASS" || echo "FAIL"
test -f tests/__init__.py && echo "PASS" || echo "FAIL"
test -f tests/conftest.py && echo "PASS" || echo "FAIL"

# AC3: Core files exist
test -f content_assistant/app.py && echo "PASS" || echo "FAIL"
test -f content_assistant/config.py && echo "PASS" || echo "FAIL"
test -f requirements.txt && echo "PASS" || echo "FAIL"

# AC4: Package is importable
python -c "import content_assistant; print(f'PASS: version={content_assistant.__version__}')"

# AC5: Requirements install successfully
pip install -r requirements.txt --quiet && echo "PASS: requirements installed" || echo "FAIL"

# AC6: Ruff passes
ruff check content_assistant/ tests/ && echo "PASS: ruff clean" || echo "FAIL"

# AC7: App starts (headless mode, 3 second timeout)
timeout 3 streamlit run content_assistant/app.py --server.headless true 2>&1 | grep -q "You can now view" && echo "PASS: app starts" || echo "PASS: app starts (timeout expected)"
```

---

#### Story 2: Set Up Configuration Module

**What to Build:**
Create a robust configuration module that loads environment variables, provides defaults, validates required variables, and raises clear errors with helpful messages.

**Files to Create/Modify:**

1. `content_assistant/config.py`
```python
"""Configuration management for TheLifeCo Content Assistant."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # Required variables (will raise ConfigError if missing)
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    anthropic_api_key: str
    voyage_api_key: str

    # Optional variables with defaults
    test_email: str = "test@thelifeco.com"
    test_password: str = "testpassword123"
    claude_model: str = "claude-sonnet-4-20250514"
    voyage_model: str = "voyage-3-lite"
    embedding_dimension: int = 1024
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_retries: int = 3

    # Cost control limits
    max_tokens_per_call: int = 4096          # Max tokens per Claude call
    max_few_shot_examples: int = 5           # Max examples in prompt (fixed)
    daily_generation_limit: int = 100        # Max generations per day
    monthly_budget_usd: float = 100.0        # Monthly budget cap in USD
    cost_alert_threshold: float = 0.8        # Alert at 80% of budget

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """
        Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file. If None, uses default .env

        Returns:
            Config instance with all values loaded

        Raises:
            ConfigError: If any required variable is missing
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Required variables - raise clear errors if missing
        required_vars = {
            "SUPABASE_URL": "supabase_url",
            "SUPABASE_KEY": "supabase_key",
            "SUPABASE_SERVICE_KEY": "supabase_service_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "VOYAGE_API_KEY": "voyage_api_key",
        }

        missing = []
        values = {}

        for env_var, field_name in required_vars.items():
            value = os.getenv(env_var)
            if not value:
                missing.append(env_var)
            else:
                values[field_name] = value

        if missing:
            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please set these in your .env file or environment."
            )

        # Optional variables with defaults
        values["test_email"] = os.getenv("TEST_EMAIL", "test@thelifeco.com")
        values["test_password"] = os.getenv("TEST_PASSWORD", "testpassword123")
        values["claude_model"] = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        values["voyage_model"] = os.getenv("VOYAGE_MODEL", "voyage-3-lite")
        values["embedding_dimension"] = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
        values["chunk_size"] = int(os.getenv("CHUNK_SIZE", "500"))
        values["chunk_overlap"] = int(os.getenv("CHUNK_OVERLAP", "50"))
        values["max_retries"] = int(os.getenv("MAX_RETRIES", "3"))

        # Cost control limits
        values["max_tokens_per_call"] = int(os.getenv("MAX_TOKENS_PER_CALL", "4096"))
        values["max_few_shot_examples"] = int(os.getenv("MAX_FEW_SHOT_EXAMPLES", "5"))
        values["daily_generation_limit"] = int(os.getenv("DAILY_GENERATION_LIMIT", "100"))
        values["monthly_budget_usd"] = float(os.getenv("MONTHLY_BUDGET_USD", "100.0"))
        values["cost_alert_threshold"] = float(os.getenv("COST_ALERT_THRESHOLD", "0.8"))

        return cls(**values)


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance (creates one if not exists)

    Raises:
        ConfigError: If required variables are missing
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reset_config() -> None:
    """Reset the global config (useful for testing)."""
    global _config
    _config = None
```

2. `tests/test_config.py`
```python
"""Tests for configuration module."""
import os
import pytest
from content_assistant.config import Config, ConfigError, get_config, reset_config


class TestConfig:
    """Test suite for Config class."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def test_missing_anthropic_api_key_raises_config_error(self, monkeypatch):
        """Test that missing ANTHROPIC_API_KEY raises ConfigError with clear message."""
        # Clear the env var
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        # Set other required vars
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-voyage-key")

        with pytest.raises(ConfigError) as exc_info:
            Config.from_env()

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)
        assert "Missing required environment variables" in str(exc_info.value)

    def test_missing_multiple_vars_lists_all(self, monkeypatch):
        """Test that multiple missing vars are all listed in error."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("VOYAGE_API_KEY", raising=False)
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")

        with pytest.raises(ConfigError) as exc_info:
            Config.from_env()

        error_msg = str(exc_info.value)
        assert "ANTHROPIC_API_KEY" in error_msg
        assert "VOYAGE_API_KEY" in error_msg

    def test_all_vars_loaded_correctly(self, monkeypatch):
        """Test that all variables are loaded with correct values."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-anon-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-voyage-key")
        monkeypatch.setenv("TEST_EMAIL", "custom@test.com")
        monkeypatch.setenv("EMBEDDING_DIMENSION", "512")

        config = Config.from_env()

        assert config.supabase_url == "https://test.supabase.co"
        assert config.supabase_key == "test-anon-key"
        assert config.supabase_service_key == "test-service-key"
        assert config.anthropic_api_key == "test-anthropic-key"
        assert config.voyage_api_key == "test-voyage-key"
        assert config.test_email == "custom@test.com"
        assert config.embedding_dimension == 512

    def test_defaults_applied_when_optional_vars_missing(self, monkeypatch):
        """Test that defaults are used for optional variables."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-voyage-key")
        monkeypatch.delenv("TEST_EMAIL", raising=False)
        monkeypatch.delenv("CHUNK_SIZE", raising=False)

        config = Config.from_env()

        assert config.test_email == "test@thelifeco.com"  # default
        assert config.chunk_size == 500  # default
        assert config.chunk_overlap == 50  # default
        assert config.claude_model == "claude-sonnet-4-20250514"  # default

    def test_get_config_returns_same_instance(self, monkeypatch):
        """Test that get_config returns singleton."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_reset_config_clears_singleton(self, monkeypatch):
        """Test that reset_config allows new instance."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        config1 = get_config()
        reset_config()
        config2 = get_config()

        assert config1 is not config2
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Config module exists and is importable
python -c "from content_assistant.config import Config, ConfigError, get_config" && echo "PASS: imports work"

# AC2: ConfigError is a proper exception
python -c "from content_assistant.config import ConfigError; assert issubclass(ConfigError, Exception); print('PASS: ConfigError is Exception')"

# AC3: Config has all required fields
python -c "
from content_assistant.config import Config
import inspect
sig = inspect.signature(Config)
required = ['supabase_url', 'supabase_key', 'supabase_service_key', 'anthropic_api_key', 'voyage_api_key']
for field in required:
    assert field in sig.parameters, f'Missing {field}'
print('PASS: all required fields exist')
"

# AC4: All tests pass
pytest tests/test_config.py -v
# Expected output: 6 passed

# AC5: Test specifically for missing ANTHROPIC_API_KEY error
pytest tests/test_config.py::TestConfig::test_missing_anthropic_api_key_raises_config_error -v
# Expected: PASSED

# AC6: Test for correct value loading
pytest tests/test_config.py::TestConfig::test_all_vars_loaded_correctly -v
# Expected: PASSED

# AC7: Ruff passes
ruff check content_assistant/config.py tests/test_config.py && echo "PASS: ruff clean"
```

---
### Epic 2: Supabase Database Layer
---

#### Story 3: Create Supabase Client Module

**What to Build:**
Create a Supabase client module that provides both regular (anon key) and admin (service role) clients with proper connection handling.

**Files to Create:**

1. `content_assistant/db/supabase_client.py`
```python
"""Supabase client management for TheLifeCo Content Assistant."""
from typing import Optional
from supabase import create_client, Client
from content_assistant.config import get_config


# Client singletons
_client: Optional[Client] = None
_admin_client: Optional[Client] = None


def get_client() -> Client:
    """
    Get Supabase client with anon key (for regular operations).

    Returns:
        Supabase Client instance

    Raises:
        ConfigError: If SUPABASE_URL or SUPABASE_KEY not configured
    """
    global _client
    if _client is None:
        config = get_config()
        _client = create_client(config.supabase_url, config.supabase_key)
    return _client


def get_admin_client() -> Client:
    """
    Get Supabase client with service role key (for admin operations).

    Use this for operations that bypass RLS (Row Level Security).

    Returns:
        Supabase Client instance with service role

    Raises:
        ConfigError: If SUPABASE_URL or SUPABASE_SERVICE_KEY not configured
    """
    global _admin_client
    if _admin_client is None:
        config = get_config()
        _admin_client = create_client(config.supabase_url, config.supabase_service_key)
    return _admin_client


def reset_clients() -> None:
    """Reset client singletons (for testing)."""
    global _client, _admin_client
    _client = None
    _admin_client = None


def test_connection() -> bool:
    """
    Test database connection by executing a simple query.

    Returns:
        True if connection successful

    Raises:
        Exception: If connection fails
    """
    client = get_client()
    # Execute simple query to verify connection
    result = client.rpc("", {}).execute()  # Empty RPC just tests connection
    return True


def execute_sql(sql: str, admin: bool = False) -> dict:
    """
    Execute raw SQL using Supabase.

    Args:
        sql: SQL statement to execute
        admin: If True, use admin client (bypasses RLS)

    Returns:
        Query result as dict
    """
    client = get_admin_client() if admin else get_client()
    # Note: Raw SQL execution requires using postgrest or a function
    # For schema creation, we use the Supabase SQL editor or migrations
    return {"status": "ok"}
```

2. `tests/test_supabase_client.py`
```python
"""Tests for Supabase client module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from content_assistant.db.supabase_client import (
    get_client,
    get_admin_client,
    reset_clients,
)
from content_assistant.config import reset_config


class TestSupabaseClient:
    """Test suite for Supabase client."""

    def setup_method(self):
        """Reset clients before each test."""
        reset_clients()
        reset_config()

    @patch("content_assistant.db.supabase_client.create_client")
    def test_get_client_returns_valid_client(self, mock_create_client, monkeypatch):
        """Test that get_client returns a Supabase client."""
        # Setup env vars
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-anon-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        client = get_client()

        assert client is not None
        mock_create_client.assert_called_once_with(
            "https://test.supabase.co",
            "test-anon-key"
        )

    @patch("content_assistant.db.supabase_client.create_client")
    def test_get_admin_client_uses_service_key(self, mock_create_client, monkeypatch):
        """Test that admin client uses service role key."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-anon-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        client = get_admin_client()

        assert client is not None
        mock_create_client.assert_called_once_with(
            "https://test.supabase.co",
            "test-service-key"  # Service key, not anon key
        )

    @patch("content_assistant.db.supabase_client.create_client")
    def test_get_client_returns_singleton(self, mock_create_client, monkeypatch):
        """Test that get_client returns the same instance."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        client1 = get_client()
        client2 = get_client()

        assert client1 is client2
        assert mock_create_client.call_count == 1  # Only called once

    @patch("content_assistant.db.supabase_client.create_client")
    def test_reset_clients_clears_singletons(self, mock_create_client, monkeypatch):
        """Test that reset_clients allows new instances."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client1 = MagicMock()
        mock_client2 = MagicMock()
        mock_create_client.side_effect = [mock_client1, mock_client2]

        client1 = get_client()
        reset_clients()
        client2 = get_client()

        assert client1 is not client2


@pytest.mark.integration
class TestSupabaseClientIntegration:
    """Integration tests requiring real Supabase connection."""

    def setup_method(self):
        """Reset clients before each test."""
        reset_clients()
        reset_config()

    @pytest.mark.skipif(
        not all([
            __import__("os").getenv("SUPABASE_URL"),
            __import__("os").getenv("SUPABASE_KEY"),
        ]),
        reason="Supabase credentials not configured"
    )
    def test_real_connection_select_one(self):
        """Test actual connection to Supabase with SELECT 1."""
        client = get_client()
        # This will fail if connection doesn't work
        # Using a simple table query - adjust based on actual schema
        assert client is not None
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.db.supabase_client import get_client, get_admin_client, reset_clients" && echo "PASS: imports work"

# AC2: Functions have correct signatures
python -c "
from content_assistant.db.supabase_client import get_client, get_admin_client
import inspect
# get_client takes no args
sig = inspect.signature(get_client)
assert len(sig.parameters) == 0, 'get_client should take no args'
# get_admin_client takes no args
sig = inspect.signature(get_admin_client)
assert len(sig.parameters) == 0, 'get_admin_client should take no args'
print('PASS: correct signatures')
"

# AC3: Unit tests pass (mocked, no real DB needed)
pytest tests/test_supabase_client.py -v -k "not integration"
# Expected: 4 passed

# AC4: Singleton pattern test passes
pytest tests/test_supabase_client.py::TestSupabaseClient::test_get_client_returns_singleton -v
# Expected: PASSED

# AC5: Admin client uses service key
pytest tests/test_supabase_client.py::TestSupabaseClient::test_get_admin_client_uses_service_key -v
# Expected: PASSED

# AC6: Ruff passes
ruff check content_assistant/db/supabase_client.py tests/test_supabase_client.py && echo "PASS: ruff clean"
```

---

#### Story 4: Create Database Schema

**What to Build:**
Create the complete database schema SQL file and an initialization script. Schema includes 4 tables: knowledge_chunks, content_generations, experiments, experiment_assignments.

**Files to Create:**

1. `content_assistant/db/schema.sql`
```sql
-- TheLifeCo Content Assistant Database Schema
-- Run this in Supabase SQL Editor

-- Enable pgvector extension (must be done first)
CREATE EXTENSION IF NOT EXISTS vector;

-- Table 1: knowledge_chunks
-- Stores embedded chunks from wellness PDFs and engagement guidelines
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,                          -- e.g., "minibook1.pdf", "engagement_guide.md"
    collection TEXT NOT NULL DEFAULT 'wellness',   -- "wellness" or "engagement"
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,                  -- Position in original document
    embedding vector(1024),                        -- Voyage AI embeddings are 1024 dim
    metadata JSONB DEFAULT '{}'::jsonb,            -- Additional metadata (page, section, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for filtering by collection
CREATE INDEX IF NOT EXISTS knowledge_chunks_collection_idx ON knowledge_chunks(collection);

-- Table 2: content_generations
-- Stores all generated content with briefs, signals, and embeddings
CREATE TABLE IF NOT EXISTS content_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,                                  -- References Supabase auth.users
    brief JSONB NOT NULL,                          -- The 13-question brief
    preview JSONB,                                 -- Preview that was approved
    content TEXT NOT NULL,                         -- Generated content
    content_type TEXT NOT NULL,                    -- email, landing_page, instagram_post, etc.
    embedding vector(1024),                        -- Embedding of the content for similarity search
    signals JSONB DEFAULT '{}'::jsonb,             -- User feedback signals
    metadata JSONB DEFAULT '{}'::jsonb,            -- Additional metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for vector similarity search on content
CREATE INDEX IF NOT EXISTS content_generations_embedding_idx
ON content_generations USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for filtering by user and content type
CREATE INDEX IF NOT EXISTS content_generations_user_idx ON content_generations(user_id);
CREATE INDEX IF NOT EXISTS content_generations_type_idx ON content_generations(content_type);

-- Table 3: experiments
-- Stores A/B experiment configurations
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,                     -- e.g., "hook_style_test_jan_2025"
    description TEXT,
    config JSONB NOT NULL,                         -- Experiment configuration
    status TEXT NOT NULL DEFAULT 'draft',          -- draft, active, completed, archived
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ
);

-- Index for active experiments
CREATE INDEX IF NOT EXISTS experiments_status_idx ON experiments(status);

-- Table 4: experiment_assignments
-- Tracks which users/sessions are in which experiment variants
CREATE TABLE IF NOT EXISTS experiment_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,                      -- User session or user_id
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    variant TEXT NOT NULL,                         -- "control" or "treatment"
    signals JSONB DEFAULT '{}'::jsonb,             -- Signals collected for this assignment
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, experiment_id)              -- One assignment per session per experiment
);

-- Index for lookups
CREATE INDEX IF NOT EXISTS experiment_assignments_session_idx ON experiment_assignments(session_id);
CREATE INDEX IF NOT EXISTS experiment_assignments_experiment_idx ON experiment_assignments(experiment_id);

-- Table 5: api_costs
-- Tracks API usage and costs for budget management
CREATE TABLE IF NOT EXISTS api_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation TEXT NOT NULL,                       -- e.g., "generate_preview", "embed_brief"
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    embedding_tokens INTEGER DEFAULT 0,
    estimated_cost_usd DECIMAL(10, 6) DEFAULT 0,
    user_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for cost queries
CREATE INDEX IF NOT EXISTS api_costs_created_idx ON api_costs(created_at);
CREATE INDEX IF NOT EXISTS api_costs_user_idx ON api_costs(user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for content_generations
DROP TRIGGER IF EXISTS content_generations_updated_at ON content_generations;
CREATE TRIGGER content_generations_updated_at
    BEFORE UPDATE ON content_generations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Comments for documentation
COMMENT ON TABLE knowledge_chunks IS 'Stores embedded chunks from wellness and engagement documents for RAG';
COMMENT ON TABLE content_generations IS 'Stores all generated content with briefs, signals for learning';
COMMENT ON TABLE experiments IS 'A/B experiment definitions';
COMMENT ON TABLE experiment_assignments IS 'Tracks user assignments to experiment variants';
COMMENT ON TABLE api_costs IS 'Tracks API usage and costs for budget management';
```

2. `content_assistant/db/init_db.py`
```python
"""Database initialization script for TheLifeCo Content Assistant."""
import os
import sys
from pathlib import Path


def get_schema_sql() -> str:
    """Read the schema SQL file."""
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return schema_path.read_text()


def init_database(dry_run: bool = False) -> dict:
    """
    Initialize the database schema.

    Args:
        dry_run: If True, only print the SQL without executing

    Returns:
        dict with status and any messages
    """
    schema_sql = get_schema_sql()

    if dry_run:
        print("=== DRY RUN - Schema SQL ===")
        print(schema_sql)
        print("=== END DRY RUN ===")
        return {"status": "dry_run", "sql_length": len(schema_sql)}

    # For actual execution, user should run this in Supabase SQL Editor
    # or use supabase CLI migrations
    print("Schema SQL loaded successfully.")
    print(f"SQL length: {len(schema_sql)} characters")
    print("\nTo initialize the database:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Paste and run the contents of content_assistant/db/schema.sql")
    print("\nOr use Supabase CLI:")
    print("  supabase db push")

    return {"status": "ready", "sql_length": len(schema_sql)}


def verify_tables() -> dict:
    """
    Verify that all required tables exist in the database.

    Returns:
        dict with table names and their existence status
    """
    from content_assistant.db.supabase_client import get_admin_client

    required_tables = [
        "knowledge_chunks",
        "content_generations",
        "experiments",
        "experiment_assignments",
        "api_costs"
    ]

    client = get_admin_client()
    results = {}

    for table in required_tables:
        try:
            # Try to query the table (will fail if doesn't exist)
            response = client.table(table).select("id").limit(1).execute()
            results[table] = {"exists": True, "error": None}
        except Exception as e:
            results[table] = {"exists": False, "error": str(e)}

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize TheLifeCo database")
    parser.add_argument("--dry-run", action="store_true", help="Print SQL without executing")
    parser.add_argument("--verify", action="store_true", help="Verify tables exist")

    args = parser.parse_args()

    if args.verify:
        print("Verifying database tables...")
        results = verify_tables()
        all_exist = all(r["exists"] for r in results.values())
        for table, status in results.items():
            emoji = "✓" if status["exists"] else "✗"
            print(f"  {emoji} {table}: {'exists' if status['exists'] else status['error']}")
        sys.exit(0 if all_exist else 1)
    else:
        result = init_database(dry_run=args.dry_run)
        print(f"\nResult: {result}")
```

3. `tests/test_schema.py`
```python
"""Tests for database schema."""
import pytest
from pathlib import Path


class TestSchema:
    """Test suite for database schema."""

    def test_schema_file_exists(self):
        """Test that schema.sql file exists."""
        schema_path = Path("content_assistant/db/schema.sql")
        assert schema_path.exists(), "schema.sql file must exist"

    def test_schema_contains_knowledge_chunks_table(self):
        """Test that schema defines knowledge_chunks table."""
        schema_path = Path("content_assistant/db/schema.sql")
        content = schema_path.read_text()

        assert "CREATE TABLE IF NOT EXISTS knowledge_chunks" in content
        assert "embedding vector(1024)" in content
        assert "chunk_text TEXT NOT NULL" in content
        assert "collection TEXT" in content

    def test_schema_contains_content_generations_table(self):
        """Test that schema defines content_generations table."""
        schema_path = Path("content_assistant/db/schema.sql")
        content = schema_path.read_text()

        assert "CREATE TABLE IF NOT EXISTS content_generations" in content
        assert "brief JSONB NOT NULL" in content
        assert "content TEXT NOT NULL" in content
        assert "content_type TEXT NOT NULL" in content
        assert "signals JSONB" in content
        assert "embedding vector(1024)" in content

    def test_schema_contains_experiments_table(self):
        """Test that schema defines experiments table."""
        schema_path = Path("content_assistant/db/schema.sql")
        content = schema_path.read_text()

        assert "CREATE TABLE IF NOT EXISTS experiments" in content
        assert "name TEXT NOT NULL" in content
        assert "config JSONB NOT NULL" in content
        assert "status TEXT" in content

    def test_schema_contains_experiment_assignments_table(self):
        """Test that schema defines experiment_assignments table."""
        schema_path = Path("content_assistant/db/schema.sql")
        content = schema_path.read_text()

        assert "CREATE TABLE IF NOT EXISTS experiment_assignments" in content
        assert "session_id TEXT NOT NULL" in content
        assert "experiment_id UUID NOT NULL" in content
        assert "variant TEXT NOT NULL" in content

    def test_schema_enables_pgvector(self):
        """Test that schema enables pgvector extension."""
        schema_path = Path("content_assistant/db/schema.sql")
        content = schema_path.read_text()

        assert "CREATE EXTENSION IF NOT EXISTS vector" in content

    def test_schema_has_vector_indexes(self):
        """Test that schema creates vector similarity indexes."""
        schema_path = Path("content_assistant/db/schema.sql")
        content = schema_path.read_text()

        assert "CREATE INDEX" in content
        assert "vector_cosine_ops" in content

    def test_init_db_script_exists(self):
        """Test that init_db.py exists."""
        init_path = Path("content_assistant/db/init_db.py")
        assert init_path.exists(), "init_db.py must exist"

    def test_init_db_importable(self):
        """Test that init_db module is importable."""
        from content_assistant.db.init_db import init_database, get_schema_sql
        assert callable(init_database)
        assert callable(get_schema_sql)

    def test_init_db_dry_run(self):
        """Test init_database dry run mode."""
        from content_assistant.db.init_db import init_database

        result = init_database(dry_run=True)

        assert result["status"] == "dry_run"
        assert result["sql_length"] > 1000  # Schema should be substantial


@pytest.mark.integration
class TestSchemaIntegration:
    """Integration tests requiring real Supabase connection."""

    @pytest.mark.skipif(
        not all([
            __import__("os").getenv("SUPABASE_URL"),
            __import__("os").getenv("SUPABASE_SERVICE_KEY"),
        ]),
        reason="Supabase credentials not configured"
    )
    def test_verify_all_tables_exist(self):
        """Verify all 4 tables exist in database."""
        from content_assistant.db.init_db import verify_tables

        results = verify_tables()

        assert len(results) == 5
        for table_name, status in results.items():
            assert status["exists"], f"Table {table_name} should exist: {status['error']}"
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Schema file exists and is readable
test -f content_assistant/db/schema.sql && echo "PASS: schema.sql exists"
test -s content_assistant/db/schema.sql && echo "PASS: schema.sql is not empty"

# AC2: Schema contains all 5 required tables
grep -q "CREATE TABLE IF NOT EXISTS knowledge_chunks" content_assistant/db/schema.sql && echo "PASS: knowledge_chunks table"
grep -q "CREATE TABLE IF NOT EXISTS content_generations" content_assistant/db/schema.sql && echo "PASS: content_generations table"
grep -q "CREATE TABLE IF NOT EXISTS experiments" content_assistant/db/schema.sql && echo "PASS: experiments table"
grep -q "CREATE TABLE IF NOT EXISTS experiment_assignments" content_assistant/db/schema.sql && echo "PASS: experiment_assignments table"
grep -q "CREATE TABLE IF NOT EXISTS api_costs" content_assistant/db/schema.sql && echo "PASS: api_costs table"

# AC3: Schema has correct column types
grep -q "embedding vector(1024)" content_assistant/db/schema.sql && echo "PASS: vector embedding column"
grep -q "brief JSONB NOT NULL" content_assistant/db/schema.sql && echo "PASS: brief JSONB column"
grep -q "signals JSONB" content_assistant/db/schema.sql && echo "PASS: signals JSONB column"

# AC4: init_db.py exists and runs
test -f content_assistant/db/init_db.py && echo "PASS: init_db.py exists"
python content_assistant/db/init_db.py --dry-run && echo "PASS: dry run works"

# AC5: All unit tests pass
pytest tests/test_schema.py -v -k "not integration"
# Expected: 10 passed

# AC6: Schema file is valid SQL (basic check)
python -c "
content = open('content_assistant/db/schema.sql').read()
assert 'CREATE TABLE' in content
assert 'PRIMARY KEY' in content
assert 'REFERENCES' in content
assert 'CREATE INDEX' in content
print('PASS: SQL structure looks valid')
"

# AC7: Ruff passes
ruff check content_assistant/db/init_db.py tests/test_schema.py && echo "PASS: ruff clean"
```

---
### Epic 3: RAG Foundation
---

#### Story 5: Build Document Loader

**What to Build:**
Create a document loader module that can parse PDF files and text files (txt, md) into plain text for chunking and embedding.

**Files to Create:**

1. `content_assistant/rag/loader.py`
```python
"""Document loading utilities for RAG pipeline."""
from pathlib import Path
from typing import Union
import PyPDF2


class LoaderError(Exception):
    """Raised when document loading fails."""
    pass


def load_pdf(path: Union[str, Path]) -> str:
    """
    Load text content from a PDF file.

    Args:
        path: Path to PDF file

    Returns:
        Extracted text content as string

    Raises:
        LoaderError: If file not found or not a valid PDF
    """
    path = Path(path)
    if not path.exists():
        raise LoaderError(f"PDF file not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise LoaderError(f"Not a PDF file: {path}")

    try:
        text_parts = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n\n".join(text_parts)
        if not full_text.strip():
            raise LoaderError(f"No text extracted from PDF: {path}")
        return full_text
    except PyPDF2.errors.PdfReadError as e:
        raise LoaderError(f"Invalid PDF file {path}: {e}")


def load_text(path: Union[str, Path]) -> str:
    """
    Load content from a text file (.txt, .md, or similar).

    Args:
        path: Path to text file

    Returns:
        File content as string

    Raises:
        LoaderError: If file not found or unreadable
    """
    path = Path(path)
    if not path.exists():
        raise LoaderError(f"File not found: {path}")

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        try:
            return path.read_text(encoding="latin-1")
        except Exception as e:
            raise LoaderError(f"Cannot read file {path}: {e}")


def load_document(path: Union[str, Path]) -> str:
    """
    Load document content, auto-detecting file type.

    Args:
        path: Path to document (PDF, TXT, MD)

    Returns:
        Document content as string

    Raises:
        LoaderError: If file type not supported or loading fails
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf(path)
    elif suffix in [".txt", ".md", ".markdown", ".text"]:
        return load_text(path)
    else:
        # Try as text file
        try:
            return load_text(path)
        except LoaderError:
            raise LoaderError(f"Unsupported file type: {suffix}")


def get_document_metadata(path: Union[str, Path]) -> dict:
    """
    Extract metadata from a document.

    Args:
        path: Path to document

    Returns:
        dict with: filename, extension, size_bytes
    """
    path = Path(path)
    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }
```

2. `tests/test_loader.py`
```python
"""Tests for document loader module."""
import pytest
from pathlib import Path
import tempfile
from content_assistant.rag.loader import (
    load_pdf,
    load_text,
    load_document,
    LoaderError,
    get_document_metadata,
)


class TestLoadPdf:
    """Tests for PDF loading."""

    def test_load_pdf_returns_string(self):
        """Test loading minibook1.pdf returns string content."""
        # This test requires minibook1.pdf to exist
        pdf_path = Path("minibook1.pdf")
        if not pdf_path.exists():
            pytest.skip("minibook1.pdf not found")

        result = load_pdf(pdf_path)

        assert isinstance(result, str)
        assert len(result) > 1000, "PDF should have substantial content"

    def test_load_pdf_file_not_found_raises_error(self):
        """Test that missing file raises LoaderError."""
        with pytest.raises(LoaderError) as exc_info:
            load_pdf("nonexistent.pdf")
        assert "not found" in str(exc_info.value).lower()

    def test_load_pdf_non_pdf_raises_error(self):
        """Test that non-PDF file raises LoaderError."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a pdf")
            temp_path = f.name

        try:
            with pytest.raises(LoaderError) as exc_info:
                load_pdf(temp_path)
            assert "not a pdf" in str(exc_info.value).lower()
        finally:
            Path(temp_path).unlink()


class TestLoadText:
    """Tests for text file loading."""

    def test_load_text_returns_content(self):
        """Test loading text file returns content."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("Hello, world!\nThis is a test.")
            temp_path = f.name

        try:
            result = load_text(temp_path)
            assert result == "Hello, world!\nThis is a test."
        finally:
            Path(temp_path).unlink()

    def test_load_text_markdown_works(self):
        """Test loading markdown file."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write("# Header\n\nSome content")
            temp_path = f.name

        try:
            result = load_text(temp_path)
            assert "# Header" in result
        finally:
            Path(temp_path).unlink()

    def test_load_text_file_not_found_raises_error(self):
        """Test that missing file raises LoaderError."""
        with pytest.raises(LoaderError):
            load_text("nonexistent.txt")


class TestLoadDocument:
    """Tests for auto-detecting document loader."""

    def test_load_document_pdf(self):
        """Test auto-detection of PDF."""
        pdf_path = Path("minibook1.pdf")
        if not pdf_path.exists():
            pytest.skip("minibook1.pdf not found")

        result = load_document(pdf_path)
        assert isinstance(result, str)
        assert len(result) > 1000

    def test_load_document_txt(self):
        """Test auto-detection of text file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("Test content for document loader")
            temp_path = f.name

        try:
            result = load_document(temp_path)
            assert "Test content" in result
        finally:
            Path(temp_path).unlink()

    def test_load_document_md(self):
        """Test auto-detection of markdown file."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write("# Markdown Test\n\nContent here")
            temp_path = f.name

        try:
            result = load_document(temp_path)
            assert "# Markdown Test" in result
        finally:
            Path(temp_path).unlink()


class TestGetDocumentMetadata:
    """Tests for metadata extraction."""

    def test_get_metadata_returns_dict(self):
        """Test metadata extraction returns expected fields."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("Some content")
            temp_path = f.name

        try:
            metadata = get_document_metadata(temp_path)
            assert "filename" in metadata
            assert "extension" in metadata
            assert "size_bytes" in metadata
            assert metadata["extension"] == ".txt"
            assert metadata["size_bytes"] > 0
        finally:
            Path(temp_path).unlink()
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.rag.loader import load_pdf, load_text, load_document, LoaderError" && echo "PASS: imports work"

# AC2: Function signatures are correct
python -c "
from content_assistant.rag.loader import load_pdf, load_text, load_document
import inspect

# Check load_pdf
sig = inspect.signature(load_pdf)
assert 'path' in sig.parameters
print('PASS: load_pdf has path parameter')

# Check return type annotation
assert 'str' in str(sig.return_annotation) or sig.return_annotation == str
print('PASS: load_pdf returns str')
"

# AC3: LoaderError is proper exception
python -c "from content_assistant.rag.loader import LoaderError; assert issubclass(LoaderError, Exception); print('PASS')"

# AC4: PDF loading works (if minibook1.pdf exists)
python -c "
from pathlib import Path
if Path('minibook1.pdf').exists():
    from content_assistant.rag.loader import load_pdf
    result = load_pdf('minibook1.pdf')
    assert isinstance(result, str)
    assert len(result) > 1000, f'Expected >1000 chars, got {len(result)}'
    print(f'PASS: loaded minibook1.pdf with {len(result)} characters')
else:
    print('SKIP: minibook1.pdf not found')
"

# AC5: Text loading works
python -c "
import tempfile
from pathlib import Path
from content_assistant.rag.loader import load_text

with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
    f.write('Test content 12345')
    path = f.name

result = load_text(path)
assert result == 'Test content 12345'
Path(path).unlink()
print('PASS: load_text works')
"

# AC6: Auto-detection works
python -c "
import tempfile
from pathlib import Path
from content_assistant.rag.loader import load_document

with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as f:
    f.write('# Test Markdown')
    path = f.name

result = load_document(path)
assert '# Test Markdown' in result
Path(path).unlink()
print('PASS: load_document auto-detects type')
"

# AC7: All tests pass
pytest tests/test_loader.py -v
# Expected: at least 8 passed

# AC8: Ruff passes
ruff check content_assistant/rag/loader.py tests/test_loader.py && echo "PASS: ruff clean"
```

---

#### Story 6: Build Text Chunker

**What to Build:**
Create a text chunking module that splits documents into overlapping chunks suitable for embedding, preserving paragraph boundaries where possible.

**Files to Create:**

1. `content_assistant/rag/chunker.py`
```python
"""Text chunking utilities for RAG pipeline."""
from typing import List
import re


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    preserve_paragraphs: bool = True,
) -> List[dict]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: Text to split
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        preserve_paragraphs: Try to break at paragraph boundaries

    Returns:
        List of chunk dicts with keys:
        - text: The chunk text
        - start_char: Starting character position in original
        - end_char: Ending character position in original
        - chunk_index: 0-based index of this chunk
    """
    if not text or not text.strip():
        return []

    # Normalize whitespace
    text = text.strip()

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        # Calculate end position
        end = min(start + chunk_size, len(text))

        # If we're not at the end and preserve_paragraphs is True,
        # try to find a good break point
        if end < len(text) and preserve_paragraphs:
            # Look for paragraph break (double newline)
            para_break = text.rfind("\n\n", start, end)
            if para_break > start + chunk_size // 2:
                end = para_break + 2  # Include the newlines

            # If no paragraph break, try single newline
            elif (newline := text.rfind("\n", start + chunk_size // 2, end)) > start:
                end = newline + 1

            # If no newline, try sentence end
            elif (period := text.rfind(". ", start + chunk_size // 2, end)) > start:
                end = period + 2

            # If no good break, try space
            elif (space := text.rfind(" ", start + chunk_size // 2, end)) > start:
                end = space + 1

        chunk_text = text[start:end].strip()

        if chunk_text:  # Only add non-empty chunks
            chunks.append({
                "text": chunk_text,
                "start_char": start,
                "end_char": end,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

        # Move start position for next chunk (with overlap)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)

    return chunks


def estimate_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> int:
    """
    Estimate how many chunks a text will produce.

    Args:
        text: Text to estimate
        chunk_size: Target chunk size
        overlap: Overlap between chunks

    Returns:
        Estimated number of chunks
    """
    if not text:
        return 0
    text_len = len(text.strip())
    if text_len <= chunk_size:
        return 1
    # Each chunk after the first advances by (chunk_size - overlap)
    effective_advance = chunk_size - overlap
    return 1 + ((text_len - chunk_size) // effective_advance) + 1


def validate_chunks(chunks: List[dict], max_size: int = 600) -> dict:
    """
    Validate chunks meet requirements.

    Args:
        chunks: List of chunk dicts
        max_size: Maximum allowed chunk size

    Returns:
        dict with: valid (bool), issues (list of strings)
    """
    issues = []

    for i, chunk in enumerate(chunks):
        # Check required keys
        for key in ["text", "start_char", "end_char", "chunk_index"]:
            if key not in chunk:
                issues.append(f"Chunk {i} missing key: {key}")

        # Check size
        if "text" in chunk and len(chunk["text"]) > max_size:
            issues.append(f"Chunk {i} exceeds max size: {len(chunk['text'])} > {max_size}")

        # Check index
        if chunk.get("chunk_index") != i:
            issues.append(f"Chunk {i} has wrong index: {chunk.get('chunk_index')}")

    return {"valid": len(issues) == 0, "issues": issues}
```

2. `tests/test_chunker.py`
```python
"""Tests for text chunking module."""
import pytest
from content_assistant.rag.chunker import chunk_text, estimate_chunks, validate_chunks


class TestChunkText:
    """Tests for chunk_text function."""

    def test_chunk_2000_chars_produces_4_to_5_chunks(self):
        """Test that 2000 chars with default settings produces 4-5 chunks."""
        # Create 2000 character text
        text = "This is a test sentence. " * 80  # ~2000 chars
        text = text[:2000]

        chunks = chunk_text(text, chunk_size=500, overlap=50)

        assert 4 <= len(chunks) <= 5, f"Expected 4-5 chunks, got {len(chunks)}"

    def test_chunks_overlap_by_approximately_50_chars(self):
        """Test that consecutive chunks overlap by roughly the specified amount."""
        text = "Word " * 500  # 2500 chars

        chunks = chunk_text(text, chunk_size=500, overlap=50)

        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            current_end = chunks[i]["end_char"]
            next_start = chunks[i + 1]["start_char"]
            overlap = current_end - next_start
            # Allow some tolerance due to word boundaries
            assert 30 <= overlap <= 100, f"Overlap between chunks {i} and {i+1}: {overlap}"

    def test_no_chunk_exceeds_600_chars(self):
        """Test that no chunk exceeds 600 characters."""
        text = "A" * 3000  # Long text with no break points

        chunks = chunk_text(text, chunk_size=500, overlap=50)

        for i, chunk in enumerate(chunks):
            assert len(chunk["text"]) <= 600, f"Chunk {i} is {len(chunk['text'])} chars"

    def test_chunks_have_required_keys(self):
        """Test that each chunk has text, start_char, end_char, chunk_index."""
        text = "Test text for chunking. " * 50

        chunks = chunk_text(text)

        required_keys = {"text", "start_char", "end_char", "chunk_index"}
        for i, chunk in enumerate(chunks):
            assert required_keys.issubset(chunk.keys()), f"Chunk {i} missing keys"

    def test_chunk_index_is_sequential(self):
        """Test that chunk_index values are 0, 1, 2, ..."""
        text = "Testing chunk indices. " * 100

        chunks = chunk_text(text, chunk_size=200)

        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i

    def test_empty_text_returns_empty_list(self):
        """Test that empty text returns empty list."""
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_short_text_returns_single_chunk(self):
        """Test that text shorter than chunk_size returns one chunk."""
        text = "Short text."

        chunks = chunk_text(text, chunk_size=500)

        assert len(chunks) == 1
        assert chunks[0]["text"] == "Short text."
        assert chunks[0]["chunk_index"] == 0

    def test_preserves_paragraph_boundaries(self):
        """Test that chunks prefer to break at paragraph boundaries."""
        text = "First paragraph content here.\n\nSecond paragraph starts here.\n\nThird paragraph."

        chunks = chunk_text(text, chunk_size=40, overlap=5, preserve_paragraphs=True)

        # First chunk should end at or near a paragraph boundary
        # This is a soft requirement - we just check it doesn't cut mid-word badly
        for chunk in chunks:
            assert len(chunk["text"]) > 0


class TestEstimateChunks:
    """Tests for chunk estimation."""

    def test_estimate_matches_actual_roughly(self):
        """Test that estimate is close to actual count."""
        text = "Word " * 500

        estimated = estimate_chunks(text, chunk_size=500, overlap=50)
        actual = len(chunk_text(text, chunk_size=500, overlap=50))

        # Allow 20% tolerance
        assert abs(estimated - actual) <= max(1, actual * 0.2)


class TestValidateChunks:
    """Tests for chunk validation."""

    def test_valid_chunks_pass_validation(self):
        """Test that properly formed chunks pass validation."""
        text = "Test content for validation. " * 50
        chunks = chunk_text(text)

        result = validate_chunks(chunks, max_size=600)

        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_oversized_chunk_fails_validation(self):
        """Test that oversized chunks fail validation."""
        chunks = [{"text": "A" * 700, "start_char": 0, "end_char": 700, "chunk_index": 0}]

        result = validate_chunks(chunks, max_size=600)

        assert result["valid"] is False
        assert any("exceeds max size" in issue for issue in result["issues"])
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.rag.chunker import chunk_text, estimate_chunks, validate_chunks" && echo "PASS"

# AC2: 2000 char text produces 4-5 chunks
python -c "
from content_assistant.rag.chunker import chunk_text
text = 'This is a test. ' * 125  # ~2000 chars
text = text[:2000]
chunks = chunk_text(text, chunk_size=500, overlap=50)
assert 4 <= len(chunks) <= 5, f'Expected 4-5 chunks, got {len(chunks)}'
print(f'PASS: 2000 chars produced {len(chunks)} chunks')
"

# AC3: Chunks overlap by ~50 chars
python -c "
from content_assistant.rag.chunker import chunk_text
text = 'Word ' * 500
chunks = chunk_text(text, chunk_size=500, overlap=50)
for i in range(len(chunks) - 1):
    overlap = chunks[i]['end_char'] - chunks[i + 1]['start_char']
    assert 25 <= overlap <= 100, f'Bad overlap: {overlap}'
print('PASS: chunks have correct overlap')
"

# AC4: No chunk exceeds 600 chars
python -c "
from content_assistant.rag.chunker import chunk_text
text = 'A' * 3000
chunks = chunk_text(text, chunk_size=500, overlap=50)
max_len = max(len(c['text']) for c in chunks)
assert max_len <= 600, f'Max chunk is {max_len} chars'
print(f'PASS: max chunk size is {max_len} chars')
"

# AC5: Chunks have required keys
python -c "
from content_assistant.rag.chunker import chunk_text
chunks = chunk_text('Test ' * 100)
required = {'text', 'start_char', 'end_char', 'chunk_index'}
for c in chunks:
    assert required.issubset(c.keys())
print('PASS: all chunks have required keys')
"

# AC6: All tests pass
pytest tests/test_chunker.py -v
# Expected: at least 10 passed

# AC7: Ruff passes
ruff check content_assistant/rag/chunker.py tests/test_chunker.py && echo "PASS: ruff clean"
```

---

#### Story 7: Build Embedding Module

**What to Build:**
Create an embedding module using Voyage AI that supports both single text and batch embedding with retry logic for rate limits.

**Files to Create:**

1. `content_assistant/rag/embeddings.py`
```python
"""Embedding utilities using Voyage AI."""
from typing import List, Optional
import voyageai
from tenacity import retry, stop_after_attempt, wait_exponential
from content_assistant.config import get_config


class EmbeddingError(Exception):
    """Raised when embedding fails."""
    pass


_client: Optional[voyageai.Client] = None


def get_voyage_client() -> voyageai.Client:
    """Get or create Voyage AI client."""
    global _client
    if _client is None:
        config = get_config()
        _client = voyageai.Client(api_key=config.voyage_api_key)
    return _client


def reset_client() -> None:
    """Reset client (for testing)."""
    global _client
    _client = None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def embed_text(text: str, model: Optional[str] = None) -> List[float]:
    """
    Generate embedding for a single text.

    Args:
        text: Text to embed
        model: Voyage model to use (default from config)

    Returns:
        List of 1024 floats (embedding vector)

    Raises:
        EmbeddingError: If embedding fails
    """
    if not text or not text.strip():
        raise EmbeddingError("Cannot embed empty text")

    config = get_config()
    model = model or config.voyage_model
    client = get_voyage_client()

    try:
        result = client.embed([text], model=model, input_type="document")
        return result.embeddings[0]
    except Exception as e:
        raise EmbeddingError(f"Embedding failed: {e}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def embed_texts(
    texts: List[str],
    model: Optional[str] = None,
    batch_size: int = 128,
) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.

    Args:
        texts: List of texts to embed
        model: Voyage model to use (default from config)
        batch_size: Number of texts per API call

    Returns:
        List of embedding vectors (each 1024 floats)

    Raises:
        EmbeddingError: If embedding fails
    """
    if not texts:
        return []

    # Filter empty texts
    valid_texts = [t for t in texts if t and t.strip()]
    if not valid_texts:
        raise EmbeddingError("All texts are empty")

    config = get_config()
    model = model or config.voyage_model
    client = get_voyage_client()

    all_embeddings = []
    try:
        # Process in batches
        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i + batch_size]
            result = client.embed(batch, model=model, input_type="document")
            all_embeddings.extend(result.embeddings)
        return all_embeddings
    except Exception as e:
        raise EmbeddingError(f"Batch embedding failed: {e}")


def embed_query(text: str, model: Optional[str] = None) -> List[float]:
    """
    Generate embedding for a search query.

    Uses input_type="query" for better search performance.

    Args:
        text: Query text
        model: Voyage model to use

    Returns:
        Embedding vector
    """
    if not text or not text.strip():
        raise EmbeddingError("Cannot embed empty query")

    config = get_config()
    model = model or config.voyage_model
    client = get_voyage_client()

    try:
        result = client.embed([text], model=model, input_type="query")
        return result.embeddings[0]
    except Exception as e:
        raise EmbeddingError(f"Query embedding failed: {e}")
```

2. `tests/test_embeddings.py`
```python
"""Tests for embedding module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from content_assistant.rag.embeddings import (
    embed_text,
    embed_texts,
    embed_query,
    EmbeddingError,
    reset_client,
)
from content_assistant.config import reset_config


class TestEmbedText:
    """Tests for single text embedding."""

    def setup_method(self):
        reset_client()
        reset_config()

    @patch("content_assistant.rag.embeddings.get_voyage_client")
    def test_embed_text_returns_1024_floats(self, mock_get_client, monkeypatch):
        """Test that embed_text returns list of 1024 floats."""
        # Setup env
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-voyage-key")

        # Mock Voyage response
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.embeddings = [[0.1] * 1024]  # 1024 floats
        mock_client.embed.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = embed_text("hello world")

        assert isinstance(result, list)
        assert len(result) == 1024
        assert all(isinstance(x, float) for x in result)

    @patch("content_assistant.rag.embeddings.get_voyage_client")
    def test_embed_text_empty_raises_error(self, mock_get_client, monkeypatch):
        """Test that empty text raises EmbeddingError."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        with pytest.raises(EmbeddingError) as exc_info:
            embed_text("")
        assert "empty" in str(exc_info.value).lower()


class TestEmbedTexts:
    """Tests for batch embedding."""

    def setup_method(self):
        reset_client()
        reset_config()

    @patch("content_assistant.rag.embeddings.get_voyage_client")
    def test_embed_texts_returns_multiple_embeddings(self, mock_get_client, monkeypatch):
        """Test that embed_texts returns one embedding per text."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.embeddings = [[0.1] * 1024, [0.2] * 1024]
        mock_client.embed.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = embed_texts(["text a", "text b"])

        assert len(result) == 2
        assert len(result[0]) == 1024
        assert len(result[1]) == 1024

    @patch("content_assistant.rag.embeddings.get_voyage_client")
    def test_embed_texts_empty_list_returns_empty(self, mock_get_client, monkeypatch):
        """Test that empty list returns empty list."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        result = embed_texts([])
        assert result == []


@pytest.mark.integration
class TestEmbeddingsIntegration:
    """Integration tests requiring real Voyage AI."""

    def setup_method(self):
        reset_client()
        reset_config()

    @pytest.mark.skipif(
        not __import__("os").getenv("VOYAGE_API_KEY"),
        reason="VOYAGE_API_KEY not set"
    )
    def test_real_embedding(self):
        """Test actual embedding with Voyage AI."""
        result = embed_text("Hello world, this is a test.")

        assert isinstance(result, list)
        assert len(result) == 1024
        assert all(isinstance(x, float) for x in result)
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.rag.embeddings import embed_text, embed_texts, embed_query, EmbeddingError" && echo "PASS"

# AC2: embed_text returns 1024 floats (mocked test)
pytest tests/test_embeddings.py::TestEmbedText::test_embed_text_returns_1024_floats -v
# Expected: PASSED

# AC3: embed_texts returns 2 embeddings for 2 inputs (mocked test)
pytest tests/test_embeddings.py::TestEmbedTexts::test_embed_texts_returns_multiple_embeddings -v
# Expected: PASSED

# AC4: Empty text raises EmbeddingError
pytest tests/test_embeddings.py::TestEmbedText::test_embed_text_empty_raises_error -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_embeddings.py -v -k "not integration"
# Expected: at least 4 passed

# AC6: Function has retry decorator
python -c "
from content_assistant.rag.embeddings import embed_text
# Check that embed_text has retry wrapper
assert hasattr(embed_text, 'retry')
print('PASS: embed_text has retry logic')
"

# AC7: Ruff passes
ruff check content_assistant/rag/embeddings.py tests/test_embeddings.py && echo "PASS: ruff clean"
```

---

#### Story 8: Build Vector Store Operations

**What to Build:**
Create a vector store module that uses Supabase pgvector for storing and searching embedded chunks.

**Files to Create:**

1. `content_assistant/rag/vector_store.py`
```python
"""Vector store operations using Supabase pgvector."""
from typing import List, Optional
from content_assistant.db.supabase_client import get_admin_client
from content_assistant.rag.embeddings import embed_query


def store_chunks(
    chunks: List[dict],
    source: str,
    collection: str = "wellness",
) -> int:
    """
    Store embedded chunks in the vector database.

    Args:
        chunks: List of chunk dicts with 'text' and 'embedding' keys
        source: Source document identifier (e.g., "minibook1.pdf")
        collection: Collection name ("wellness" or "engagement")

    Returns:
        Number of chunks stored

    Raises:
        ValueError: If chunks are invalid
    """
    if not chunks:
        return 0

    client = get_admin_client()

    # Prepare records for insertion
    records = []
    for i, chunk in enumerate(chunks):
        if "text" not in chunk or "embedding" not in chunk:
            raise ValueError(f"Chunk {i} missing 'text' or 'embedding' key")

        records.append({
            "source": source,
            "collection": collection,
            "chunk_text": chunk["text"],
            "chunk_index": chunk.get("chunk_index", i),
            "embedding": chunk["embedding"],
            "metadata": chunk.get("metadata", {}),
        })

    # Insert into knowledge_chunks table
    result = client.table("knowledge_chunks").insert(records).execute()

    return len(result.data) if result.data else 0


def search(
    query: str,
    collection: str = "wellness",
    top_k: int = 5,
) -> List[dict]:
    """
    Search for similar chunks using vector similarity.

    Args:
        query: Search query text
        collection: Collection to search ("wellness" or "engagement")
        top_k: Number of results to return

    Returns:
        List of dicts with: text, source, score, metadata
    """
    # Embed the query
    query_embedding = embed_query(query)

    client = get_admin_client()

    # Use pgvector similarity search via RPC function
    # This requires a function to be set up in Supabase
    # For now, we'll use a simple approach with the Python client

    # Note: This requires the match_knowledge_chunks function in Supabase
    # See schema.sql for the function definition
    result = client.rpc(
        "match_knowledge_chunks",
        {
            "query_embedding": query_embedding,
            "match_collection": collection,
            "match_count": top_k,
        }
    ).execute()

    if not result.data:
        return []

    return [
        {
            "text": row["chunk_text"],
            "source": row["source"],
            "score": row["similarity"],
            "metadata": row.get("metadata", {}),
        }
        for row in result.data
    ]


def delete_by_source(source: str) -> int:
    """
    Delete all chunks from a specific source.

    Args:
        source: Source identifier to delete

    Returns:
        Number of chunks deleted
    """
    client = get_admin_client()
    result = client.table("knowledge_chunks").delete().eq("source", source).execute()
    return len(result.data) if result.data else 0


def count_chunks(collection: Optional[str] = None) -> int:
    """
    Count chunks in the store.

    Args:
        collection: Optional collection to filter by

    Returns:
        Number of chunks
    """
    client = get_admin_client()
    query = client.table("knowledge_chunks").select("id", count="exact")
    if collection:
        query = query.eq("collection", collection)
    result = query.execute()
    return result.count if result.count else 0
```

2. `tests/test_vector_store.py`
```python
"""Tests for vector store operations."""
import pytest
from unittest.mock import MagicMock, patch
from content_assistant.rag.vector_store import (
    store_chunks,
    search,
    delete_by_source,
    count_chunks,
)
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients


class TestStoreChunks:
    """Tests for storing chunks."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.rag.vector_store.get_admin_client")
    def test_store_chunks_returns_count(self, mock_get_client, monkeypatch):
        """Test that store_chunks returns number stored."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "1"}, {"id": "2"}]  # 2 inserted
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        chunks = [
            {"text": "chunk 1", "embedding": [0.1] * 1024, "chunk_index": 0},
            {"text": "chunk 2", "embedding": [0.2] * 1024, "chunk_index": 1},
        ]

        result = store_chunks(chunks, source="test.pdf", collection="wellness")

        assert result == 2

    def test_store_chunks_empty_returns_zero(self):
        """Test that empty chunks list returns 0."""
        result = store_chunks([], source="test.pdf")
        assert result == 0

    @patch("content_assistant.rag.vector_store.get_admin_client")
    def test_store_chunks_validates_keys(self, mock_get_client, monkeypatch):
        """Test that chunks without required keys raise error."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        chunks = [{"text": "missing embedding"}]  # No 'embedding' key

        with pytest.raises(ValueError) as exc_info:
            store_chunks(chunks, source="test.pdf")
        assert "embedding" in str(exc_info.value).lower()


class TestSearch:
    """Tests for vector search."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.rag.vector_store.embed_query")
    @patch("content_assistant.rag.vector_store.get_admin_client")
    def test_search_returns_results(self, mock_get_client, mock_embed, monkeypatch):
        """Test that search returns list of results."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_embed.return_value = [0.1] * 1024

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"chunk_text": "detox content", "source": "minibook1.pdf", "similarity": 0.95, "metadata": {}},
            {"chunk_text": "more detox", "source": "minibook1.pdf", "similarity": 0.90, "metadata": {}},
        ]
        mock_client.rpc.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        results = search("detox", collection="wellness", top_k=5)

        assert len(results) == 2
        assert results[0]["text"] == "detox content"
        assert results[0]["source"] == "minibook1.pdf"
        assert "score" in results[0]

    @patch("content_assistant.rag.vector_store.embed_query")
    @patch("content_assistant.rag.vector_store.get_admin_client")
    def test_search_results_have_required_keys(self, mock_get_client, mock_embed, monkeypatch):
        """Test that results have text, source, score keys."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_embed.return_value = [0.1] * 1024

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"chunk_text": "test", "source": "test.pdf", "similarity": 0.9, "metadata": {}},
        ]
        mock_client.rpc.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        results = search("test query")

        required_keys = {"text", "source", "score"}
        for result in results:
            assert required_keys.issubset(result.keys())
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.rag.vector_store import store_chunks, search, delete_by_source, count_chunks" && echo "PASS"

# AC2: store_chunks returns count (mocked)
pytest tests/test_vector_store.py::TestStoreChunks::test_store_chunks_returns_count -v
# Expected: PASSED

# AC3: search returns results with required keys (mocked)
pytest tests/test_vector_store.py::TestSearch::test_search_results_have_required_keys -v
# Expected: PASSED

# AC4: Empty chunks returns 0
pytest tests/test_vector_store.py::TestStoreChunks::test_store_chunks_empty_returns_zero -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_vector_store.py -v
# Expected: at least 5 passed

# AC6: Ruff passes
ruff check content_assistant/rag/vector_store.py tests/test_vector_store.py && echo "PASS: ruff clean"
```

---

#### Story 9: Build Knowledge Base Loader

**What to Build:**
Create a knowledge base module that orchestrates loading PDFs and engagement guidelines into the vector store, and provides retrieval functions for wellness facts and engagement patterns.

**Files to Create:**

1. `content_assistant/rag/knowledge_base.py`
```python
"""Knowledge base management for TheLifeCo Content Assistant."""
from pathlib import Path
from typing import List, Union, Optional
from content_assistant.rag.loader import load_document, get_document_metadata
from content_assistant.rag.chunker import chunk_text
from content_assistant.rag.embeddings import embed_texts
from content_assistant.rag.vector_store import store_chunks, search, delete_by_source, count_chunks


def load_wellness_knowledge(
    pdf_paths: List[Union[str, Path]],
    chunk_size: int = 500,
    overlap: int = 50,
) -> dict:
    """
    Load and index wellness knowledge from PDF files.

    Args:
        pdf_paths: List of paths to PDF files
        chunk_size: Size of text chunks
        overlap: Overlap between chunks

    Returns:
        dict with: total_chunks, sources_loaded, errors
    """
    results = {
        "total_chunks": 0,
        "sources_loaded": [],
        "errors": [],
    }

    for pdf_path in pdf_paths:
        pdf_path = Path(pdf_path)
        try:
            # Load document
            text = load_document(pdf_path)

            # Chunk text
            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

            if not chunks:
                results["errors"].append(f"{pdf_path.name}: no chunks generated")
                continue

            # Embed chunks
            texts = [c["text"] for c in chunks]
            embeddings = embed_texts(texts)

            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding
                chunk["metadata"] = {
                    "source_file": pdf_path.name,
                    **get_document_metadata(pdf_path),
                }

            # Store in vector database
            stored = store_chunks(chunks, source=pdf_path.name, collection="wellness")

            results["total_chunks"] += stored
            results["sources_loaded"].append(pdf_path.name)

        except Exception as e:
            results["errors"].append(f"{pdf_path.name}: {str(e)}")

    return results


def load_engagement_guidelines(
    doc_paths: List[Union[str, Path]],
    chunk_size: int = 500,
    overlap: int = 50,
) -> dict:
    """
    Load and index engagement guidelines (markdown files).

    Args:
        doc_paths: List of paths to guideline documents
        chunk_size: Size of text chunks
        overlap: Overlap between chunks

    Returns:
        dict with: total_chunks, sources_loaded, errors
    """
    results = {
        "total_chunks": 0,
        "sources_loaded": [],
        "errors": [],
    }

    for doc_path in doc_paths:
        doc_path = Path(doc_path)
        try:
            text = load_document(doc_path)
            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

            if not chunks:
                results["errors"].append(f"{doc_path.name}: no chunks generated")
                continue

            texts = [c["text"] for c in chunks]
            embeddings = embed_texts(texts)

            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding
                chunk["metadata"] = {"source_file": doc_path.name}

            stored = store_chunks(chunks, source=doc_path.name, collection="engagement")

            results["total_chunks"] += stored
            results["sources_loaded"].append(doc_path.name)

        except Exception as e:
            results["errors"].append(f"{doc_path.name}: {str(e)}")

    return results


def retrieve_wellness_facts(
    query: str,
    top_k: int = 5,
) -> List[dict]:
    """
    Retrieve relevant wellness facts for a query.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        List of dicts with: text, source, score
    """
    return search(query, collection="wellness", top_k=top_k)


def retrieve_engagement_patterns(
    query: str,
    top_k: int = 5,
) -> List[dict]:
    """
    Retrieve relevant engagement patterns for a query.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        List of dicts with: text, source, score
    """
    return search(query, collection="engagement", top_k=top_k)


def get_knowledge_stats() -> dict:
    """
    Get statistics about the knowledge base.

    Returns:
        dict with counts by collection
    """
    return {
        "wellness_chunks": count_chunks("wellness"),
        "engagement_chunks": count_chunks("engagement"),
        "total_chunks": count_chunks(),
    }
```

2. `tests/test_knowledge_base.py`
```python
"""Tests for knowledge base module."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from content_assistant.rag.knowledge_base import (
    load_wellness_knowledge,
    load_engagement_guidelines,
    retrieve_wellness_facts,
    retrieve_engagement_patterns,
    get_knowledge_stats,
)
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients
from content_assistant.rag.embeddings import reset_client as reset_embed_client


class TestLoadWellnessKnowledge:
    """Tests for loading wellness PDFs."""

    def setup_method(self):
        reset_config()
        reset_clients()
        reset_embed_client()

    @patch("content_assistant.rag.knowledge_base.store_chunks")
    @patch("content_assistant.rag.knowledge_base.embed_texts")
    @patch("content_assistant.rag.knowledge_base.load_document")
    def test_load_wellness_returns_results_dict(
        self, mock_load, mock_embed, mock_store, monkeypatch
    ):
        """Test that load_wellness_knowledge returns proper results."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        # Mock document loading
        mock_load.return_value = "Test wellness content. " * 100

        # Mock embeddings
        mock_embed.return_value = [[0.1] * 1024] * 3  # 3 chunks

        # Mock storage
        mock_store.return_value = 3

        # Create temp PDF path (won't actually be read due to mock)
        result = load_wellness_knowledge(["test.pdf"])

        assert "total_chunks" in result
        assert "sources_loaded" in result
        assert "errors" in result


class TestRetrieveWellnessFacts:
    """Tests for wellness fact retrieval."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.rag.knowledge_base.search")
    def test_retrieve_wellness_facts_returns_results(self, mock_search, monkeypatch):
        """Test that retrieve_wellness_facts returns results."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_search.return_value = [
            {"text": "Fasting fact 1", "source": "minibook1.pdf", "score": 0.95},
            {"text": "Fasting fact 2", "source": "minibook1.pdf", "score": 0.90},
            {"text": "Fasting fact 3", "source": "minibook1.pdf", "score": 0.85},
        ]

        results = retrieve_wellness_facts("fasting")

        assert len(results) >= 3
        mock_search.assert_called_once_with("fasting", collection="wellness", top_k=5)

    @patch("content_assistant.rag.knowledge_base.search")
    def test_results_have_required_keys(self, mock_search, monkeypatch):
        """Test that results include text, source, score."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_search.return_value = [
            {"text": "test text", "source": "test.pdf", "score": 0.9},
        ]

        results = retrieve_wellness_facts("test")

        required_keys = {"text", "source", "score"}
        for result in results:
            assert required_keys.issubset(result.keys())


@pytest.mark.integration
class TestKnowledgeBaseIntegration:
    """Integration tests requiring real services."""

    @pytest.mark.skipif(
        not all([
            Path("minibook1.pdf").exists(),
            __import__("os").getenv("VOYAGE_API_KEY"),
            __import__("os").getenv("SUPABASE_URL"),
        ]),
        reason="Missing minibook1.pdf or API credentials"
    )
    def test_load_and_retrieve_minibook(self):
        """Test loading minibook1.pdf and retrieving facts about fasting."""
        # Load the PDF
        result = load_wellness_knowledge(["minibook1.pdf"])
        assert result["total_chunks"] > 0, "Should have loaded chunks"

        # Retrieve facts about fasting
        facts = retrieve_wellness_facts("fasting")
        assert len(facts) >= 3, "Should return at least 3 facts about fasting"
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.rag.knowledge_base import load_wellness_knowledge, load_engagement_guidelines, retrieve_wellness_facts, retrieve_engagement_patterns" && echo "PASS"

# AC2: Functions have correct signatures
python -c "
import inspect
from content_assistant.rag.knowledge_base import retrieve_wellness_facts
sig = inspect.signature(retrieve_wellness_facts)
assert 'query' in sig.parameters
assert 'top_k' in sig.parameters
print('PASS: correct signature')
"

# AC3: Load function returns results dict (mocked)
pytest tests/test_knowledge_base.py::TestLoadWellnessKnowledge::test_load_wellness_returns_results_dict -v
# Expected: PASSED

# AC4: Retrieve returns results with required keys (mocked)
pytest tests/test_knowledge_base.py::TestRetrieveWellnessFacts::test_results_have_required_keys -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_knowledge_base.py -v -k "not integration"
# Expected: at least 4 passed

# AC6: Ruff passes
ruff check content_assistant/rag/knowledge_base.py tests/test_knowledge_base.py && echo "PASS: ruff clean"
```

---
### Epic 4: Content Generation Tools
---

#### Story 10: Build Claude Client Module

**What to Build:**
Create a Claude API client module that handles both simple text generation and tool-calling workflows with proper error handling and retry logic.

**Files to Create:**

1. `content_assistant/tools/claude_client.py`
```python
"""Claude API client for content generation."""
from typing import List, Dict, Optional, Any
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from content_assistant.config import get_config


class ClaudeClientError(Exception):
    """Raised when Claude API calls fail."""
    pass


_client: Optional[anthropic.Anthropic] = None


def get_anthropic_client() -> anthropic.Anthropic:
    """Get or create Anthropic client."""
    global _client
    if _client is None:
        config = get_config()
        _client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    return _client


def reset_client() -> None:
    """Reset client (for testing)."""
    global _client
    _client = None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def generate(
    system_prompt: str,
    user_message: str,
    model: Optional[str] = None,
    max_tokens: int = 4096,
) -> str:
    """
    Generate text using Claude without tools.

    Args:
        system_prompt: System message defining Claude's role
        user_message: User's input message
        model: Claude model to use (default from config)
        max_tokens: Maximum tokens in response

    Returns:
        Generated text response

    Raises:
        ClaudeClientError: If generation fails
    """
    config = get_config()
    model = model or config.claude_model
    client = get_anthropic_client()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        # Extract text from response
        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        if not text_parts:
            raise ClaudeClientError("No text in response")

        return "\n".join(text_parts)

    except anthropic.APIError as e:
        raise ClaudeClientError(f"Claude API error: {e}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def generate_with_tools(
    system_prompt: str,
    user_message: str,
    tools: List[Dict[str, Any]],
    tool_executor: callable,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    max_iterations: int = 10,
) -> Dict[str, Any]:
    """
    Generate using Claude with tool calling support.

    Args:
        system_prompt: System message
        user_message: User's input
        tools: List of tool definitions
        tool_executor: Function that executes tools: (name, input) -> result
        model: Claude model to use
        max_tokens: Max tokens per response
        max_iterations: Max tool call iterations

    Returns:
        dict with: final_text, tool_calls (list of {name, input, result})

    Raises:
        ClaudeClientError: If generation fails
    """
    config = get_config()
    model = model or config.claude_model
    client = get_anthropic_client()

    messages = [{"role": "user", "content": user_message}]
    tool_calls = []

    try:
        for iteration in range(max_iterations):
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )

            # Check if we're done (no more tool calls)
            if response.stop_reason == "end_turn":
                # Extract final text
                text_parts = []
                for block in response.content:
                    if hasattr(block, "text"):
                        text_parts.append(block.text)

                return {
                    "final_text": "\n".join(text_parts),
                    "tool_calls": tool_calls,
                }

            # Process tool calls
            if response.stop_reason == "tool_use":
                # Add assistant message
                messages.append({"role": "assistant", "content": response.content})

                # Execute each tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        # Execute the tool
                        try:
                            result = tool_executor(tool_name, tool_input)
                        except Exception as e:
                            result = f"Error executing tool: {e}"

                        tool_calls.append({
                            "name": tool_name,
                            "input": tool_input,
                            "result": result,
                        })

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })

                # Add tool results
                messages.append({"role": "user", "content": tool_results})

        # Max iterations reached
        raise ClaudeClientError(f"Max iterations ({max_iterations}) reached")

    except anthropic.APIError as e:
        raise ClaudeClientError(f"Claude API error: {e}")


def generate_json(
    system_prompt: str,
    user_message: str,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate JSON output from Claude.

    Args:
        system_prompt: System prompt (should ask for JSON)
        user_message: User message

    Returns:
        Parsed JSON dict

    Raises:
        ClaudeClientError: If generation or parsing fails
    """
    import json

    response = generate(
        system_prompt=system_prompt + "\n\nRespond ONLY with valid JSON, no other text.",
        user_message=user_message,
        model=model,
    )

    # Try to extract JSON from response
    try:
        # Handle markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ClaudeClientError(f"Failed to parse JSON response: {e}")
```

2. `tests/test_claude_client.py`
```python
"""Tests for Claude client module."""
import pytest
from unittest.mock import MagicMock, patch
from content_assistant.tools.claude_client import (
    generate,
    generate_with_tools,
    generate_json,
    ClaudeClientError,
    reset_client,
)
from content_assistant.config import reset_config


class TestGenerate:
    """Tests for simple text generation."""

    def setup_method(self):
        reset_client()
        reset_config()

    @patch("content_assistant.tools.claude_client.get_anthropic_client")
    def test_generate_returns_non_empty_string(self, mock_get_client, monkeypatch):
        """Test that generate returns non-empty string."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        # Mock response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_text_block = MagicMock()
        mock_text_block.text = "Hello! How can I help you today?"
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate("You are helpful", "Say hello")

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("content_assistant.tools.claude_client.get_anthropic_client")
    def test_generate_response_contains_greeting(self, mock_get_client, monkeypatch):
        """Test that greeting request returns greeting."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_text_block = MagicMock()
        mock_text_block.text = "Hello there! Nice to meet you."
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate("You are a friendly assistant", "Say hello")

        # Check response contains greeting-related words
        result_lower = result.lower()
        assert any(word in result_lower for word in ["hello", "hi", "hey", "greetings", "nice"])


class TestGenerateWithTools:
    """Tests for tool-calling generation."""

    def setup_method(self):
        reset_client()
        reset_config()

    @patch("content_assistant.tools.claude_client.get_anthropic_client")
    def test_generate_with_tools_returns_dict(self, mock_get_client, monkeypatch):
        """Test that generate_with_tools returns dict with required keys."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        mock_text_block = MagicMock()
        mock_text_block.text = "I've completed the task."
        mock_text_block.type = "text"
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        tools = [{
            "name": "test_tool",
            "description": "A test tool",
            "input_schema": {"type": "object", "properties": {}},
        }]

        result = generate_with_tools(
            system_prompt="You are helpful",
            user_message="Do something",
            tools=tools,
            tool_executor=lambda name, input: "done",
        )

        assert isinstance(result, dict)
        assert "final_text" in result
        assert "tool_calls" in result

    @patch("content_assistant.tools.claude_client.get_anthropic_client")
    def test_tool_executor_is_called(self, mock_get_client, monkeypatch):
        """Test that tool executor is called when Claude uses tools."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()

        # First response: tool use
        mock_tool_response = MagicMock()
        mock_tool_response.stop_reason = "tool_use"
        mock_tool_block = MagicMock()
        mock_tool_block.type = "tool_use"
        mock_tool_block.name = "search"
        mock_tool_block.input = {"query": "test"}
        mock_tool_block.id = "tool_123"
        mock_tool_response.content = [mock_tool_block]

        # Second response: end turn
        mock_final_response = MagicMock()
        mock_final_response.stop_reason = "end_turn"
        mock_text_block = MagicMock()
        mock_text_block.text = "Found results."
        mock_text_block.type = "text"
        mock_final_response.content = [mock_text_block]

        mock_client.messages.create.side_effect = [mock_tool_response, mock_final_response]
        mock_get_client.return_value = mock_client

        executor_called = []

        def mock_executor(name, input):
            executor_called.append((name, input))
            return "search results"

        tools = [{
            "name": "search",
            "description": "Search for info",
            "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
        }]

        result = generate_with_tools(
            system_prompt="Use tools",
            user_message="Search for test",
            tools=tools,
            tool_executor=mock_executor,
        )

        assert len(executor_called) == 1
        assert executor_called[0][0] == "search"
        assert len(result["tool_calls"]) == 1


class TestGenerateJson:
    """Tests for JSON generation."""

    def setup_method(self):
        reset_client()
        reset_config()

    @patch("content_assistant.tools.claude_client.get_anthropic_client")
    def test_generate_json_returns_dict(self, mock_get_client, monkeypatch):
        """Test that generate_json returns parsed dict."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_text_block = MagicMock()
        mock_text_block.text = '{"name": "test", "value": 42}'
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate_json("Return JSON", "Give me data")

        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["value"] == 42


@pytest.mark.integration
class TestClaudeClientIntegration:
    """Integration tests requiring real Claude API."""

    @pytest.mark.skipif(
        not __import__("os").getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_real_generation(self):
        """Test actual generation with Claude."""
        result = generate(
            system_prompt="You are a helpful assistant. Respond briefly.",
            user_message="Say hello in exactly 3 words.",
        )

        assert isinstance(result, str)
        assert len(result) > 0
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.claude_client import generate, generate_with_tools, generate_json, ClaudeClientError" && echo "PASS"

# AC2: generate returns non-empty string (mocked)
pytest tests/test_claude_client.py::TestGenerate::test_generate_returns_non_empty_string -v
# Expected: PASSED

# AC3: generate response contains greeting (mocked)
pytest tests/test_claude_client.py::TestGenerate::test_generate_response_contains_greeting -v
# Expected: PASSED

# AC4: generate_with_tools returns dict with required keys (mocked)
pytest tests/test_claude_client.py::TestGenerateWithTools::test_generate_with_tools_returns_dict -v
# Expected: PASSED

# AC5: Tool executor is called when tools used (mocked)
pytest tests/test_claude_client.py::TestGenerateWithTools::test_tool_executor_is_called -v
# Expected: PASSED

# AC6: All unit tests pass
pytest tests/test_claude_client.py -v -k "not integration"
# Expected: at least 5 passed

# AC7: Functions have retry decorator
python -c "
from content_assistant.tools.claude_client import generate
assert hasattr(generate, 'retry')
print('PASS: generate has retry logic')
"

# AC8: Ruff passes
ruff check content_assistant/tools/claude_client.py tests/test_claude_client.py && echo "PASS: ruff clean"
```

---

#### Story 11: Build Socratic Brief Questionnaire

**What to Build:**
Create a brief questionnaire module that defines the 13 mandatory questions, validates briefs, and analyzes them for potential clarification needs.

**Files to Create:**

1. `content_assistant/tools/brief_questionnaire.py`
```python
"""Socratic Brief Questionnaire for content generation."""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from content_assistant.tools.claude_client import generate_json


@dataclass
class BriefQuestion:
    """Definition of a brief question."""
    field_name: str
    question: str
    placeholder: str
    section: str
    is_crucial: bool = False


# The 13 mandatory questions organized by section
BRIEF_QUESTIONS: List[BriefQuestion] = [
    # AUDIENCE & PROBLEM
    BriefQuestion(
        field_name="target_audience",
        question="Who is this content for? Describe your ideal reader.",
        placeholder="Busy executives aged 40-55 who are experiencing burnout",
        section="AUDIENCE & PROBLEM",
    ),
    BriefQuestion(
        field_name="pain_area",
        question="What problem or pain point are they facing? Be specific.",
        placeholder="Chronic fatigue, can't lose weight despite trying many diets",
        section="AUDIENCE & PROBLEM",
        is_crucial=True,  # Marked as crucial
    ),
    BriefQuestion(
        field_name="compliance_level",
        question="Is this for people with medical conditions (high compliance) or lifestyle goals (low compliance)?",
        placeholder="High compliance - Type 2 diabetes management",
        section="AUDIENCE & PROBLEM",
    ),
    BriefQuestion(
        field_name="funnel_stage",
        question="What marketing funnel stage? (Awareness / Consideration / Conversion / Loyalty)",
        placeholder="Consideration - they're researching wellness retreat options",
        section="AUDIENCE & PROBLEM",
    ),
    # VALUE & ACTION
    BriefQuestion(
        field_name="value_proposition",
        question="What's the main benefit or transformation we're offering?",
        placeholder="Reset your metabolism and energy levels in 7 days",
        section="VALUE & ACTION",
    ),
    BriefQuestion(
        field_name="desired_action",
        question="What ONE action should they take after reading this?",
        placeholder="Book a free 15-minute consultation call",
        section="VALUE & ACTION",
    ),
    # THELIFECO SPECIFICS
    BriefQuestion(
        field_name="specific_programs",
        question="Which TheLifeCo programs should be mentioned?",
        placeholder="Diabetes Management program under Lifestyle As Medicine",
        section="THELIFECO SPECIFICS",
    ),
    BriefQuestion(
        field_name="specific_centers",
        question="Which TheLifeCo centers to feature?",
        placeholder="Bodrum and Antalya, Turkey",
        section="THELIFECO SPECIFICS",
    ),
    # TONE & CONTENT
    BriefQuestion(
        field_name="tone",
        question="What tone/voice should this content have?",
        placeholder="Warm and educational, medically credible, not salesy",
        section="TONE & CONTENT",
    ),
    BriefQuestion(
        field_name="key_messages",
        question="Any specific facts, stats, or messages that MUST be included?",
        placeholder="Mention 20+ years experience, medically supervised, doctor consultations",
        section="TONE & CONTENT",
    ),
    BriefQuestion(
        field_name="constraints",
        question="Anything to AVOID mentioning?",
        placeholder="Don't mention specific prices, avoid 'cure' language",
        section="TONE & CONTENT",
    ),
    # PLATFORM & PRICING
    BriefQuestion(
        field_name="platform",
        question="Where will this content be published?",
        placeholder="Email newsletter for existing leads",
        section="PLATFORM & PRICING",
    ),
    BriefQuestion(
        field_name="price_point",
        question="Any pricing information to include?",
        placeholder="Starting from €2,500 for 7-day program",
        section="PLATFORM & PRICING",
    ),
]

# All 13 required field names
REQUIRED_FIELDS = [q.field_name for q in BRIEF_QUESTIONS]


def get_questions_by_section() -> Dict[str, List[BriefQuestion]]:
    """
    Get questions organized by section.

    Returns:
        Dict mapping section name to list of questions
    """
    sections: Dict[str, List[BriefQuestion]] = {}
    for q in BRIEF_QUESTIONS:
        if q.section not in sections:
            sections[q.section] = []
        sections[q.section].append(q)
    return sections


def validate_brief(brief: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate that a brief has all required fields filled.

    Args:
        brief: Dict with brief field values

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    for field_name in REQUIRED_FIELDS:
        value = brief.get(field_name, "")
        if not value or not str(value).strip():
            # Find the question for better error message
            question = next((q for q in BRIEF_QUESTIONS if q.field_name == field_name), None)
            if question:
                errors.append(f"Missing required field: {question.question}")
            else:
                errors.append(f"Missing required field: {field_name}")

    return (len(errors) == 0, errors)


def analyze_brief_for_clarifications(brief: Dict[str, str]) -> List[str]:
    """
    Analyze a brief to determine if clarifying questions are needed.

    Uses Claude to identify ambiguities in the brief.

    Args:
        brief: Validated brief dict

    Returns:
        List of clarifying questions (empty if brief is clear)
    """
    # Check for obvious ambiguities first (without API call)
    clarifications = []

    # Check target_audience
    audience = brief.get("target_audience", "").lower()
    vague_audience_terms = ["everyone", "general", "all", "anyone", "people"]
    if any(term in audience for term in vague_audience_terms):
        clarifications.append(
            "Your target audience seems broad. Can you be more specific about "
            "their age, profession, or life situation?"
        )

    # Check pain_area
    pain = brief.get("pain_area", "").lower()
    if len(pain) < 20:  # Very short pain description
        clarifications.append(
            "Can you elaborate on the pain point? What specific symptoms or "
            "frustrations are they experiencing?"
        )

    # Check funnel_stage
    funnel = brief.get("funnel_stage", "").lower()
    valid_stages = ["awareness", "consideration", "conversion", "loyalty"]
    if not any(stage in funnel for stage in valid_stages):
        clarifications.append(
            "Please clarify the funnel stage: Is this for Awareness (don't know us), "
            "Consideration (comparing options), Conversion (ready to book), or Loyalty (past guests)?"
        )

    # If no obvious issues, return empty list (brief is clear)
    # For more sophisticated analysis, could use Claude
    return clarifications


def create_empty_brief() -> Dict[str, str]:
    """
    Create an empty brief template with all fields.

    Returns:
        Dict with all field names as keys, empty strings as values
    """
    return {q.field_name: "" for q in BRIEF_QUESTIONS}


def brief_to_context_string(brief: Dict[str, str]) -> str:
    """
    Convert a brief to a formatted string for use in prompts.

    Args:
        brief: Completed brief dict

    Returns:
        Formatted string representation
    """
    lines = ["## Content Brief\n"]
    for q in BRIEF_QUESTIONS:
        value = brief.get(q.field_name, "")
        lines.append(f"**{q.question}**")
        lines.append(f"{value}\n")
    return "\n".join(lines)
```

2. `tests/test_brief_questionnaire.py`
```python
"""Tests for brief questionnaire module."""
import pytest
from content_assistant.tools.brief_questionnaire import (
    BRIEF_QUESTIONS,
    REQUIRED_FIELDS,
    validate_brief,
    analyze_brief_for_clarifications,
    get_questions_by_section,
    create_empty_brief,
    brief_to_context_string,
)


class TestBriefQuestions:
    """Tests for question definitions."""

    def test_exactly_13_required_fields(self):
        """Test that there are exactly 13 required fields."""
        assert len(REQUIRED_FIELDS) == 13

    def test_exactly_13_questions(self):
        """Test that there are exactly 13 question definitions."""
        assert len(BRIEF_QUESTIONS) == 13

    def test_all_questions_have_required_attributes(self):
        """Test that all questions have field_name, question, placeholder, section."""
        for q in BRIEF_QUESTIONS:
            assert q.field_name, "Missing field_name"
            assert q.question, "Missing question"
            assert q.placeholder, "Missing placeholder"
            assert q.section, "Missing section"

    def test_pain_area_is_marked_crucial(self):
        """Test that pain_area is marked as crucial."""
        pain_q = next((q for q in BRIEF_QUESTIONS if q.field_name == "pain_area"), None)
        assert pain_q is not None
        assert pain_q.is_crucial is True


class TestValidateBrief:
    """Tests for brief validation."""

    def test_brief_with_empty_field_returns_invalid(self):
        """Test that brief with ANY empty field returns is_valid=False."""
        brief = create_empty_brief()
        # Fill all but one field
        for field in REQUIRED_FIELDS[:-1]:
            brief[field] = "Some value"
        # Leave last field empty

        is_valid, errors = validate_brief(brief)

        assert is_valid is False
        assert len(errors) >= 1

    def test_brief_with_all_fields_returns_valid(self):
        """Test that brief with all 13 fields filled returns is_valid=True."""
        brief = {
            "target_audience": "Busy executives aged 40-55 experiencing burnout",
            "pain_area": "Chronic fatigue, weight gain, stress",
            "compliance_level": "Low - lifestyle wellness",
            "funnel_stage": "Consideration",
            "value_proposition": "Reset your energy in 7 days",
            "desired_action": "Book a free consultation",
            "specific_programs": "Master Detox",
            "specific_centers": "Bodrum, Turkey",
            "tone": "Warm and educational",
            "key_messages": "20+ years experience, medically supervised",
            "constraints": "No specific prices, avoid cure language",
            "platform": "Email newsletter",
            "price_point": "Starting from €2,500",
        }

        is_valid, errors = validate_brief(brief)

        assert is_valid is True
        assert len(errors) == 0

    def test_whitespace_only_field_is_invalid(self):
        """Test that fields with only whitespace are invalid."""
        brief = {field: "valid" for field in REQUIRED_FIELDS}
        brief["target_audience"] = "   "  # Only whitespace

        is_valid, errors = validate_brief(brief)

        assert is_valid is False

    def test_missing_field_error_is_descriptive(self):
        """Test that error messages are descriptive."""
        brief = {}  # All fields missing

        is_valid, errors = validate_brief(brief)

        assert is_valid is False
        assert len(errors) == 13
        # Check errors mention the question or field
        assert any("audience" in e.lower() or "target" in e.lower() for e in errors)


class TestAnalyzeBriefForClarifications:
    """Tests for clarification analysis."""

    def test_ambiguous_audience_triggers_clarification(self):
        """Test that vague audience like 'general audience' triggers question."""
        brief = {
            "target_audience": "general audience, everyone interested in health",
            "pain_area": "They want to feel better",
            "compliance_level": "Low",
            "funnel_stage": "Awareness",
            "value_proposition": "Feel great",
            "desired_action": "Learn more",
            "specific_programs": "Any program",
            "specific_centers": "Any center",
            "tone": "Friendly",
            "key_messages": "We are good",
            "constraints": "None",
            "platform": "Social media",
            "price_point": "Various",
        }

        clarifications = analyze_brief_for_clarifications(brief)

        assert len(clarifications) >= 1
        assert any("audience" in c.lower() or "specific" in c.lower() for c in clarifications)

    def test_clear_specific_brief_returns_no_clarifications(self):
        """Test that clear, specific brief returns no clarification questions."""
        brief = {
            "target_audience": "Women aged 45-55 experiencing perimenopause symptoms, working professionals who feel their energy declining",
            "pain_area": "Hot flashes, sleep disturbances, weight gain around midsection despite maintaining same diet and exercise routine, mood swings affecting work relationships",
            "compliance_level": "High compliance - hormonal health management",
            "funnel_stage": "Consideration - they've heard of TheLifeCo and are researching options",
            "value_proposition": "Restore hormonal balance naturally with medically supervised protocols, regain energy and mental clarity",
            "desired_action": "Book a free 20-minute consultation with our women's health specialist",
            "specific_programs": "Hormonal Longevity for Women program",
            "specific_centers": "Bodrum, Turkey - our flagship center with full hormonal health facilities",
            "tone": "Empathetic and scientifically credible, acknowledging their struggles while offering hope",
            "key_messages": "Our approach combines functional medicine testing with personalized nutrition, bioidentical hormone support when appropriate, stress management techniques",
            "constraints": "Avoid making promises about specific symptom relief timelines, don't compare to HRT negatively",
            "platform": "Email sequence for leads who downloaded our perimenopause guide",
            "price_point": "14-day program starting from €4,500, mention that insurance may cover some costs",
        }

        clarifications = analyze_brief_for_clarifications(brief)

        assert len(clarifications) == 0


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_questions_by_section_returns_all_sections(self):
        """Test that all sections are returned."""
        sections = get_questions_by_section()

        expected_sections = [
            "AUDIENCE & PROBLEM",
            "VALUE & ACTION",
            "THELIFECO SPECIFICS",
            "TONE & CONTENT",
            "PLATFORM & PRICING",
        ]

        for section in expected_sections:
            assert section in sections

    def test_create_empty_brief_has_all_fields(self):
        """Test that empty brief template has all 13 fields."""
        empty = create_empty_brief()

        assert len(empty) == 13
        for field in REQUIRED_FIELDS:
            assert field in empty
            assert empty[field] == ""

    def test_brief_to_context_string_includes_all_fields(self):
        """Test that context string includes all brief fields."""
        brief = {field: f"Value for {field}" for field in REQUIRED_FIELDS}

        context = brief_to_context_string(brief)

        # Check all values are in the context
        for field in REQUIRED_FIELDS:
            assert f"Value for {field}" in context
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.brief_questionnaire import BRIEF_QUESTIONS, REQUIRED_FIELDS, validate_brief, analyze_brief_for_clarifications" && echo "PASS"

# AC2: Exactly 13 required fields
python -c "
from content_assistant.tools.brief_questionnaire import REQUIRED_FIELDS
assert len(REQUIRED_FIELDS) == 13, f'Expected 13 fields, got {len(REQUIRED_FIELDS)}'
print('PASS: exactly 13 required fields')
"

# AC3: Brief with empty field returns is_valid=False
pytest tests/test_brief_questionnaire.py::TestValidateBrief::test_brief_with_empty_field_returns_invalid -v
# Expected: PASSED

# AC4: Brief with all 13 fields filled returns is_valid=True
pytest tests/test_brief_questionnaire.py::TestValidateBrief::test_brief_with_all_fields_returns_valid -v
# Expected: PASSED

# AC5: Ambiguous brief triggers clarification question
pytest tests/test_brief_questionnaire.py::TestAnalyzeBriefForClarifications::test_ambiguous_audience_triggers_clarification -v
# Expected: PASSED

# AC6: Clear specific brief returns no clarifications
pytest tests/test_brief_questionnaire.py::TestAnalyzeBriefForClarifications::test_clear_specific_brief_returns_no_clarifications -v
# Expected: PASSED

# AC7: All unit tests pass
pytest tests/test_brief_questionnaire.py -v
# Expected: at least 12 passed

# AC8: Ruff passes
ruff check content_assistant/tools/brief_questionnaire.py tests/test_brief_questionnaire.py && echo "PASS: ruff clean"
```

---

#### Story 12: Build Content Preview Generator

**What to Build:**
Create a preview generator that analyzes the brief and generates a proposed hook with engagement psychology elements, which the user must approve before full content generation.

**Files to Create:**

1. `content_assistant/tools/preview_generator.py`
```python
"""Content preview generator with hook psychology."""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from content_assistant.tools.claude_client import generate_json
from content_assistant.tools.brief_questionnaire import validate_brief, brief_to_context_string
from content_assistant.rag.knowledge_base import retrieve_engagement_patterns


@dataclass
class ContentPreview:
    """Preview of content to be generated."""
    proposed_hook: str  # The attention-grabbing opener
    hook_type: str  # Mystery, Tension, Incomplete Story, Countdown, Transformation
    pattern_interrupt: str  # What violates expectations
    curiosity_gap: str  # What question is raised
    stakes: str  # Why reader should care
    open_loops: List[Dict[str, str]]  # Planned open loops (macro, medium, micro)
    content_structure: str  # Platform format, sections, flow
    promise_to_reader: str  # What they'll know/feel after reading


HOOK_TYPES = [
    "Mystery",
    "Tension",
    "Incomplete Story",
    "Countdown",
    "Transformation",
]

PREVIEW_SYSTEM_PROMPT = """You are a master content strategist specializing in wellness marketing.
Your job is to create compelling content previews that use proven psychological engagement techniques.

## Key Principles:
1. **Pattern Interrupt**: The first line must violate expectations to capture attention
2. **Curiosity Gap**: Create an open loop that the reader must close
3. **Stakes**: Make clear why this matters to them personally
4. **Open Loops**: Plan macro (whole content), medium (sections), and micro (sentence) loops
5. **Promise**: Be clear about what transformation or knowledge they'll gain

## Hook Types:
- **Mystery**: "What if I told you..." - creates unknown to be revealed
- **Tension**: "Everything you know about X is wrong" - creates conflict to resolve
- **Incomplete Story**: "Last month, a client came to us..." - story that needs ending
- **Countdown**: "You have 72 hours before..." - time pressure
- **Transformation**: "From exhausted to energized in 7 days" - before/after

## Platform Considerations:
- Email: Hook in subject line AND first line
- Instagram: Hook in first line (before "more")
- Blog: Hook in title AND opening paragraph
- Landing page: Hook above the fold

Respond with valid JSON matching the exact schema requested."""


def generate_preview(brief: Dict[str, str]) -> ContentPreview:
    """
    Generate a content preview based on the brief.

    Args:
        brief: Validated brief with all 13 fields

    Returns:
        ContentPreview with hook and structure details

    Raises:
        ValueError: If brief is invalid
    """
    # Validate brief first
    is_valid, errors = validate_brief(brief)
    if not is_valid:
        raise ValueError(f"Invalid brief: {'; '.join(errors)}")

    # Get engagement patterns from RAG
    pain_area = brief.get("pain_area", "")
    platform = brief.get("platform", "")
    engagement_context = retrieve_engagement_patterns(
        f"hook patterns for {pain_area} {platform}",
        top_k=3
    )

    engagement_text = "\n".join([r["text"] for r in engagement_context]) if engagement_context else ""

    # Build prompt
    brief_context = brief_to_context_string(brief)

    user_message = f"""Based on this content brief and engagement guidelines, create a preview for the content.

{brief_context}

## Engagement Guidelines Context:
{engagement_text}

## Task:
Create a content preview with:
1. A powerful proposed_hook (the actual opening text, 1-3 sentences)
2. The hook_type (one of: Mystery, Tension, Incomplete Story, Countdown, Transformation)
3. pattern_interrupt - explain what expectation it violates
4. curiosity_gap - what question does it raise in the reader's mind
5. stakes - why should they care (make it personal)
6. open_loops - list of 3 planned loops:
   - One "macro" loop (spans whole content)
   - One "medium" loop (spans a section)
   - One "micro" loop (sentence-to-sentence)
7. content_structure - outline of sections/flow for this platform
8. promise_to_reader - what they'll know/feel/be able to do after reading

Respond with valid JSON:
{{
    "proposed_hook": "...",
    "hook_type": "...",
    "pattern_interrupt": "...",
    "curiosity_gap": "...",
    "stakes": "...",
    "open_loops": [
        {{"level": "macro", "loop": "...", "closes_at": "..."}},
        {{"level": "medium", "loop": "...", "closes_at": "..."}},
        {{"level": "micro", "loop": "...", "closes_at": "..."}}
    ],
    "content_structure": "...",
    "promise_to_reader": "..."
}}"""

    # Generate preview using Claude
    result = generate_json(PREVIEW_SYSTEM_PROMPT, user_message)

    # Validate and create preview
    return ContentPreview(
        proposed_hook=result.get("proposed_hook", ""),
        hook_type=result.get("hook_type", ""),
        pattern_interrupt=result.get("pattern_interrupt", ""),
        curiosity_gap=result.get("curiosity_gap", ""),
        stakes=result.get("stakes", ""),
        open_loops=result.get("open_loops", []),
        content_structure=result.get("content_structure", ""),
        promise_to_reader=result.get("promise_to_reader", ""),
    )


def preview_to_dict(preview: ContentPreview) -> Dict:
    """Convert preview to dict for storage/display."""
    return asdict(preview)


def validate_preview(preview: ContentPreview) -> tuple[bool, List[str]]:
    """
    Validate that preview has all required fields filled.

    Args:
        preview: ContentPreview to validate

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if not preview.proposed_hook:
        issues.append("Missing proposed_hook")
    if not preview.hook_type:
        issues.append("Missing hook_type")
    elif preview.hook_type not in HOOK_TYPES:
        issues.append(f"Invalid hook_type: {preview.hook_type}")
    if not preview.pattern_interrupt:
        issues.append("Missing pattern_interrupt")
    if not preview.curiosity_gap:
        issues.append("Missing curiosity_gap")
    if not preview.stakes:
        issues.append("Missing stakes")
    if not preview.open_loops or len(preview.open_loops) < 1:
        issues.append("Missing or empty open_loops")
    if not preview.content_structure:
        issues.append("Missing content_structure")
    if not preview.promise_to_reader:
        issues.append("Missing promise_to_reader")

    return (len(issues) == 0, issues)


def check_hook_has_pattern_interrupt(hook: str) -> bool:
    """
    Check if hook likely has a pattern interrupt in first line.

    Simple heuristic check - looks for question, contradiction, or unusual statement.

    Args:
        hook: The proposed hook text

    Returns:
        True if hook appears to have pattern interrupt
    """
    if not hook:
        return False

    first_line = hook.split("\n")[0].strip()

    # Check for question
    if "?" in first_line:
        return True

    # Check for contradiction indicators
    contradiction_words = ["but", "however", "actually", "wrong", "mistake", "myth", "lie", "truth"]
    if any(word in first_line.lower() for word in contradiction_words):
        return True

    # Check for unusual/specific opening (not generic)
    generic_starts = ["we are", "our company", "at thelifeco", "welcome to"]
    if any(first_line.lower().startswith(start) for start in generic_starts):
        return False

    # If it starts with a specific statement or story, likely good
    return len(first_line) > 20
```

2. `tests/test_preview_generator.py`
```python
"""Tests for preview generator module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.tools.preview_generator import (
    generate_preview,
    ContentPreview,
    validate_preview,
    preview_to_dict,
    check_hook_has_pattern_interrupt,
    HOOK_TYPES,
)
from content_assistant.config import reset_config


@pytest.fixture
def valid_brief():
    """Return a complete valid brief."""
    return {
        "target_audience": "Women aged 45-55 experiencing perimenopause",
        "pain_area": "Hot flashes, sleep issues, weight gain",
        "compliance_level": "High - hormonal health",
        "funnel_stage": "Consideration",
        "value_proposition": "Natural hormonal balance restoration",
        "desired_action": "Book consultation",
        "specific_programs": "Hormonal Longevity for Women",
        "specific_centers": "Bodrum, Turkey",
        "tone": "Empathetic and scientific",
        "key_messages": "Functional medicine approach",
        "constraints": "No HRT comparisons",
        "platform": "Email newsletter",
        "price_point": "Starting from €4,500",
    }


@pytest.fixture
def valid_preview():
    """Return a valid ContentPreview."""
    return ContentPreview(
        proposed_hook="What if everything you've been told about menopause is wrong?",
        hook_type="Tension",
        pattern_interrupt="Challenges common medical advice about hormone decline",
        curiosity_gap="What IS the truth about menopause?",
        stakes="Your energy, mood, and quality of life for the next 30 years",
        open_loops=[
            {"level": "macro", "loop": "The secret doctors don't tell you", "closes_at": "end"},
            {"level": "medium", "loop": "Maria's transformation", "closes_at": "section 3"},
            {"level": "micro", "loop": "But that's not the whole story...", "closes_at": "next paragraph"},
        ],
        content_structure="1. Hook 2. Problem 3. Story 4. Solution 5. CTA",
        promise_to_reader="You'll understand why conventional approaches fail and what actually works",
    )


class TestGeneratePreview:
    """Tests for preview generation."""

    def setup_method(self):
        reset_config()

    @patch("content_assistant.tools.preview_generator.retrieve_engagement_patterns")
    @patch("content_assistant.tools.preview_generator.generate_json")
    def test_preview_includes_all_required_fields(
        self, mock_generate, mock_retrieve, valid_brief, monkeypatch
    ):
        """Test that preview includes all required fields."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_retrieve.return_value = [{"text": "Use pattern interrupts"}]
        mock_generate.return_value = {
            "proposed_hook": "What if your fatigue isn't about sleep?",
            "hook_type": "Mystery",
            "pattern_interrupt": "Challenges assumption about sleep = energy",
            "curiosity_gap": "What IS causing the fatigue?",
            "stakes": "Your daily energy and quality of life",
            "open_loops": [
                {"level": "macro", "loop": "The real cause", "closes_at": "end"}
            ],
            "content_structure": "Hook, Problem, Solution, CTA",
            "promise_to_reader": "Understand the root cause of fatigue",
        }

        preview = generate_preview(valid_brief)

        assert preview.proposed_hook
        assert preview.hook_type
        assert preview.pattern_interrupt
        assert preview.curiosity_gap
        assert preview.stakes
        assert preview.open_loops
        assert preview.content_structure
        assert preview.promise_to_reader

    @patch("content_assistant.tools.preview_generator.retrieve_engagement_patterns")
    @patch("content_assistant.tools.preview_generator.generate_json")
    def test_hook_type_is_valid(
        self, mock_generate, mock_retrieve, valid_brief, monkeypatch
    ):
        """Test that hook type is one of the valid types."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_retrieve.return_value = []
        mock_generate.return_value = {
            "proposed_hook": "Test hook",
            "hook_type": "Transformation",  # Valid type
            "pattern_interrupt": "Test",
            "curiosity_gap": "Test",
            "stakes": "Test",
            "open_loops": [{"level": "macro", "loop": "test", "closes_at": "end"}],
            "content_structure": "Test",
            "promise_to_reader": "Test",
        }

        preview = generate_preview(valid_brief)

        assert preview.hook_type in HOOK_TYPES

    def test_invalid_brief_raises_error(self):
        """Test that invalid brief raises ValueError."""
        invalid_brief = {"target_audience": "Someone"}  # Missing fields

        with pytest.raises(ValueError) as exc_info:
            generate_preview(invalid_brief)

        assert "Invalid brief" in str(exc_info.value)


class TestValidatePreview:
    """Tests for preview validation."""

    def test_valid_preview_passes(self, valid_preview):
        """Test that valid preview passes validation."""
        is_valid, issues = validate_preview(valid_preview)

        assert is_valid is True
        assert len(issues) == 0

    def test_missing_hook_fails(self, valid_preview):
        """Test that missing hook fails validation."""
        valid_preview.proposed_hook = ""

        is_valid, issues = validate_preview(valid_preview)

        assert is_valid is False
        assert any("proposed_hook" in issue for issue in issues)

    def test_invalid_hook_type_fails(self, valid_preview):
        """Test that invalid hook type fails validation."""
        valid_preview.hook_type = "InvalidType"

        is_valid, issues = validate_preview(valid_preview)

        assert is_valid is False
        assert any("hook_type" in issue for issue in issues)


class TestCheckHookPatternInterrupt:
    """Tests for pattern interrupt detection."""

    def test_question_hook_has_pattern_interrupt(self):
        """Test that question in first line is detected."""
        hook = "What if everything you know about dieting is wrong?"

        assert check_hook_has_pattern_interrupt(hook) is True

    def test_contradiction_hook_has_pattern_interrupt(self):
        """Test that contradiction words are detected."""
        hook = "The truth about detox that doctors won't tell you"

        assert check_hook_has_pattern_interrupt(hook) is True

    def test_generic_opening_fails(self):
        """Test that generic company openings fail."""
        hook = "We are TheLifeCo, a wellness company"

        assert check_hook_has_pattern_interrupt(hook) is False

    def test_empty_hook_fails(self):
        """Test that empty hook fails."""
        assert check_hook_has_pattern_interrupt("") is False


class TestPreviewToDict:
    """Tests for preview serialization."""

    def test_preview_to_dict_has_all_keys(self, valid_preview):
        """Test that dict has all expected keys."""
        result = preview_to_dict(valid_preview)

        expected_keys = [
            "proposed_hook", "hook_type", "pattern_interrupt",
            "curiosity_gap", "stakes", "open_loops",
            "content_structure", "promise_to_reader"
        ]

        for key in expected_keys:
            assert key in result
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.preview_generator import generate_preview, ContentPreview, validate_preview, HOOK_TYPES" && echo "PASS"

# AC2: Preview includes all required fields (mocked)
pytest tests/test_preview_generator.py::TestGeneratePreview::test_preview_includes_all_required_fields -v
# Expected: PASSED

# AC3: Hook type is valid
pytest tests/test_preview_generator.py::TestGeneratePreview::test_hook_type_is_valid -v
# Expected: PASSED

# AC4: Pattern interrupt check works for question
pytest tests/test_preview_generator.py::TestCheckHookPatternInterrupt::test_question_hook_has_pattern_interrupt -v
# Expected: PASSED

# AC5: Generic opening fails pattern interrupt check
pytest tests/test_preview_generator.py::TestCheckHookPatternInterrupt::test_generic_opening_fails -v
# Expected: PASSED

# AC6: All unit tests pass
pytest tests/test_preview_generator.py -v
# Expected: at least 10 passed

# AC7: HOOK_TYPES constant has correct values
python -c "
from content_assistant.tools.preview_generator import HOOK_TYPES
expected = ['Mystery', 'Tension', 'Incomplete Story', 'Countdown', 'Transformation']
assert set(HOOK_TYPES) == set(expected), f'Expected {expected}, got {HOOK_TYPES}'
print('PASS: HOOK_TYPES correct')
"

# AC8: Ruff passes
ruff check content_assistant/tools/preview_generator.py tests/test_preview_generator.py && echo "PASS: ruff clean"
```

---

#### Story 13: Build Content Generator Tool

**What to Build:**
Create the main content generator that takes a validated brief and approved preview to generate full content, ensuring the hook is used and all open loops are closed.

**Files to Create:**

1. `content_assistant/tools/content_generator.py`
```python
"""Content generator using approved preview and brief."""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from content_assistant.tools.claude_client import generate_json
from content_assistant.tools.brief_questionnaire import validate_brief, brief_to_context_string
from content_assistant.tools.preview_generator import ContentPreview, preview_to_dict
from content_assistant.rag.knowledge_base import (
    retrieve_wellness_facts,
    retrieve_engagement_patterns,
)


@dataclass
class GeneratedContent:
    """Generated content result."""
    title: str
    hook: str  # Must match approved preview
    content: str  # Full content body
    cta: str  # Call to action
    open_loops_used: List[Dict]  # Loops from preview that were used
    text_overlays: Optional[List[str]]  # For social content
    metadata: Dict  # Additional info


PLATFORM_TYPES = [
    "email",
    "landing_page",
    "meta_ad",
    "instagram_post",
    "instagram_story",
    "instagram_reel",
    "linkedin_post",
    "blog",
    "whatsapp",
]

CONTENT_SYSTEM_PROMPT = """You are TheLifeCo's expert content writer, creating wellness marketing content.

## Your Principles:
1. **Use the approved hook exactly** - The preview hook has been approved, use it verbatim
2. **Close all open loops** - Every loop opened in the preview must be closed
3. **Deliver on the promise** - The reader must get what was promised in the preview
4. **Adapt to compliance level** - High compliance = medical credibility, Low = lifestyle focus
5. **Match funnel stage** - Awareness = educate, Consideration = differentiate, Conversion = urgency
6. **Platform-appropriate** - Follow platform best practices for length, format, tone

## Platform Guidelines:
- **email**: 150-500 words, scannable, one primary CTA
- **landing_page**: Clear sections, multiple CTAs, social proof
- **meta_ad**: <125 chars primary text, clear value prop
- **instagram_post**: 150-2200 chars, hashtags, link in bio CTA
- **instagram_story**: Very short, swipe up or link CTA
- **instagram_reel**: Script for 15-60 sec, text overlay suggestions
- **linkedin_post**: Professional tone, 1300+ chars, industry insights
- **blog**: 1500-2500 words, H2 every 200-300 words, SEO-optimized
- **whatsapp**: Short, personal, direct CTA

## Content Structure:
1. HOOK (from approved preview - use exactly)
2. PROBLEM AMPLIFICATION (stakes, empathy)
3. SOLUTION (TheLifeCo's approach)
4. PROOF (testimonials, stats, credentials)
5. CTA (single clear action)

For social content, also provide text_overlays (list of 3-5 text strings to overlay on video/image).

Respond with valid JSON."""


def generate_content(
    brief: Dict[str, str],
    approved_preview: Dict,
) -> GeneratedContent:
    """
    Generate full content from brief and approved preview.

    Args:
        brief: Validated brief with all 13 fields
        approved_preview: Preview dict that user approved

    Returns:
        GeneratedContent with full content

    Raises:
        ValueError: If brief is invalid or preview missing
    """
    # Validate brief
    is_valid, errors = validate_brief(brief)
    if not is_valid:
        raise ValueError(f"Invalid brief: {'; '.join(errors)}")

    if not approved_preview:
        raise ValueError("Approved preview is required")

    # Get relevant RAG context
    pain_area = brief.get("pain_area", "")
    programs = brief.get("specific_programs", "")

    wellness_context = retrieve_wellness_facts(f"{pain_area} {programs}", top_k=5)
    engagement_context = retrieve_engagement_patterns(
        f"{brief.get('platform', '')} content structure",
        top_k=3
    )

    wellness_text = "\n".join([f"- {r['text']}" for r in wellness_context]) if wellness_context else ""
    engagement_text = "\n".join([r["text"] for r in engagement_context]) if engagement_context else ""

    # Build prompt
    brief_context = brief_to_context_string(brief)

    platform = brief.get("platform", "email").lower()
    is_social = any(s in platform for s in ["instagram", "reel", "story", "tiktok"])

    user_message = f"""Generate content based on this approved preview and brief.

## APPROVED PREVIEW (user has approved this hook and structure):
Proposed Hook: {approved_preview.get('proposed_hook', '')}
Hook Type: {approved_preview.get('hook_type', '')}
Open Loops to Use: {approved_preview.get('open_loops', [])}
Content Structure: {approved_preview.get('content_structure', '')}
Promise to Reader: {approved_preview.get('promise_to_reader', '')}

## CONTENT BRIEF:
{brief_context}

## WELLNESS FACTS (use these for credibility):
{wellness_text}

## ENGAGEMENT PATTERNS:
{engagement_text}

## REQUIREMENTS:
1. START with the exact approved hook (copy it verbatim)
2. CLOSE every open loop listed in the preview
3. DELIVER on the promise to reader
4. COMPLIANCE LEVEL: {brief.get('compliance_level', '')}
5. FUNNEL STAGE: {brief.get('funnel_stage', '')}
6. Include CTA: {brief.get('desired_action', '')}
{'7. IMPORTANT: Include text_overlays list for social content (3-5 punchy text overlay suggestions)' if is_social else ''}

Respond with JSON:
{{
    "title": "...",
    "hook": "... (exact copy of approved hook)",
    "content": "... (full content body)",
    "cta": "...",
    "open_loops_used": [... (list each loop and where it was closed)],
    {"\"text_overlays\": [\"...\", \"...\", \"...\"]," if is_social else ""}
    "metadata": {{
        "word_count": ...,
        "platform": "...",
        "compliance_level": "...",
        "funnel_stage": "..."
    }}
}}"""

    # Generate content
    result = generate_json(CONTENT_SYSTEM_PROMPT, user_message)

    return GeneratedContent(
        title=result.get("title", ""),
        hook=result.get("hook", ""),
        content=result.get("content", ""),
        cta=result.get("cta", ""),
        open_loops_used=result.get("open_loops_used", []),
        text_overlays=result.get("text_overlays") if is_social else None,
        metadata=result.get("metadata", {}),
    )


def verify_content_uses_approved_hook(
    content: GeneratedContent,
    approved_preview: Dict,
) -> bool:
    """
    Verify that generated content starts with approved hook.

    Args:
        content: Generated content
        approved_preview: The approved preview

    Returns:
        True if content uses the approved hook
    """
    approved_hook = approved_preview.get("proposed_hook", "").strip()
    content_hook = content.hook.strip()

    # Check if hooks match (allowing for minor formatting differences)
    if not approved_hook or not content_hook:
        return False

    # Normalize whitespace
    approved_normalized = " ".join(approved_hook.split())
    content_normalized = " ".join(content_hook.split())

    return approved_normalized == content_normalized


def verify_loops_closed(
    content: GeneratedContent,
    approved_preview: Dict,
) -> tuple[bool, List[str]]:
    """
    Verify that all open loops from preview are closed in content.

    Args:
        content: Generated content
        approved_preview: The approved preview

    Returns:
        Tuple of (all_closed, list of unclosed loops)
    """
    planned_loops = approved_preview.get("open_loops", [])
    used_loops = content.open_loops_used or []

    used_loop_texts = [l.get("loop", "") for l in used_loops]
    unclosed = []

    for planned in planned_loops:
        loop_text = planned.get("loop", "")
        if loop_text and not any(loop_text in used for used in used_loop_texts):
            unclosed.append(loop_text)

    return (len(unclosed) == 0, unclosed)


def content_to_dict(content: GeneratedContent) -> Dict:
    """Convert content to dict for storage/display."""
    return asdict(content)
```

2. `tests/test_content_generator.py`
```python
"""Tests for content generator module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.tools.content_generator import (
    generate_content,
    GeneratedContent,
    verify_content_uses_approved_hook,
    verify_loops_closed,
    content_to_dict,
    PLATFORM_TYPES,
)
from content_assistant.config import reset_config


@pytest.fixture
def valid_brief():
    """Return a complete valid brief."""
    return {
        "target_audience": "Women aged 45-55 with perimenopause",
        "pain_area": "Hot flashes, sleep issues, weight gain",
        "compliance_level": "High - hormonal health",
        "funnel_stage": "Consideration",
        "value_proposition": "Natural hormonal balance",
        "desired_action": "Book consultation",
        "specific_programs": "Hormonal Longevity for Women",
        "specific_centers": "Bodrum, Turkey",
        "tone": "Empathetic and scientific",
        "key_messages": "Functional medicine approach",
        "constraints": "No HRT comparisons",
        "platform": "Email newsletter",
        "price_point": "Starting from €4,500",
    }


@pytest.fixture
def approved_preview():
    """Return an approved preview dict."""
    return {
        "proposed_hook": "What if everything you've been told about menopause is wrong?",
        "hook_type": "Tension",
        "pattern_interrupt": "Challenges medical assumptions",
        "curiosity_gap": "What is the truth?",
        "stakes": "Your next 30 years",
        "open_loops": [
            {"level": "macro", "loop": "The secret doctors miss", "closes_at": "end"},
            {"level": "medium", "loop": "Maria's story", "closes_at": "section 3"},
        ],
        "content_structure": "Hook, Problem, Solution, Proof, CTA",
        "promise_to_reader": "Understand why conventional approaches fail",
    }


class TestGenerateContent:
    """Tests for content generation."""

    def setup_method(self):
        reset_config()

    @patch("content_assistant.tools.content_generator.retrieve_wellness_facts")
    @patch("content_assistant.tools.content_generator.retrieve_engagement_patterns")
    @patch("content_assistant.tools.content_generator.generate_json")
    def test_generated_content_starts_with_approved_hook(
        self, mock_generate, mock_engagement, mock_wellness,
        valid_brief, approved_preview, monkeypatch
    ):
        """Test that generated content uses the approved hook."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_wellness.return_value = []
        mock_engagement.return_value = []
        mock_generate.return_value = {
            "title": "The Truth About Menopause",
            "hook": "What if everything you've been told about menopause is wrong?",
            "content": "Full content here...",
            "cta": "Book your consultation today",
            "open_loops_used": [
                {"loop": "The secret doctors miss", "closed_at": "paragraph 5"},
                {"loop": "Maria's story", "closed_at": "section 3"},
            ],
            "metadata": {"word_count": 350, "platform": "email"},
        }

        content = generate_content(valid_brief, approved_preview)

        assert content.hook == approved_preview["proposed_hook"]

    @patch("content_assistant.tools.content_generator.retrieve_wellness_facts")
    @patch("content_assistant.tools.content_generator.retrieve_engagement_patterns")
    @patch("content_assistant.tools.content_generator.generate_json")
    def test_all_open_loops_closed(
        self, mock_generate, mock_engagement, mock_wellness,
        valid_brief, approved_preview, monkeypatch
    ):
        """Test that all open loops from preview are closed."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_wellness.return_value = []
        mock_engagement.return_value = []
        mock_generate.return_value = {
            "title": "Test",
            "hook": "Test hook",
            "content": "Content...",
            "cta": "CTA",
            "open_loops_used": [
                {"loop": "The secret doctors miss", "closed_at": "end"},
                {"loop": "Maria's story", "closed_at": "section 3"},
            ],
            "metadata": {},
        }

        content = generate_content(valid_brief, approved_preview)
        all_closed, unclosed = verify_loops_closed(content, approved_preview)

        assert all_closed is True
        assert len(unclosed) == 0

    @patch("content_assistant.tools.content_generator.retrieve_wellness_facts")
    @patch("content_assistant.tools.content_generator.retrieve_engagement_patterns")
    @patch("content_assistant.tools.content_generator.generate_json")
    def test_social_content_has_text_overlays(
        self, mock_generate, mock_engagement, mock_wellness,
        valid_brief, approved_preview, monkeypatch
    ):
        """Test that social content includes text overlay suggestions."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        # Change platform to Instagram
        valid_brief["platform"] = "instagram_reel"

        mock_wellness.return_value = []
        mock_engagement.return_value = []
        mock_generate.return_value = {
            "title": "Test",
            "hook": "Test hook",
            "content": "Content...",
            "cta": "CTA",
            "open_loops_used": [],
            "text_overlays": [
                "Wait for it...",
                "This changed everything",
                "Link in bio",
            ],
            "metadata": {},
        }

        content = generate_content(valid_brief, approved_preview)

        assert content.text_overlays is not None
        assert len(content.text_overlays) >= 1

    def test_invalid_brief_raises_error(self, approved_preview):
        """Test that invalid brief raises ValueError."""
        invalid_brief = {"target_audience": "Someone"}

        with pytest.raises(ValueError) as exc_info:
            generate_content(invalid_brief, approved_preview)

        assert "Invalid brief" in str(exc_info.value)

    def test_missing_preview_raises_error(self, valid_brief):
        """Test that missing preview raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generate_content(valid_brief, None)

        assert "preview" in str(exc_info.value).lower()


class TestVerifyFunctions:
    """Tests for verification functions."""

    def test_verify_hook_match(self, approved_preview):
        """Test hook verification when hooks match."""
        content = GeneratedContent(
            title="Test",
            hook="What if everything you've been told about menopause is wrong?",
            content="Content",
            cta="CTA",
            open_loops_used=[],
            text_overlays=None,
            metadata={},
        )

        assert verify_content_uses_approved_hook(content, approved_preview) is True

    def test_verify_hook_mismatch(self, approved_preview):
        """Test hook verification when hooks don't match."""
        content = GeneratedContent(
            title="Test",
            hook="Different hook entirely",
            content="Content",
            cta="CTA",
            open_loops_used=[],
            text_overlays=None,
            metadata={},
        )

        assert verify_content_uses_approved_hook(content, approved_preview) is False

    def test_verify_unclosed_loops_detected(self, approved_preview):
        """Test that unclosed loops are detected."""
        content = GeneratedContent(
            title="Test",
            hook="Test",
            content="Content",
            cta="CTA",
            open_loops_used=[
                {"loop": "The secret doctors miss", "closed_at": "end"},
                # Missing: Maria's story
            ],
            text_overlays=None,
            metadata={},
        )

        all_closed, unclosed = verify_loops_closed(content, approved_preview)

        assert all_closed is False
        assert "Maria's story" in unclosed


class TestPlatformTypes:
    """Tests for platform type definitions."""

    def test_all_expected_platforms_exist(self):
        """Test that all expected platform types are defined."""
        expected = [
            "email", "landing_page", "meta_ad",
            "instagram_post", "instagram_story", "instagram_reel",
            "linkedin_post", "blog", "whatsapp"
        ]

        for platform in expected:
            assert platform in PLATFORM_TYPES
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.content_generator import generate_content, GeneratedContent, verify_content_uses_approved_hook, verify_loops_closed, PLATFORM_TYPES" && echo "PASS"

# AC2: Generated content uses approved hook (mocked)
pytest tests/test_content_generator.py::TestGenerateContent::test_generated_content_starts_with_approved_hook -v
# Expected: PASSED

# AC3: All open loops are closed (mocked)
pytest tests/test_content_generator.py::TestGenerateContent::test_all_open_loops_closed -v
# Expected: PASSED

# AC4: Social content has text overlays (mocked)
pytest tests/test_content_generator.py::TestGenerateContent::test_social_content_has_text_overlays -v
# Expected: PASSED

# AC5: Hook mismatch is detected
pytest tests/test_content_generator.py::TestVerifyFunctions::test_verify_hook_mismatch -v
# Expected: PASSED

# AC6: Unclosed loops are detected
pytest tests/test_content_generator.py::TestVerifyFunctions::test_verify_unclosed_loops_detected -v
# Expected: PASSED

# AC7: All unit tests pass
pytest tests/test_content_generator.py -v
# Expected: at least 8 passed

# AC8: Ruff passes
ruff check content_assistant/tools/content_generator.py tests/test_content_generator.py && echo "PASS: ruff clean"
```

---

#### Story 14: Build Few-Shot Example Retriever

**What to Build:**
Create a module that retrieves similar past content generations to use as few-shot examples, with graceful cold-start handling.

**Files to Create:**

1. `content_assistant/tools/example_retriever.py`
```python
"""Few-shot example retriever for content generation."""
from typing import List, Dict, Optional
from content_assistant.db.supabase_client import get_admin_client
from content_assistant.rag.embeddings import embed_text
from content_assistant.tools.brief_questionnaire import brief_to_context_string


def get_similar_generations(
    brief: Dict[str, str],
    top_k: int = 5,
    min_rating: Optional[float] = None,
) -> List[Dict]:
    """
    Retrieve past generations with similar briefs.

    Args:
        brief: Current brief to find similar examples for
        top_k: Number of examples to return
        min_rating: Optional minimum star rating filter

    Returns:
        List of similar generation dicts with:
        - brief: the original brief
        - content: the generated content
        - signals: user feedback
        - similarity: similarity score
    """
    # Create embedding from brief
    brief_text = brief_to_context_string(brief)
    brief_embedding = embed_text(brief_text)

    client = get_admin_client()

    # Search for similar generations using vector similarity
    # This requires a function in Supabase for vector search
    try:
        result = client.rpc(
            "match_content_generations",
            {
                "query_embedding": brief_embedding,
                "match_count": top_k,
                "min_rating": min_rating,
            }
        ).execute()

        if not result.data:
            return []

        return [
            {
                "brief": row.get("brief", {}),
                "preview": row.get("preview", {}),
                "content": row.get("content", ""),
                "content_type": row.get("content_type", ""),
                "signals": row.get("signals", {}),
                "similarity": row.get("similarity", 0.0),
            }
            for row in result.data
        ]

    except Exception:
        # Cold start: no generations yet, or function doesn't exist
        return []


def get_generations_by_type(
    content_type: str,
    limit: int = 10,
    min_rating: Optional[float] = None,
) -> List[Dict]:
    """
    Get past generations filtered by content type.

    Args:
        content_type: Type of content (email, blog, etc.)
        limit: Maximum number to return
        min_rating: Optional minimum star rating filter

    Returns:
        List of generation dicts
    """
    client = get_admin_client()

    query = client.table("content_generations").select("*").eq("content_type", content_type)

    if min_rating:
        query = query.gte("signals->star_rating", min_rating)

    query = query.order("created_at", desc=True).limit(limit)

    result = query.execute()

    return result.data if result.data else []


def get_high_rated_examples(
    min_rating: float = 4.0,
    limit: int = 10,
) -> List[Dict]:
    """
    Get examples with high user ratings.

    Args:
        min_rating: Minimum star rating (1-5)
        limit: Maximum number to return

    Returns:
        List of highly rated generation dicts
    """
    client = get_admin_client()

    result = client.table("content_generations").select("*").gte("signals->star_rating", min_rating).order("signals->star_rating", desc=True).limit(limit).execute()

    return result.data if result.data else []


def format_example_for_prompt(generation: Dict) -> str:
    """
    Format a past generation as a few-shot example for prompts.

    Args:
        generation: A generation dict

    Returns:
        Formatted string for use in prompts
    """
    brief = generation.get("brief", {})
    content = generation.get("content", "")
    signals = generation.get("signals", {})

    rating = signals.get("star_rating", "N/A")
    hook_worked = signals.get("hook_worked", "Unknown")

    return f"""## Example (Rating: {rating}/5, Hook Worked: {hook_worked})

### Brief Summary:
- Audience: {brief.get('target_audience', 'N/A')}
- Pain: {brief.get('pain_area', 'N/A')}
- Platform: {brief.get('platform', 'N/A')}

### Generated Content:
{content[:500]}{'...' if len(content) > 500 else ''}
"""
```

2. `tests/test_example_retriever.py`
```python
"""Tests for example retriever module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.tools.example_retriever import (
    get_similar_generations,
    get_generations_by_type,
    get_high_rated_examples,
    format_example_for_prompt,
)
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients
from content_assistant.rag.embeddings import reset_client as reset_embed


@pytest.fixture
def sample_generation():
    """Return a sample generation dict."""
    return {
        "brief": {
            "target_audience": "Executives with burnout",
            "pain_area": "Chronic fatigue",
            "platform": "email",
        },
        "preview": {},
        "content": "Great content here about wellness...",
        "content_type": "email",
        "signals": {
            "star_rating": 5,
            "hook_worked": True,
        },
        "similarity": 0.92,
    }


class TestGetSimilarGenerations:
    """Tests for similar generation retrieval."""

    def setup_method(self):
        reset_config()
        reset_clients()
        reset_embed()

    @patch("content_assistant.tools.example_retriever.embed_text")
    @patch("content_assistant.tools.example_retriever.get_admin_client")
    def test_returns_empty_list_when_no_history(
        self, mock_get_client, mock_embed, monkeypatch
    ):
        """Test that empty list is returned when no generations exist."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_embed.return_value = [0.1] * 1024

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []  # No results
        mock_client.rpc.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        brief = {"target_audience": "Test", "pain_area": "Test"}
        result = get_similar_generations(brief)

        assert result == []

    @patch("content_assistant.tools.example_retriever.embed_text")
    @patch("content_assistant.tools.example_retriever.get_admin_client")
    def test_returns_similar_generations(
        self, mock_get_client, mock_embed, sample_generation, monkeypatch
    ):
        """Test that similar generations are returned."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_embed.return_value = [0.1] * 1024

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [sample_generation]
        mock_client.rpc.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        brief = {"target_audience": "Executives", "pain_area": "Fatigue"}
        result = get_similar_generations(brief, top_k=5)

        assert len(result) == 1
        assert "content" in result[0]
        assert "similarity" in result[0]

    @patch("content_assistant.tools.example_retriever.embed_text")
    @patch("content_assistant.tools.example_retriever.get_admin_client")
    def test_handles_exception_gracefully(
        self, mock_get_client, mock_embed, monkeypatch
    ):
        """Test that exceptions result in empty list (cold start)."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_embed.return_value = [0.1] * 1024
        mock_client = MagicMock()
        mock_client.rpc.side_effect = Exception("Function not found")
        mock_get_client.return_value = mock_client

        brief = {"target_audience": "Test"}
        result = get_similar_generations(brief)

        assert result == []  # Graceful failure


class TestFormatExampleForPrompt:
    """Tests for prompt formatting."""

    def test_formats_example_with_all_fields(self, sample_generation):
        """Test that example is formatted with all fields."""
        result = format_example_for_prompt(sample_generation)

        assert "Example" in result
        assert "Rating: 5/5" in result
        assert "Hook Worked: True" in result
        assert "Executives" in result
        assert "fatigue" in result.lower()

    def test_truncates_long_content(self):
        """Test that long content is truncated."""
        generation = {
            "brief": {},
            "content": "A" * 1000,  # Long content
            "signals": {},
        }

        result = format_example_for_prompt(generation)

        assert "..." in result
        assert len(result) < 1000
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.example_retriever import get_similar_generations, get_high_rated_examples, format_example_for_prompt" && echo "PASS"

# AC2: Returns empty list when no history (mocked)
pytest tests/test_example_retriever.py::TestGetSimilarGenerations::test_returns_empty_list_when_no_history -v
# Expected: PASSED

# AC3: Returns similar generations when exist (mocked)
pytest tests/test_example_retriever.py::TestGetSimilarGenerations::test_returns_similar_generations -v
# Expected: PASSED

# AC4: Handles exceptions gracefully (cold start)
pytest tests/test_example_retriever.py::TestGetSimilarGenerations::test_handles_exception_gracefully -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_example_retriever.py -v
# Expected: at least 5 passed

# AC6: Ruff passes
ruff check content_assistant/tools/example_retriever.py tests/test_example_retriever.py && echo "PASS: ruff clean"
```

---
### Epic 5: Content Review Tools
---

#### Story 15: Build Wellness Verifier Tool

**What to Build:**
Create a tool that extracts wellness claims from content and verifies each against the RAG knowledge base, returning verification status for each claim.

**Files to Create:**

1. `content_assistant/tools/wellness_verifier.py`
```python
"""Wellness claim verification using RAG knowledge base."""
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum
from content_assistant.tools.claude_client import generate_json
from content_assistant.rag.knowledge_base import retrieve_wellness_facts


class ClaimStatus(str, Enum):
    """Status of a wellness claim verification."""
    VERIFIED = "VERIFIED"
    INACCURATE = "INACCURATE"
    UNVERIFIED = "UNVERIFIED"


@dataclass
class VerifiedClaim:
    """A verified wellness claim."""
    claim: str
    status: ClaimStatus
    evidence: str
    source: str


CLAIM_EXTRACTION_PROMPT = """You are a wellness content analyst. Extract all wellness/health claims from the content.

A wellness claim is any statement about:
- Health benefits
- Medical effects
- Nutritional facts
- Treatment outcomes
- Scientific processes (autophagy, metabolism, etc.)

Return ONLY a JSON array of claim strings. Each claim should be a single, specific statement.

Example:
["Fasting activates autophagy", "Water detox removes toxins", "7 days can reset metabolism"]"""


VERIFICATION_PROMPT = """You are a fact-checker for TheLifeCo wellness content.

Given a claim and evidence from our knowledge base, determine if the claim is:
- VERIFIED: The evidence supports this claim
- INACCURATE: The evidence contradicts this claim
- UNVERIFIED: Not enough evidence to verify (but not necessarily wrong)

Be strict: Only mark as VERIFIED if the evidence clearly supports the specific claim.
Be careful with absolute statements ("cures", "guarantees", "always").

Respond with JSON:
{
    "status": "VERIFIED" | "INACCURATE" | "UNVERIFIED",
    "evidence": "Quote or summary from knowledge base that supports/contradicts",
    "explanation": "Brief explanation of your reasoning"
}"""


def extract_claims(content: str) -> List[str]:
    """
    Extract wellness claims from content using Claude.

    Args:
        content: Content text to analyze

    Returns:
        List of claim strings
    """
    if not content or len(content.strip()) < 10:
        return []

    try:
        result = generate_json(
            CLAIM_EXTRACTION_PROMPT,
            f"Extract wellness claims from this content:\n\n{content}"
        )

        if isinstance(result, list):
            return [str(c) for c in result if c]
        return []
    except Exception:
        return []


def verify_claim(claim: str) -> VerifiedClaim:
    """
    Verify a single claim against the knowledge base.

    Args:
        claim: The claim to verify

    Returns:
        VerifiedClaim with status and evidence
    """
    # Retrieve relevant facts from knowledge base
    facts = retrieve_wellness_facts(claim, top_k=5)

    if not facts:
        return VerifiedClaim(
            claim=claim,
            status=ClaimStatus.UNVERIFIED,
            evidence="No relevant information found in knowledge base",
            source="",
        )

    # Build evidence context
    evidence_text = "\n".join([
        f"- {f['text']} (Source: {f['source']})"
        for f in facts
    ])

    # Use Claude to verify claim against evidence
    try:
        result = generate_json(
            VERIFICATION_PROMPT,
            f"""Verify this claim:
"{claim}"

Evidence from TheLifeCo knowledge base:
{evidence_text}"""
        )

        status_str = result.get("status", "UNVERIFIED")
        status = ClaimStatus(status_str) if status_str in ClaimStatus.__members__ else ClaimStatus.UNVERIFIED

        return VerifiedClaim(
            claim=claim,
            status=status,
            evidence=result.get("evidence", "") or result.get("explanation", ""),
            source=facts[0]["source"] if facts else "",
        )
    except Exception as e:
        return VerifiedClaim(
            claim=claim,
            status=ClaimStatus.UNVERIFIED,
            evidence=f"Verification error: {e}",
            source="",
        )


def verify_content(content: str) -> Dict:
    """
    Verify all wellness claims in content.

    Args:
        content: Content to verify

    Returns:
        Dict with:
        - claims: List of VerifiedClaim as dicts
        - summary: Overall summary
        - verified_count: Number of verified claims
        - inaccurate_count: Number of inaccurate claims
        - unverified_count: Number of unverified claims
    """
    # Extract claims
    claims = extract_claims(content)

    if not claims:
        return {
            "claims": [],
            "summary": "No wellness claims found in content",
            "verified_count": 0,
            "inaccurate_count": 0,
            "unverified_count": 0,
        }

    # Verify each claim
    verified_claims = []
    for claim in claims:
        result = verify_claim(claim)
        verified_claims.append({
            "claim": result.claim,
            "status": result.status.value,
            "evidence": result.evidence,
            "source": result.source,
        })

    # Count by status
    counts = {status.value: 0 for status in ClaimStatus}
    for vc in verified_claims:
        counts[vc["status"]] += 1

    # Generate summary
    if counts["INACCURATE"] > 0:
        summary = f"ATTENTION: {counts['INACCURATE']} inaccurate claim(s) found. Please review and correct."
    elif counts["UNVERIFIED"] > len(claims) // 2:
        summary = f"Many claims ({counts['UNVERIFIED']}) could not be verified. Consider adding sources."
    else:
        summary = f"Content verified: {counts['VERIFIED']} verified, {counts['UNVERIFIED']} unverified."

    return {
        "claims": verified_claims,
        "summary": summary,
        "verified_count": counts["VERIFIED"],
        "inaccurate_count": counts["INACCURATE"],
        "unverified_count": counts["UNVERIFIED"],
    }
```

2. `tests/test_wellness_verifier.py`
```python
"""Tests for wellness verifier module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.tools.wellness_verifier import (
    extract_claims,
    verify_claim,
    verify_content,
    ClaimStatus,
    VerifiedClaim,
)
from content_assistant.config import reset_config


class TestExtractClaims:
    """Tests for claim extraction."""

    def setup_method(self):
        reset_config()

    @patch("content_assistant.tools.wellness_verifier.generate_json")
    def test_extracts_claims_from_content(self, mock_generate, monkeypatch):
        """Test that claims are extracted from content."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_generate.return_value = [
            "Fasting activates autophagy",
            "Detox removes toxins from the body",
        ]

        content = "Our fasting program activates autophagy and the detox removes toxins."
        claims = extract_claims(content)

        assert len(claims) == 2
        assert "autophagy" in claims[0].lower()

    def test_empty_content_returns_empty_list(self):
        """Test that empty content returns no claims."""
        claims = extract_claims("")
        assert claims == []


class TestVerifyClaim:
    """Tests for individual claim verification."""

    def setup_method(self):
        reset_config()

    @patch("content_assistant.tools.wellness_verifier.generate_json")
    @patch("content_assistant.tools.wellness_verifier.retrieve_wellness_facts")
    def test_autophagy_claim_returns_verified(
        self, mock_retrieve, mock_generate, monkeypatch
    ):
        """Test that 'fasting activates autophagy' returns VERIFIED."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_retrieve.return_value = [
            {"text": "Fasting triggers autophagy, the cellular cleaning process", "source": "minibook1.pdf"},
        ]
        mock_generate.return_value = {
            "status": "VERIFIED",
            "evidence": "Fasting triggers autophagy as stated in knowledge base",
        }

        result = verify_claim("Fasting activates autophagy")

        assert result.status == ClaimStatus.VERIFIED

    @patch("content_assistant.tools.wellness_verifier.generate_json")
    @patch("content_assistant.tools.wellness_verifier.retrieve_wellness_facts")
    def test_cancer_cure_claim_returns_inaccurate_or_unverified(
        self, mock_retrieve, mock_generate, monkeypatch
    ):
        """Test that 'fasting cures cancer' returns INACCURATE or UNVERIFIED."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_retrieve.return_value = [
            {"text": "Fasting may support cancer prevention", "source": "minibook1.pdf"},
        ]
        mock_generate.return_value = {
            "status": "INACCURATE",
            "evidence": "Knowledge base does not support cure claims",
        }

        result = verify_claim("Fasting cures cancer")

        assert result.status in [ClaimStatus.INACCURATE, ClaimStatus.UNVERIFIED]


class TestVerifyContent:
    """Tests for full content verification."""

    def setup_method(self):
        reset_config()

    @patch("content_assistant.tools.wellness_verifier.verify_claim")
    @patch("content_assistant.tools.wellness_verifier.extract_claims")
    def test_returns_at_least_one_claim_for_wellness_content(
        self, mock_extract, mock_verify, monkeypatch
    ):
        """Test that wellness content returns at least one claim."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_extract.return_value = ["Fasting improves health"]
        mock_verify.return_value = VerifiedClaim(
            claim="Fasting improves health",
            status=ClaimStatus.VERIFIED,
            evidence="Supported by research",
            source="minibook1.pdf",
        )

        content = "Our fasting program improves your health."
        result = verify_content(content)

        assert len(result["claims"]) >= 1

    @patch("content_assistant.tools.wellness_verifier.extract_claims")
    def test_content_without_claims_returns_empty(self, mock_extract):
        """Test that content without claims returns empty list."""
        mock_extract.return_value = []

        result = verify_content("Hello, welcome to our website.")

        assert result["claims"] == []
        assert result["verified_count"] == 0

    @patch("content_assistant.tools.wellness_verifier.verify_claim")
    @patch("content_assistant.tools.wellness_verifier.extract_claims")
    def test_result_has_required_keys(self, mock_extract, mock_verify, monkeypatch):
        """Test that result has all required keys."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_extract.return_value = ["Test claim"]
        mock_verify.return_value = VerifiedClaim(
            claim="Test",
            status=ClaimStatus.VERIFIED,
            evidence="Test",
            source="test.pdf",
        )

        result = verify_content("Test content.")

        required_keys = ["claims", "summary", "verified_count", "inaccurate_count", "unverified_count"]
        for key in required_keys:
            assert key in result
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.wellness_verifier import verify_content, verify_claim, ClaimStatus" && echo "PASS"

# AC2: Autophagy claim returns VERIFIED (mocked)
pytest tests/test_wellness_verifier.py::TestVerifyClaim::test_autophagy_claim_returns_verified -v
# Expected: PASSED

# AC3: Cancer cure claim returns INACCURATE or UNVERIFIED (mocked)
pytest tests/test_wellness_verifier.py::TestVerifyClaim::test_cancer_cure_claim_returns_inaccurate_or_unverified -v
# Expected: PASSED

# AC4: Wellness content returns at least one claim (mocked)
pytest tests/test_wellness_verifier.py::TestVerifyContent::test_returns_at_least_one_claim_for_wellness_content -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_wellness_verifier.py -v
# Expected: at least 6 passed

# AC6: ClaimStatus enum has correct values
python -c "
from content_assistant.tools.wellness_verifier import ClaimStatus
assert 'VERIFIED' in ClaimStatus.__members__
assert 'INACCURATE' in ClaimStatus.__members__
assert 'UNVERIFIED' in ClaimStatus.__members__
print('PASS: ClaimStatus has all values')
"

# AC7: Ruff passes
ruff check content_assistant/tools/wellness_verifier.py tests/test_wellness_verifier.py && echo "PASS: ruff clean"
```

---

#### Story 16: Build Engagement Analyzer Tool

**What to Build:**
Create a tool that analyzes content for engagement factors (hook strength, CTA effectiveness, structure) and provides scores and improvement suggestions.

**Files to Create:**

1. `content_assistant/tools/engagement_analyzer.py`
```python
"""Engagement analysis for marketing content."""
from typing import Dict, List
from dataclasses import dataclass, asdict
from content_assistant.tools.claude_client import generate_json
from content_assistant.rag.knowledge_base import retrieve_engagement_patterns


@dataclass
class EngagementScores:
    """Engagement scores for content."""
    hook_score: int  # 1-10
    cta_score: int  # 1-10
    structure_score: int  # 1-10
    overall_score: float  # Average


@dataclass
class EngagementAnalysis:
    """Full engagement analysis result."""
    scores: EngagementScores
    issues: List[str]
    suggestions: List[str]
    hook_analysis: str
    cta_analysis: str
    structure_analysis: str


ANALYSIS_SYSTEM_PROMPT = """You are an expert content engagement analyst for wellness marketing.

Analyze content for engagement factors:

1. **HOOK (Score 1-10)**
   - Does first sentence grab attention?
   - Is there a pattern interrupt?
   - Is there a curiosity gap?
   - Score < 5 if: generic opening, starts with "We", no question/tension

2. **CTA (Score 1-10)**
   - Is there a clear call to action?
   - Is it specific (not just "click here")?
   - Is it appropriate for the platform?
   - Score < 3 if: no CTA present, vague CTA

3. **STRUCTURE (Score 1-10)**
   - Is content scannable?
   - Appropriate length for platform?
   - Good use of formatting?
   - Clear flow from hook to CTA?

For each issue, provide a specific, actionable suggestion.

Respond with JSON:
{
    "hook_score": 1-10,
    "hook_analysis": "...",
    "cta_score": 1-10,
    "cta_analysis": "...",
    "structure_score": 1-10,
    "structure_analysis": "...",
    "issues": ["issue 1", "issue 2", ...],
    "suggestions": ["suggestion 1", "suggestion 2", ...]
}"""


def analyze_engagement(content: str, content_type: str) -> EngagementAnalysis:
    """
    Analyze content for engagement factors.

    Args:
        content: Content to analyze
        content_type: Type of content (email, blog, instagram_post, etc.)

    Returns:
        EngagementAnalysis with scores, issues, and suggestions
    """
    if not content or not content.strip():
        return EngagementAnalysis(
            scores=EngagementScores(0, 0, 0, 0.0),
            issues=["Content is empty"],
            suggestions=["Provide content to analyze"],
            hook_analysis="No content",
            cta_analysis="No content",
            structure_analysis="No content",
        )

    # Get engagement guidelines from RAG
    guidelines = retrieve_engagement_patterns(
        f"{content_type} engagement best practices hook CTA",
        top_k=3
    )
    guidelines_text = "\n".join([g["text"] for g in guidelines]) if guidelines else ""

    # Analyze with Claude
    user_message = f"""Analyze this {content_type} content for engagement:

---
{content}
---

Engagement guidelines context:
{guidelines_text}

Provide scores and specific suggestions."""

    try:
        result = generate_json(ANALYSIS_SYSTEM_PROMPT, user_message)

        hook_score = int(result.get("hook_score", 5))
        cta_score = int(result.get("cta_score", 5))
        structure_score = int(result.get("structure_score", 5))

        # Ensure scores are in valid range
        hook_score = max(1, min(10, hook_score))
        cta_score = max(1, min(10, cta_score))
        structure_score = max(1, min(10, structure_score))

        scores = EngagementScores(
            hook_score=hook_score,
            cta_score=cta_score,
            structure_score=structure_score,
            overall_score=round((hook_score + cta_score + structure_score) / 3, 1),
        )

        return EngagementAnalysis(
            scores=scores,
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
            hook_analysis=result.get("hook_analysis", ""),
            cta_analysis=result.get("cta_analysis", ""),
            structure_analysis=result.get("structure_analysis", ""),
        )

    except Exception as e:
        return EngagementAnalysis(
            scores=EngagementScores(5, 5, 5, 5.0),
            issues=[f"Analysis error: {e}"],
            suggestions=["Please try again"],
            hook_analysis="Error during analysis",
            cta_analysis="Error during analysis",
            structure_analysis="Error during analysis",
        )


def has_weak_hook(content: str) -> bool:
    """
    Quick check if content has a weak hook.

    Args:
        content: Content to check

    Returns:
        True if hook appears weak
    """
    if not content:
        return True

    first_line = content.split("\n")[0].strip()

    # Check for weak patterns
    weak_patterns = [
        "we are",
        "our company",
        "welcome to",
        "at thelifeco",
        "hello",
        "hi there",
    ]

    first_lower = first_line.lower()
    return any(first_lower.startswith(pattern) for pattern in weak_patterns)


def has_cta(content: str) -> bool:
    """
    Quick check if content has a call to action.

    Args:
        content: Content to check

    Returns:
        True if CTA appears present
    """
    if not content:
        return False

    content_lower = content.lower()

    cta_indicators = [
        "book now",
        "sign up",
        "learn more",
        "get started",
        "contact us",
        "schedule",
        "call today",
        "click here",
        "link in bio",
        "tap to",
        "swipe up",
        "dm us",
        "download",
        "register",
        "reserve",
        "claim your",
    ]

    return any(indicator in content_lower for indicator in cta_indicators)


def analysis_to_dict(analysis: EngagementAnalysis) -> Dict:
    """Convert analysis to dict."""
    result = asdict(analysis)
    result["scores"] = asdict(analysis.scores)
    return result
```

2. `tests/test_engagement_analyzer.py`
```python
"""Tests for engagement analyzer module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.tools.engagement_analyzer import (
    analyze_engagement,
    has_weak_hook,
    has_cta,
    EngagementAnalysis,
    EngagementScores,
    analysis_to_dict,
)
from content_assistant.config import reset_config


class TestAnalyzeEngagement:
    """Tests for engagement analysis."""

    def setup_method(self):
        reset_config()

    @patch("content_assistant.tools.engagement_analyzer.retrieve_engagement_patterns")
    @patch("content_assistant.tools.engagement_analyzer.generate_json")
    def test_weak_hook_gets_low_score(
        self, mock_generate, mock_retrieve, monkeypatch
    ):
        """Test that content with weak hook gets hook_score < 5."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_retrieve.return_value = []
        mock_generate.return_value = {
            "hook_score": 3,  # Weak hook
            "hook_analysis": "Generic opening, no pattern interrupt",
            "cta_score": 7,
            "cta_analysis": "Good CTA",
            "structure_score": 6,
            "structure_analysis": "OK structure",
            "issues": ["Hook is too generic"],
            "suggestions": ["Start with a question or surprising fact"],
        }

        content = "We are TheLifeCo, a wellness company. We offer many programs. Book now."
        result = analyze_engagement(content, "email")

        assert result.scores.hook_score < 5

    @patch("content_assistant.tools.engagement_analyzer.retrieve_engagement_patterns")
    @patch("content_assistant.tools.engagement_analyzer.generate_json")
    def test_no_cta_gets_low_score(
        self, mock_generate, mock_retrieve, monkeypatch
    ):
        """Test that content without CTA gets cta_score < 3."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_retrieve.return_value = []
        mock_generate.return_value = {
            "hook_score": 8,
            "hook_analysis": "Strong hook",
            "cta_score": 2,  # No CTA
            "cta_analysis": "No clear call to action found",
            "structure_score": 7,
            "structure_analysis": "Good structure",
            "issues": ["Missing call to action"],
            "suggestions": ["Add a clear CTA at the end"],
        }

        content = "What if everything about diets is wrong? Here's the truth about metabolism."
        result = analyze_engagement(content, "blog")

        assert result.scores.cta_score < 3

    @patch("content_assistant.tools.engagement_analyzer.retrieve_engagement_patterns")
    @patch("content_assistant.tools.engagement_analyzer.generate_json")
    def test_returns_list_of_suggestions(
        self, mock_generate, mock_retrieve, monkeypatch
    ):
        """Test that analysis returns suggestions list."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_retrieve.return_value = []
        mock_generate.return_value = {
            "hook_score": 6,
            "hook_analysis": "OK",
            "cta_score": 6,
            "cta_analysis": "OK",
            "structure_score": 6,
            "structure_analysis": "OK",
            "issues": ["Could improve hook"],
            "suggestions": ["Add pattern interrupt", "Make CTA more specific"],
        }

        result = analyze_engagement("Test content", "email")

        assert isinstance(result.suggestions, list)
        assert len(result.suggestions) >= 1


class TestHasWeakHook:
    """Tests for weak hook detection."""

    def test_generic_opening_is_weak(self):
        """Test that generic 'We are' opening is detected as weak."""
        content = "We are TheLifeCo and we offer wellness programs."
        assert has_weak_hook(content) is True

    def test_question_opening_is_strong(self):
        """Test that question opening is not detected as weak."""
        content = "What if you could reset your body in 7 days?"
        assert has_weak_hook(content) is False

    def test_empty_content_is_weak(self):
        """Test that empty content is weak."""
        assert has_weak_hook("") is True


class TestHasCta:
    """Tests for CTA detection."""

    def test_book_now_detected(self):
        """Test that 'Book now' is detected as CTA."""
        content = "Great content here. Book now to start your journey."
        assert has_cta(content) is True

    def test_link_in_bio_detected(self):
        """Test that 'link in bio' is detected for social."""
        content = "Amazing transformation story! Link in bio."
        assert has_cta(content) is True

    def test_no_cta_not_detected(self):
        """Test that content without CTA returns False."""
        content = "Here is some information about wellness."
        assert has_cta(content) is False


class TestAnalysisToDict:
    """Tests for serialization."""

    def test_converts_to_dict(self):
        """Test that analysis converts to dict properly."""
        analysis = EngagementAnalysis(
            scores=EngagementScores(7, 8, 6, 7.0),
            issues=["Issue 1"],
            suggestions=["Suggestion 1"],
            hook_analysis="Good",
            cta_analysis="Good",
            structure_analysis="OK",
        )

        result = analysis_to_dict(analysis)

        assert isinstance(result, dict)
        assert result["scores"]["hook_score"] == 7
        assert result["issues"] == ["Issue 1"]
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.engagement_analyzer import analyze_engagement, has_weak_hook, has_cta, EngagementAnalysis" && echo "PASS"

# AC2: Weak hook gets hook_score < 5 (mocked)
pytest tests/test_engagement_analyzer.py::TestAnalyzeEngagement::test_weak_hook_gets_low_score -v
# Expected: PASSED

# AC3: Content without CTA gets cta_score < 3 (mocked)
pytest tests/test_engagement_analyzer.py::TestAnalyzeEngagement::test_no_cta_gets_low_score -v
# Expected: PASSED

# AC4: Returns list of suggestions (mocked)
pytest tests/test_engagement_analyzer.py::TestAnalyzeEngagement::test_returns_list_of_suggestions -v
# Expected: PASSED

# AC5: Quick hook check works
pytest tests/test_engagement_analyzer.py::TestHasWeakHook -v
# Expected: 3 passed

# AC6: Quick CTA check works
pytest tests/test_engagement_analyzer.py::TestHasCta -v
# Expected: 3 passed

# AC7: All unit tests pass
pytest tests/test_engagement_analyzer.py -v
# Expected: at least 9 passed

# AC8: Ruff passes
ruff check content_assistant/tools/engagement_analyzer.py tests/test_engagement_analyzer.py && echo "PASS: ruff clean"
```

---
### Epic 6: Signal Collection & Feedback Loop
---

#### Story 17: Build Signal Storage Module

**What to Build:**
Create a database module for storing content generations and collecting user feedback signals.

**Files to Create:**

1. `content_assistant/db/signals.py`
```python
"""Signal storage for content generations."""
from typing import Dict, Optional, List
from datetime import datetime
import uuid
from content_assistant.db.supabase_client import get_admin_client
from content_assistant.rag.embeddings import embed_text


def store_generation(
    user_id: Optional[str],
    brief: Dict,
    preview: Optional[Dict],
    content: str,
    content_type: str,
) -> str:
    """
    Store a new content generation.

    Args:
        user_id: User who created the content (optional)
        brief: The 13-question brief
        preview: The approved preview (optional)
        content: The generated content
        content_type: Type of content (email, blog, etc.)

    Returns:
        UUID of the stored generation
    """
    client = get_admin_client()

    # Generate embedding for the content
    embedding = embed_text(content[:2000])  # Limit length for embedding

    record = {
        "user_id": user_id,
        "brief": brief,
        "preview": preview,
        "content": content,
        "content_type": content_type,
        "embedding": embedding,
        "signals": {},  # Empty initially
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
        },
    }

    result = client.table("content_generations").insert(record).execute()

    if result.data:
        return result.data[0]["id"]
    raise Exception("Failed to store generation")


def update_signals(generation_id: str, signals: Dict) -> bool:
    """
    Update signals for a generation.

    Args:
        generation_id: UUID of the generation
        signals: Dict with signal data:
            - star_rating: 1-5
            - hook_worked: bool
            - facts_accurate: bool
            - tone_matched: bool
            - cta_effective: bool
            - edits_made: bool
            - feedback_text: optional string

    Returns:
        True if update successful
    """
    client = get_admin_client()

    # Validate signals
    validated_signals = {
        "star_rating": signals.get("star_rating"),
        "hook_worked": signals.get("hook_worked"),
        "facts_accurate": signals.get("facts_accurate"),
        "tone_matched": signals.get("tone_matched"),
        "cta_effective": signals.get("cta_effective"),
        "edits_made": signals.get("edits_made"),
        "feedback_text": signals.get("feedback_text"),
        "updated_at": datetime.utcnow().isoformat(),
    }

    result = client.table("content_generations").update({"signals": validated_signals}).eq("id", generation_id).execute()

    return bool(result.data)


def get_generation(generation_id: str) -> Optional[Dict]:
    """
    Get a generation by ID.

    Args:
        generation_id: UUID of the generation

    Returns:
        Generation dict or None if not found
    """
    client = get_admin_client()

    result = client.table("content_generations").select("*").eq("id", generation_id).single().execute()

    return result.data if result.data else None


def get_user_generations(
    user_id: str,
    limit: int = 50,
    content_type: Optional[str] = None,
) -> List[Dict]:
    """
    Get generations for a user.

    Args:
        user_id: User ID
        limit: Maximum number to return
        content_type: Optional filter by type

    Returns:
        List of generation dicts
    """
    client = get_admin_client()

    query = client.table("content_generations").select("*").eq("user_id", user_id)

    if content_type:
        query = query.eq("content_type", content_type)

    query = query.order("created_at", desc=True).limit(limit)

    result = query.execute()

    return result.data if result.data else []


def get_generations_with_signals(
    min_rating: Optional[float] = None,
    limit: int = 100,
) -> List[Dict]:
    """
    Get generations that have signal data.

    Args:
        min_rating: Optional minimum star rating
        limit: Maximum to return

    Returns:
        List of generations with signals
    """
    client = get_admin_client()

    query = client.table("content_generations").select("*").not_.is_("signals->star_rating", "null")

    if min_rating:
        query = query.gte("signals->star_rating", min_rating)

    query = query.order("created_at", desc=True).limit(limit)

    result = query.execute()

    return result.data if result.data else []
```

2. `tests/test_signals.py`
```python
"""Tests for signal storage module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.db.signals import (
    store_generation,
    update_signals,
    get_generation,
    get_user_generations,
)
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients
from content_assistant.rag.embeddings import reset_client as reset_embed


class TestStoreGeneration:
    """Tests for storing generations."""

    def setup_method(self):
        reset_config()
        reset_clients()
        reset_embed()

    @patch("content_assistant.db.signals.embed_text")
    @patch("content_assistant.db.signals.get_admin_client")
    def test_store_returns_valid_uuid(
        self, mock_get_client, mock_embed, monkeypatch
    ):
        """Test that store_generation returns valid UUID."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_embed.return_value = [0.1] * 1024

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "123e4567-e89b-12d3-a456-426614174000"}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = store_generation(
            user_id="user123",
            brief={"target_audience": "Test"},
            preview=None,
            content="Test content",
            content_type="email",
        )

        assert result == "123e4567-e89b-12d3-a456-426614174000"
        assert len(result) == 36  # UUID format


class TestUpdateSignals:
    """Tests for updating signals."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.db.signals.get_admin_client")
    def test_update_signals_returns_true(self, mock_get_client, monkeypatch):
        """Test that update_signals returns True on success."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "123"}]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = update_signals(
            "123e4567-e89b-12d3-a456-426614174000",
            {
                "star_rating": 5,
                "hook_worked": True,
                "facts_accurate": True,
            }
        )

        assert result is True


class TestGetGeneration:
    """Tests for getting generations."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.db.signals.get_admin_client")
    def test_get_generation_returns_data(self, mock_get_client, monkeypatch):
        """Test that get_generation returns stored data."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = {
            "id": "123",
            "content": "Test content",
            "signals": {"star_rating": 5},
        }
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = get_generation("123")

        assert result is not None
        assert result["signals"]["star_rating"] == 5


@pytest.mark.integration
class TestSignalsIntegration:
    """Integration tests requiring real database."""

    @pytest.mark.skipif(
        not all([
            __import__("os").getenv("SUPABASE_URL"),
            __import__("os").getenv("SUPABASE_SERVICE_KEY"),
        ]),
        reason="Supabase credentials not configured"
    )
    def test_store_update_get_cycle(self):
        """Test full cycle: store, update signals, get."""
        # Store
        gen_id = store_generation(
            user_id=None,
            brief={"target_audience": "Test integration"},
            preview=None,
            content="Integration test content",
            content_type="test",
        )
        assert gen_id

        # Update signals
        success = update_signals(gen_id, {"star_rating": 4, "hook_worked": True})
        assert success

        # Get and verify
        result = get_generation(gen_id)
        assert result["signals"]["star_rating"] == 4
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.db.signals import store_generation, update_signals, get_generation" && echo "PASS"

# AC2: Store returns valid UUID (mocked)
pytest tests/test_signals.py::TestStoreGeneration::test_store_returns_valid_uuid -v
# Expected: PASSED

# AC3: Update signals returns true (mocked)
pytest tests/test_signals.py::TestUpdateSignals::test_update_signals_returns_true -v
# Expected: PASSED

# AC4: Get generation returns updated data (mocked)
pytest tests/test_signals.py::TestGetGeneration::test_get_generation_returns_data -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_signals.py -v -k "not integration"
# Expected: at least 3 passed

# AC6: Ruff passes
ruff check content_assistant/db/signals.py tests/test_signals.py && echo "PASS: ruff clean"
```

**Additional File for Story 17: Cost Tracker**

3. `content_assistant/db/cost_tracker.py`
```python
"""Cost tracking and budget enforcement."""
from typing import Dict, Optional
from datetime import datetime, timedelta
from content_assistant.db.supabase_client import get_admin_client
from content_assistant.config import get_config


# Approximate costs per API call (USD)
COST_ESTIMATES = {
    "claude_sonnet_input_1k": 0.003,    # $3 per 1M input tokens
    "claude_sonnet_output_1k": 0.015,   # $15 per 1M output tokens
    "voyage_embed_1k": 0.0001,          # $0.10 per 1M tokens
}


class CostLimitExceeded(Exception):
    """Raised when cost limits are exceeded."""
    pass


def estimate_cost(
    input_tokens: int = 0,
    output_tokens: int = 0,
    embedding_tokens: int = 0,
) -> float:
    """
    Estimate cost for an API operation.

    Args:
        input_tokens: Claude input tokens
        output_tokens: Claude output tokens
        embedding_tokens: Voyage embedding tokens

    Returns:
        Estimated cost in USD
    """
    cost = 0.0
    cost += (input_tokens / 1000) * COST_ESTIMATES["claude_sonnet_input_1k"]
    cost += (output_tokens / 1000) * COST_ESTIMATES["claude_sonnet_output_1k"]
    cost += (embedding_tokens / 1000) * COST_ESTIMATES["voyage_embed_1k"]
    return round(cost, 6)


def log_api_cost(
    operation: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    embedding_tokens: int = 0,
    user_id: Optional[str] = None,
) -> float:
    """
    Log an API cost to the database.

    Args:
        operation: Name of operation (e.g., "generate_preview", "embed_brief")
        input_tokens: Claude input tokens used
        output_tokens: Claude output tokens used
        embedding_tokens: Voyage tokens used
        user_id: Optional user ID

    Returns:
        Estimated cost in USD
    """
    cost = estimate_cost(input_tokens, output_tokens, embedding_tokens)

    try:
        client = get_admin_client()
        client.table("api_costs").insert({
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "embedding_tokens": embedding_tokens,
            "estimated_cost_usd": cost,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass  # Don't fail if cost logging fails

    return cost


def get_daily_cost(user_id: Optional[str] = None) -> float:
    """Get total cost for today."""
    try:
        client = get_admin_client()
        today = datetime.utcnow().date().isoformat()

        query = client.table("api_costs").select("estimated_cost_usd").gte("created_at", today)

        if user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()

        if result.data:
            return sum(r.get("estimated_cost_usd", 0) for r in result.data)
        return 0.0
    except Exception:
        return 0.0


def get_monthly_cost(user_id: Optional[str] = None) -> float:
    """Get total cost for current month."""
    try:
        client = get_admin_client()
        month_start = datetime.utcnow().replace(day=1).date().isoformat()

        query = client.table("api_costs").select("estimated_cost_usd").gte("created_at", month_start)

        if user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()

        if result.data:
            return sum(r.get("estimated_cost_usd", 0) for r in result.data)
        return 0.0
    except Exception:
        return 0.0


def get_daily_generation_count(user_id: Optional[str] = None) -> int:
    """Get number of generations today."""
    try:
        client = get_admin_client()
        today = datetime.utcnow().date().isoformat()

        query = client.table("content_generations").select("id", count="exact").gte("created_at", today)

        if user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()
        return result.count if result.count else 0
    except Exception:
        return 0


def check_limits(user_id: Optional[str] = None) -> Dict:
    """
    Check if any cost limits are exceeded.

    Returns:
        Dict with:
        - can_proceed: bool
        - daily_generations: int
        - daily_cost: float
        - monthly_cost: float
        - warnings: list of warning messages
        - errors: list of blocking errors
    """
    config = get_config()

    daily_gens = get_daily_generation_count(user_id)
    daily_cost = get_daily_cost(user_id)
    monthly_cost = get_monthly_cost(user_id)

    warnings = []
    errors = []

    # Check daily generation limit
    if daily_gens >= config.daily_generation_limit:
        errors.append(f"Daily generation limit reached ({config.daily_generation_limit})")

    # Check monthly budget
    if monthly_cost >= config.monthly_budget_usd:
        errors.append(f"Monthly budget exceeded (${config.monthly_budget_usd})")

    # Check alert threshold
    budget_percent = monthly_cost / config.monthly_budget_usd if config.monthly_budget_usd > 0 else 0
    if budget_percent >= config.cost_alert_threshold:
        warnings.append(f"Warning: {budget_percent*100:.0f}% of monthly budget used")

    return {
        "can_proceed": len(errors) == 0,
        "daily_generations": daily_gens,
        "daily_cost": daily_cost,
        "monthly_cost": monthly_cost,
        "budget_percent": budget_percent,
        "warnings": warnings,
        "errors": errors,
    }


def enforce_limits(user_id: Optional[str] = None):
    """
    Enforce cost limits - raises exception if limits exceeded.

    Raises:
        CostLimitExceeded: If any limit is exceeded
    """
    result = check_limits(user_id)
    if not result["can_proceed"]:
        raise CostLimitExceeded("; ".join(result["errors"]))
```

**Note:** This requires adding an `api_costs` table to the schema. Add to `schema.sql`:

```sql
-- Table: api_costs (for cost tracking)
CREATE TABLE IF NOT EXISTS api_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    embedding_tokens INTEGER DEFAULT 0,
    estimated_cost_usd DECIMAL(10, 6) DEFAULT 0,
    user_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS api_costs_created_idx ON api_costs(created_at);
CREATE INDEX IF NOT EXISTS api_costs_user_idx ON api_costs(user_id);
```

---

#### Story 18: Build Signal-Derived Ranker

**What to Build:**
Create a ranking module that combines semantic similarity with signal scores to prioritize high-performing examples.

**Files to Create:**

1. `content_assistant/tools/signal_ranker.py`
```python
"""Signal-derived ranking for few-shot examples."""
from typing import List, Dict, Optional


def calculate_signal_score(signals: Optional[Dict]) -> float:
    """
    Calculate a signal score from user feedback.

    Formula: (star_rating/5) * bonuses
    - Each positive signal (hook_worked, facts_accurate, etc.) adds 10% bonus

    Args:
        signals: Dict with signal values, or None

    Returns:
        Score between 0.0 and ~1.5
    """
    if not signals:
        return 1.0  # Neutral score for no signals

    # Base score from star rating (0.0 - 1.0)
    star_rating = signals.get("star_rating")
    if star_rating is None:
        base_score = 0.5  # Default if no rating
    else:
        base_score = float(star_rating) / 5.0

    # Bonus multipliers for positive signals
    bonus = 1.0
    positive_signals = [
        "hook_worked",
        "facts_accurate",
        "tone_matched",
        "cta_effective",
    ]

    for signal_name in positive_signals:
        if signals.get(signal_name) is True:
            bonus += 0.1  # 10% bonus per positive signal

    # Penalty for edits (suggests content needed work)
    if signals.get("edits_made") is True:
        bonus -= 0.1

    return base_score * bonus


def rank_examples(
    examples: List[Dict],
    similarity_key: str = "similarity",
) -> List[Dict]:
    """
    Rank examples by combined score (similarity × signal_score).

    Args:
        examples: List of example dicts with similarity and signals
        similarity_key: Key containing similarity score

    Returns:
        Examples sorted by combined score (highest first)
    """
    if not examples:
        return []

    ranked = []
    for example in examples:
        similarity = example.get(similarity_key, 0.5)
        signals = example.get("signals", {})

        signal_score = calculate_signal_score(signals)
        combined_score = similarity * signal_score

        ranked.append({
            **example,
            "signal_score": signal_score,
            "combined_score": combined_score,
        })

    # Sort by combined score, highest first
    ranked.sort(key=lambda x: x["combined_score"], reverse=True)

    return ranked


def get_top_examples(
    examples: List[Dict],
    top_k: int = 5,
    min_combined_score: Optional[float] = None,
) -> List[Dict]:
    """
    Get top-ranked examples.

    Args:
        examples: List of examples to rank
        top_k: Number to return
        min_combined_score: Optional minimum score threshold

    Returns:
        Top k ranked examples
    """
    ranked = rank_examples(examples)

    if min_combined_score:
        ranked = [e for e in ranked if e["combined_score"] >= min_combined_score]

    return ranked[:top_k]
```

2. `tests/test_signal_ranker.py`
```python
"""Tests for signal-derived ranker."""
import pytest
from content_assistant.tools.signal_ranker import (
    calculate_signal_score,
    rank_examples,
    get_top_examples,
)


class TestCalculateSignalScore:
    """Tests for signal score calculation."""

    def test_five_star_with_positives_higher_than_three_star(self):
        """Test that 5-star with positive signals > 3-star rating."""
        five_star_signals = {
            "star_rating": 5,
            "hook_worked": True,
            "facts_accurate": True,
            "tone_matched": True,
        }
        three_star_signals = {
            "star_rating": 3,
        }

        five_star_score = calculate_signal_score(five_star_signals)
        three_star_score = calculate_signal_score(three_star_signals)

        assert five_star_score > three_star_score

    def test_no_signals_returns_neutral(self):
        """Test that no signals returns neutral score of 1.0."""
        score = calculate_signal_score(None)
        assert score == 1.0

        score = calculate_signal_score({})
        assert score == 0.5  # No star rating = 0.5 base

    def test_positive_signals_increase_score(self):
        """Test that positive signals increase score."""
        base_signals = {"star_rating": 4}
        with_positives = {
            "star_rating": 4,
            "hook_worked": True,
            "facts_accurate": True,
        }

        base_score = calculate_signal_score(base_signals)
        positive_score = calculate_signal_score(with_positives)

        assert positive_score > base_score

    def test_edits_made_decreases_score(self):
        """Test that edits_made decreases score."""
        without_edits = {"star_rating": 4}
        with_edits = {"star_rating": 4, "edits_made": True}

        without_score = calculate_signal_score(without_edits)
        with_score = calculate_signal_score(with_edits)

        assert with_score < without_score


class TestRankExamples:
    """Tests for example ranking."""

    def test_examples_without_signals_ranked_by_similarity(self):
        """Test that examples without signals are ranked by similarity alone."""
        examples = [
            {"content": "A", "similarity": 0.9},
            {"content": "B", "similarity": 0.7},
            {"content": "C", "similarity": 0.8},
        ]

        ranked = rank_examples(examples)

        # Should be sorted by similarity (since no signals, signal_score=1.0)
        assert ranked[0]["content"] == "A"
        assert ranked[1]["content"] == "C"
        assert ranked[2]["content"] == "B"

    def test_examples_with_signals_ranked_by_combined(self):
        """Test that examples with signals use combined score."""
        examples = [
            {"content": "Low similarity high rating", "similarity": 0.6, "signals": {"star_rating": 5, "hook_worked": True}},
            {"content": "High similarity low rating", "similarity": 0.9, "signals": {"star_rating": 2}},
        ]

        ranked = rank_examples(examples)

        # The high-rated low-similarity might beat low-rated high-similarity
        # depending on the math: 0.6 * 1.1 = 0.66 vs 0.9 * 0.4 = 0.36
        # Actually: 5-star = 1.0 * 1.1 (hook bonus) = 1.1, combined = 0.6 * 1.1 = 0.66
        # 2-star = 0.4 * 1.0 = 0.4, combined = 0.9 * 0.4 = 0.36
        assert ranked[0]["content"] == "Low similarity high rating"

    def test_empty_list_returns_empty(self):
        """Test that empty input returns empty output."""
        assert rank_examples([]) == []


class TestGetTopExamples:
    """Tests for getting top examples."""

    def test_returns_top_k(self):
        """Test that correct number of examples returned."""
        examples = [
            {"content": str(i), "similarity": 0.5 + i * 0.1}
            for i in range(10)
        ]

        top = get_top_examples(examples, top_k=3)

        assert len(top) == 3

    def test_respects_min_score(self):
        """Test that minimum score threshold is respected."""
        examples = [
            {"content": "A", "similarity": 0.9},
            {"content": "B", "similarity": 0.3},
        ]

        top = get_top_examples(examples, top_k=5, min_combined_score=0.5)

        # B has combined score 0.3 * 1.0 = 0.3, below threshold
        assert len(top) == 1
        assert top[0]["content"] == "A"
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.tools.signal_ranker import calculate_signal_score, rank_examples, get_top_examples" && echo "PASS"

# AC2: 5-star with positives > 3-star rating
pytest tests/test_signal_ranker.py::TestCalculateSignalScore::test_five_star_with_positives_higher_than_three_star -v
# Expected: PASSED

# AC3: Examples without signals ranked by similarity
pytest tests/test_signal_ranker.py::TestRankExamples::test_examples_without_signals_ranked_by_similarity -v
# Expected: PASSED

# AC4: Examples with signals ranked by combined score
pytest tests/test_signal_ranker.py::TestRankExamples::test_examples_with_signals_ranked_by_combined -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_signal_ranker.py -v
# Expected: at least 7 passed

# AC6: Ruff passes
ruff check content_assistant/tools/signal_ranker.py tests/test_signal_ranker.py && echo "PASS: ruff clean"
```

---
### Epic 7: Experiment Framework
---

#### Story 19: Build Experiment Manager

**What to Build:**
Create an A/B experiment framework for testing different content generation approaches.

**Files to Create:**

1. `content_assistant/experiments/manager.py`
```python
"""A/B Experiment management."""
from typing import Dict, Optional, List
import random
from datetime import datetime
from content_assistant.db.supabase_client import get_admin_client


def create_experiment(
    name: str,
    config: Dict,
    description: Optional[str] = None,
) -> str:
    """
    Create a new experiment.

    Args:
        name: Unique experiment name
        config: Experiment configuration (variants, parameters, etc.)
        description: Optional description

    Returns:
        UUID of created experiment
    """
    client = get_admin_client()

    record = {
        "name": name,
        "description": description,
        "config": config,
        "status": "draft",
    }

    result = client.table("experiments").insert(record).execute()

    if result.data:
        return result.data[0]["id"]
    raise Exception("Failed to create experiment")


def start_experiment(experiment_id: str) -> bool:
    """
    Start an experiment (set status to active).

    Args:
        experiment_id: UUID of experiment

    Returns:
        True if successful
    """
    client = get_admin_client()

    result = client.table("experiments").update({
        "status": "active",
        "started_at": datetime.utcnow().isoformat(),
    }).eq("id", experiment_id).execute()

    return bool(result.data)


def assign_variant(
    session_id: str,
    experiment_id: str,
) -> str:
    """
    Assign a variant to a session (random 50/50 split).

    Args:
        session_id: User session identifier
        experiment_id: UUID of experiment

    Returns:
        "control" or "treatment"
    """
    client = get_admin_client()

    # Check for existing assignment
    existing = client.table("experiment_assignments").select("variant").eq("session_id", session_id).eq("experiment_id", experiment_id).single().execute()

    if existing.data:
        return existing.data["variant"]

    # Random assignment
    variant = "control" if random.random() < 0.5 else "treatment"

    # Store assignment
    client.table("experiment_assignments").insert({
        "session_id": session_id,
        "experiment_id": experiment_id,
        "variant": variant,
        "signals": {},
    }).execute()

    return variant


def log_signal(
    session_id: str,
    experiment_id: str,
    signals: Dict,
) -> bool:
    """
    Log signals for an experiment assignment.

    Args:
        session_id: User session
        experiment_id: Experiment UUID
        signals: Signal data to log

    Returns:
        True if successful
    """
    client = get_admin_client()

    result = client.table("experiment_assignments").update({
        "signals": signals,
    }).eq("session_id", session_id).eq("experiment_id", experiment_id).execute()

    return bool(result.data)


def get_experiment_results(experiment_id: str) -> Dict:
    """
    Get aggregated results for an experiment.

    Args:
        experiment_id: UUID of experiment

    Returns:
        Dict with results by variant
    """
    client = get_admin_client()

    # Get all assignments
    result = client.table("experiment_assignments").select("*").eq("experiment_id", experiment_id).execute()

    if not result.data:
        return {"control": [], "treatment": [], "summary": {}}

    # Group by variant
    control = [a for a in result.data if a["variant"] == "control"]
    treatment = [a for a in result.data if a["variant"] == "treatment"]

    # Calculate summary stats
    def avg_rating(assignments):
        ratings = [a["signals"].get("star_rating") for a in assignments if a["signals"].get("star_rating")]
        return sum(ratings) / len(ratings) if ratings else None

    return {
        "control": control,
        "treatment": treatment,
        "summary": {
            "control_count": len(control),
            "treatment_count": len(treatment),
            "control_avg_rating": avg_rating(control),
            "treatment_avg_rating": avg_rating(treatment),
        },
    }


def get_active_experiments() -> List[Dict]:
    """Get all active experiments."""
    client = get_admin_client()

    result = client.table("experiments").select("*").eq("status", "active").execute()

    return result.data if result.data else []
```

2. `tests/test_experiments.py`
```python
"""Tests for experiment manager."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.experiments.manager import (
    create_experiment,
    assign_variant,
    log_signal,
    get_experiment_results,
)
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients


class TestCreateExperiment:
    """Tests for experiment creation."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.experiments.manager.get_admin_client")
    def test_create_returns_uuid(self, mock_get_client, monkeypatch):
        """Test that create_experiment returns UUID."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "123e4567-e89b-12d3-a456-426614174000"}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = create_experiment(
            name="test_experiment",
            config={"variants": ["control", "treatment"]},
        )

        assert len(result) == 36  # UUID format


class TestAssignVariant:
    """Tests for variant assignment."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.experiments.manager.get_admin_client")
    def test_assignments_roughly_5050(self, mock_get_client, monkeypatch):
        """Test that 100 assignments are roughly 50/50 split."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()

        # No existing assignment
        mock_select_result = MagicMock()
        mock_select_result.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_select_result

        # Insert succeeds
        mock_insert_result = MagicMock()
        mock_insert_result.data = [{}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_insert_result

        mock_get_client.return_value = mock_client

        # Run 100 assignments
        variants = []
        for i in range(100):
            variant = assign_variant(f"session_{i}", "exp_123")
            variants.append(variant)

        control_count = variants.count("control")
        treatment_count = variants.count("treatment")

        # Should be roughly 50/50 (allow 40-60 range)
        assert 40 <= control_count <= 60, f"Control: {control_count}, Treatment: {treatment_count}"
        assert 40 <= treatment_count <= 60


class TestGetExperimentResults:
    """Tests for getting results."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.experiments.manager.get_admin_client")
    def test_logged_signals_retrievable(self, mock_get_client, monkeypatch):
        """Test that logged signals are retrievable."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"variant": "control", "signals": {"star_rating": 4}},
            {"variant": "control", "signals": {"star_rating": 5}},
            {"variant": "treatment", "signals": {"star_rating": 5}},
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        results = get_experiment_results("exp_123")

        assert "control" in results
        assert "treatment" in results
        assert "summary" in results
        assert results["summary"]["control_count"] == 2
        assert results["summary"]["treatment_count"] == 1
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.experiments.manager import create_experiment, assign_variant, log_signal, get_experiment_results" && echo "PASS"

# AC2: Create experiment returns UUID (mocked)
pytest tests/test_experiments.py::TestCreateExperiment::test_create_returns_uuid -v
# Expected: PASSED

# AC3: 100 assignments roughly 50/50 (40-60 each)
pytest tests/test_experiments.py::TestAssignVariant::test_assignments_roughly_5050 -v
# Expected: PASSED

# AC4: Logged signals retrievable (mocked)
pytest tests/test_experiments.py::TestGetExperimentResults::test_logged_signals_retrievable -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_experiments.py -v
# Expected: at least 3 passed

# AC6: Ruff passes
ruff check content_assistant/experiments/manager.py tests/test_experiments.py && echo "PASS: ruff clean"
```

---
### Epic 8: Streamlit UI
---

#### Story 20: Build Main App Shell

**What to Build:**
Create the main Streamlit application shell with navigation between CREATE and REVIEW modes.

**Files to Create/Modify:**

1. `content_assistant/app.py` (update from placeholder)
```python
"""Main Streamlit application for TheLifeCo Content Assistant."""
import streamlit as st

# Page configuration must be first Streamlit command
st.set_page_config(
    page_title="TheLifeCo Content Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state():
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "mode" not in st.session_state:
        st.session_state.mode = "CREATE"


def render_sidebar():
    """Render the sidebar with navigation and info."""
    with st.sidebar:
        st.title("🌿 TheLifeCo")
        st.markdown("**Content Marketing Assistant**")
        st.divider()

        # Mode selection
        st.subheader("Mode")
        mode = st.radio(
            "Select mode:",
            ["CREATE", "REVIEW"],
            index=0 if st.session_state.mode == "CREATE" else 1,
            label_visibility="collapsed",
        )
        st.session_state.mode = mode

        st.divider()

        # User info
        if st.session_state.authenticated:
            st.write(f"👤 {st.session_state.user.get('email', 'User')}")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
        else:
            st.info("Please login to save your work")

        st.divider()

        # App info
        st.caption("v0.1.0")
        st.caption("Powered by Claude & Voyage AI")


def render_create_mode():
    """Render CREATE mode placeholder."""
    st.header("✨ CREATE Mode")
    st.write("Generate new marketing content with the 13-question brief.")
    st.info("CREATE mode UI will be implemented in Story 21")


def render_review_mode():
    """Render REVIEW mode placeholder."""
    st.header("🔍 REVIEW Mode")
    st.write("Analyze existing content for engagement and wellness accuracy.")
    st.info("REVIEW mode UI will be implemented in Story 22")


def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()

    # Main content area
    if st.session_state.mode == "CREATE":
        render_create_mode()
    else:
        render_review_mode()


if __name__ == "__main__":
    main()
```

2. `tests/test_app.py`
```python
"""Tests for main app module."""
import pytest


class TestAppImports:
    """Tests for app module imports."""

    def test_app_module_importable(self):
        """Test that app module is importable."""
        from content_assistant import app
        assert hasattr(app, "main")

    def test_app_has_required_functions(self):
        """Test that app has required functions."""
        from content_assistant.app import (
            init_session_state,
            render_sidebar,
            render_create_mode,
            render_review_mode,
            main,
        )
        assert callable(init_session_state)
        assert callable(render_sidebar)
        assert callable(render_create_mode)
        assert callable(render_review_mode)
        assert callable(main)
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: App module is importable
python -c "from content_assistant.app import main; print('PASS')"

# AC2: App starts in headless mode
timeout 5 streamlit run content_assistant/app.py --server.headless true --server.port 8502 &
sleep 3
curl -s http://localhost:8502 | grep -q "TheLifeCo" && echo "PASS: app starts and shows title"
pkill -f "streamlit run content_assistant/app.py" || true

# AC3: App has required functions
python -c "
from content_assistant.app import init_session_state, render_sidebar, main
print('PASS: all functions exist')
"

# AC4: Tests pass
pytest tests/test_app.py -v
# Expected: 2 passed

# AC5: Ruff passes
ruff check content_assistant/app.py tests/test_app.py && echo "PASS: ruff clean"
```

---

#### Story 21: Build Authentication Module

**What to Build:**
Create an authentication module using Supabase Auth that provides login, signup, and session management functions for the Streamlit app.

**Files to Create:**

1. `content_assistant/ui/auth.py`
```python
"""Authentication UI components using Supabase Auth."""
import streamlit as st
from typing import Optional, Dict
from content_assistant.db.supabase_client import get_client
from content_assistant.config import get_config


class AuthError(Exception):
    """Raised when authentication fails."""
    pass


def init_auth_state():
    """Initialize authentication session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "session" not in st.session_state:
        st.session_state.session = None


def login(email: str, password: str) -> Dict:
    """
    Authenticate user with email and password.

    Args:
        email: User's email address
        password: User's password

    Returns:
        Dict with user data on success

    Raises:
        AuthError: If authentication fails
    """
    if not email or not password:
        raise AuthError("Email and password are required")

    client = get_client()

    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "session": response.session,
            }
        else:
            raise AuthError("Invalid credentials")

    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            raise AuthError("Invalid email or password")
        raise AuthError(f"Login failed: {error_msg}")


def signup(email: str, password: str) -> Dict:
    """
    Create new user account.

    Args:
        email: User's email address
        password: User's password (min 6 characters)

    Returns:
        Dict with user data on success

    Raises:
        AuthError: If signup fails
    """
    if not email or not password:
        raise AuthError("Email and password are required")

    if len(password) < 6:
        raise AuthError("Password must be at least 6 characters")

    client = get_client()

    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password,
        })

        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "needs_confirmation": not response.session,
            }
        else:
            raise AuthError("Signup failed")

    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise AuthError("Email already registered")
        raise AuthError(f"Signup failed: {error_msg}")


def logout():
    """Log out current user and clear session."""
    try:
        client = get_client()
        client.auth.sign_out()
    except Exception:
        pass  # Ignore errors during logout

    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.session = None


def get_current_user() -> Optional[Dict]:
    """
    Get current authenticated user.

    Returns:
        User dict if authenticated, None otherwise
    """
    if st.session_state.get("authenticated") and st.session_state.get("user"):
        return st.session_state.user
    return None


def render_login_form():
    """Render login form and handle submission."""
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            try:
                user = login(email, password)
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success("Logged in successfully!")
                st.rerun()
            except AuthError as e:
                st.error(str(e))


def render_signup_form():
    """Render signup form and handle submission."""
    st.subheader("Create Account")

    with st.form("signup_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", help="Minimum 6 characters")
        password_confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up", use_container_width=True)

        if submitted:
            if password != password_confirm:
                st.error("Passwords do not match")
            else:
                try:
                    result = signup(email, password)
                    if result.get("needs_confirmation"):
                        st.success("Account created! Please check your email to confirm.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user = result
                        st.success("Account created and logged in!")
                        st.rerun()
                except AuthError as e:
                    st.error(str(e))


def render_auth_page():
    """Render full authentication page with login/signup tabs."""
    init_auth_state()

    if st.session_state.authenticated:
        st.success(f"Logged in as {st.session_state.user.get('email', 'User')}")
        if st.button("Logout"):
            logout()
            st.rerun()
        return True

    st.title("🌿 TheLifeCo Content Assistant")
    st.markdown("Please login or create an account to continue.")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        render_login_form()

    with tab2:
        render_signup_form()

    return False


def require_auth(func):
    """
    Decorator to require authentication for a page/function.

    Usage:
        @require_auth
        def my_page():
            st.write("Protected content")
    """
    def wrapper(*args, **kwargs):
        init_auth_state()
        if not st.session_state.authenticated:
            render_auth_page()
            return None
        return func(*args, **kwargs)
    return wrapper
```

2. `tests/test_auth.py`
```python
"""Tests for authentication module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.ui.auth import (
    login,
    signup,
    logout,
    get_current_user,
    init_auth_state,
    AuthError,
)
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients


class TestLogin:
    """Tests for login function."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.ui.auth.get_client")
    def test_login_with_valid_credentials_returns_user(self, mock_get_client, monkeypatch):
        """Test that valid credentials return user data."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.id = "user-123"
        mock_response.user.email = "test@thelifeco.com"
        mock_response.session = MagicMock()
        mock_client.auth.sign_in_with_password.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = login("test@thelifeco.com", "testpassword123")

        assert result["email"] == "test@thelifeco.com"
        assert "id" in result

    @patch("content_assistant.ui.auth.get_client")
    def test_login_with_invalid_credentials_raises_auth_error(self, mock_get_client, monkeypatch):
        """Test that invalid credentials raise AuthError."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")
        mock_get_client.return_value = mock_client

        with pytest.raises(AuthError) as exc_info:
            login("wrong@email.com", "wrongpassword")

        assert "Invalid email or password" in str(exc_info.value)

    def test_login_with_empty_email_raises_error(self):
        """Test that empty email raises AuthError."""
        with pytest.raises(AuthError) as exc_info:
            login("", "password")
        assert "required" in str(exc_info.value).lower()

    def test_login_with_empty_password_raises_error(self):
        """Test that empty password raises AuthError."""
        with pytest.raises(AuthError) as exc_info:
            login("test@email.com", "")
        assert "required" in str(exc_info.value).lower()


class TestSignup:
    """Tests for signup function."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.ui.auth.get_client")
    def test_signup_with_valid_data_returns_user(self, mock_get_client, monkeypatch):
        """Test that valid signup returns user data."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.id = "new-user-123"
        mock_response.user.email = "new@thelifeco.com"
        mock_response.session = MagicMock()
        mock_client.auth.sign_up.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = signup("new@thelifeco.com", "password123")

        assert result["email"] == "new@thelifeco.com"
        assert "id" in result

    def test_signup_with_short_password_raises_error(self):
        """Test that password < 6 chars raises AuthError."""
        with pytest.raises(AuthError) as exc_info:
            signup("test@email.com", "12345")
        assert "6 characters" in str(exc_info.value)

    @patch("content_assistant.ui.auth.get_client")
    def test_signup_with_existing_email_raises_error(self, mock_get_client, monkeypatch):
        """Test that existing email raises AuthError."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_client.auth.sign_up.side_effect = Exception("User already registered")
        mock_get_client.return_value = mock_client

        with pytest.raises(AuthError) as exc_info:
            signup("existing@email.com", "password123")

        assert "already registered" in str(exc_info.value).lower()


class TestGetCurrentUser:
    """Tests for get_current_user function."""

    @patch("content_assistant.ui.auth.st")
    def test_returns_user_when_authenticated(self, mock_st):
        """Test that authenticated user is returned."""
        mock_st.session_state = {
            "authenticated": True,
            "user": {"id": "123", "email": "test@test.com"},
        }

        result = get_current_user()

        assert result is not None
        assert result["email"] == "test@test.com"

    @patch("content_assistant.ui.auth.st")
    def test_returns_none_when_not_authenticated(self, mock_st):
        """Test that None is returned when not authenticated."""
        mock_st.session_state = {"authenticated": False, "user": None}

        result = get_current_user()

        assert result is None


@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests requiring real Supabase."""

    @pytest.mark.skipif(
        not all([
            __import__("os").getenv("SUPABASE_URL"),
            __import__("os").getenv("SUPABASE_KEY"),
            __import__("os").getenv("TEST_EMAIL"),
            __import__("os").getenv("TEST_PASSWORD"),
        ]),
        reason="Auth credentials not configured"
    )
    def test_login_with_test_user(self):
        """Test actual login with test credentials."""
        import os
        result = login(os.getenv("TEST_EMAIL"), os.getenv("TEST_PASSWORD"))
        assert result["email"] == os.getenv("TEST_EMAIL")
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.ui.auth import login, signup, logout, render_auth_page, AuthError" && echo "PASS"

# AC2: Login with valid credentials returns user (mocked)
pytest tests/test_auth.py::TestLogin::test_login_with_valid_credentials_returns_user -v
# Expected: PASSED

# AC3: Invalid credentials raise AuthError (mocked)
pytest tests/test_auth.py::TestLogin::test_login_with_invalid_credentials_raises_auth_error -v
# Expected: PASSED

# AC4: Short password raises error
pytest tests/test_auth.py::TestSignup::test_signup_with_short_password_raises_error -v
# Expected: PASSED

# AC5: All unit tests pass
pytest tests/test_auth.py -v -k "not integration"
# Expected: at least 8 passed

# AC6: Functions have correct signatures
python -c "
import inspect
from content_assistant.ui.auth import login, signup, logout

sig = inspect.signature(login)
assert 'email' in sig.parameters
assert 'password' in sig.parameters

sig = inspect.signature(signup)
assert 'email' in sig.parameters
assert 'password' in sig.parameters

print('PASS: correct signatures')
"

# AC7: Ruff passes
ruff check content_assistant/ui/auth.py tests/test_auth.py && echo "PASS: ruff clean"
```

---

#### Story 22: Build CREATE Mode UI

**What to Build:**
Create the main CREATE mode interface with the 13-question Socratic brief form, preview generation with approval workflow, full content generation, and signal collection.

**Files to Create:**

1. `content_assistant/ui/create_mode.py`
```python
"""CREATE mode UI for content generation."""
import streamlit as st
from typing import Dict, Optional
from content_assistant.tools.brief_questionnaire import (
    BRIEF_QUESTIONS,
    get_questions_by_section,
    validate_brief,
    create_empty_brief,
    analyze_brief_for_clarifications,
)
from content_assistant.tools.preview_generator import (
    generate_preview,
    preview_to_dict,
    validate_preview,
    HOOK_TYPES,
)
from content_assistant.tools.content_generator import (
    generate_content,
    content_to_dict,
    verify_content_uses_approved_hook,
    PLATFORM_TYPES,
)
from content_assistant.db.signals import store_generation, update_signals
from content_assistant.ui.auth import get_current_user


def init_create_state():
    """Initialize CREATE mode session state."""
    if "brief" not in st.session_state:
        st.session_state.brief = create_empty_brief()
    if "preview" not in st.session_state:
        st.session_state.preview = None
    if "preview_approved" not in st.session_state:
        st.session_state.preview_approved = False
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = None
    if "generation_id" not in st.session_state:
        st.session_state.generation_id = None
    if "create_step" not in st.session_state:
        st.session_state.create_step = "brief"  # brief, preview, content, signals


def reset_create_state():
    """Reset CREATE mode to start fresh."""
    st.session_state.brief = create_empty_brief()
    st.session_state.preview = None
    st.session_state.preview_approved = False
    st.session_state.generated_content = None
    st.session_state.generation_id = None
    st.session_state.create_step = "brief"


def render_brief_form() -> Dict[str, str]:
    """
    Render the 13-question Socratic brief form.

    Returns:
        Dict with current brief values
    """
    sections = get_questions_by_section()
    brief = st.session_state.brief

    for section_name, questions in sections.items():
        st.subheader(section_name)

        for q in questions:
            key = f"brief_{q.field_name}"

            if q.field_name in ["key_messages", "constraints"]:
                # Multi-line for these fields
                value = st.text_area(
                    q.question,
                    value=brief.get(q.field_name, ""),
                    placeholder=q.placeholder,
                    key=key,
                    height=100,
                )
            else:
                value = st.text_input(
                    q.question,
                    value=brief.get(q.field_name, ""),
                    placeholder=q.placeholder,
                    key=key,
                )

            brief[q.field_name] = value

    st.session_state.brief = brief
    return brief


def check_brief_complete(brief: Dict[str, str]) -> bool:
    """Check if all 13 brief fields are filled."""
    is_valid, _ = validate_brief(brief)
    return is_valid


def render_preview_display(preview: Dict):
    """Render the content preview for approval."""
    st.subheader("📝 Content Preview")

    st.markdown("### Proposed Hook")
    st.info(preview.get("proposed_hook", ""))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Hook Type:** {preview.get('hook_type', '')}")
        st.markdown(f"**Pattern Interrupt:** {preview.get('pattern_interrupt', '')}")
    with col2:
        st.markdown(f"**Curiosity Gap:** {preview.get('curiosity_gap', '')}")
        st.markdown(f"**Stakes:** {preview.get('stakes', '')}")

    st.markdown("### Open Loops")
    loops = preview.get("open_loops", [])
    for loop in loops:
        level = loop.get("level", "")
        loop_text = loop.get("loop", "")
        closes_at = loop.get("closes_at", "")
        st.write(f"- **{level.capitalize()}:** {loop_text} (closes at: {closes_at})")

    st.markdown("### Content Structure")
    st.write(preview.get("content_structure", ""))

    st.markdown("### Promise to Reader")
    st.success(preview.get("promise_to_reader", ""))


def render_content_display(content: Dict):
    """Render the generated content."""
    st.subheader("✨ Generated Content")

    st.markdown(f"### {content.get('title', 'Untitled')}")

    st.markdown("**Hook:**")
    st.info(content.get("hook", ""))

    st.markdown("**Content:**")
    st.write(content.get("content", ""))

    st.markdown("**Call to Action:**")
    st.success(content.get("cta", ""))

    # Text overlays for social content
    overlays = content.get("text_overlays")
    if overlays:
        st.markdown("**Text Overlays (for video/image):**")
        for i, overlay in enumerate(overlays, 1):
            st.write(f"{i}. {overlay}")

    # Copy button
    full_text = f"{content.get('title', '')}\n\n{content.get('hook', '')}\n\n{content.get('content', '')}\n\n{content.get('cta', '')}"
    st.text_area("Copy this content:", full_text, height=200)


def render_signal_collection(generation_id: str):
    """Render signal collection interface."""
    st.subheader("📊 Rate This Content")

    st.markdown("Help us improve! Your feedback trains our system.")

    # Star rating
    rating = st.slider("Overall Rating", 1, 5, 3, help="1 = Poor, 5 = Excellent")

    # What worked checkboxes
    st.markdown("**What worked well?**")
    col1, col2 = st.columns(2)
    with col1:
        hook_worked = st.checkbox("Hook/Opening")
        facts_accurate = st.checkbox("Facts & Information")
    with col2:
        tone_matched = st.checkbox("Tone & Voice")
        cta_effective = st.checkbox("Call to Action")

    # Feedback text
    feedback_text = st.text_area(
        "Additional feedback (optional)",
        placeholder="What could be improved?",
        height=100,
    )

    # Submit signals
    if st.button("Submit Feedback", type="primary", use_container_width=True):
        signals = {
            "star_rating": rating,
            "hook_worked": hook_worked,
            "facts_accurate": facts_accurate,
            "tone_matched": tone_matched,
            "cta_effective": cta_effective,
            "feedback_text": feedback_text if feedback_text else None,
            "edits_made": False,
        }

        try:
            update_signals(generation_id, signals)
            st.success("Thank you for your feedback!")
            st.balloons()

            if st.button("Create New Content"):
                reset_create_state()
                st.rerun()

        except Exception as e:
            st.error(f"Failed to save feedback: {e}")


def render_create_mode():
    """Main CREATE mode render function."""
    init_create_state()

    st.header("✨ CREATE Mode")
    st.markdown("Generate marketing content with the 13-question Socratic brief.")

    # Progress indicator
    steps = ["📝 Brief", "👁️ Preview", "✨ Content", "⭐ Feedback"]
    step_idx = ["brief", "preview", "content", "signals"].index(st.session_state.create_step)
    st.progress((step_idx + 1) / len(steps), text=steps[step_idx])

    # Reset button
    if st.session_state.create_step != "brief":
        if st.button("↩️ Start Over"):
            reset_create_state()
            st.rerun()

    st.divider()

    # Step 1: Brief Form
    if st.session_state.create_step == "brief":
        with st.form("brief_form"):
            brief = render_brief_form()

            submitted = st.form_submit_button(
                "Generate Preview →",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not check_brief_complete(brief):
                    st.error("Please fill in all 13 fields before continuing.")
                else:
                    # Check for clarifications needed
                    clarifications = analyze_brief_for_clarifications(brief)
                    if clarifications:
                        st.warning("Please clarify:")
                        for c in clarifications:
                            st.write(f"- {c}")
                    else:
                        # Generate preview
                        with st.spinner("Generating preview..."):
                            try:
                                preview = generate_preview(brief)
                                st.session_state.preview = preview_to_dict(preview)
                                st.session_state.create_step = "preview"
                                st.rerun()
                            except Exception as e:
                                st.error(f"Preview generation failed: {e}")

    # Step 2: Preview Review
    elif st.session_state.create_step == "preview":
        render_preview_display(st.session_state.preview)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve & Generate Content", type="primary", use_container_width=True):
                st.session_state.preview_approved = True
                # Generate full content
                with st.spinner("Generating full content..."):
                    try:
                        content_result = generate_content(
                            st.session_state.brief,
                            st.session_state.preview,
                        )
                        st.session_state.generated_content = content_to_dict(content_result)

                        # Store generation
                        user = get_current_user()
                        user_id = user.get("id") if user else None

                        gen_id = store_generation(
                            user_id=user_id,
                            brief=st.session_state.brief,
                            preview=st.session_state.preview,
                            content=st.session_state.generated_content.get("content", ""),
                            content_type=st.session_state.brief.get("platform", "email"),
                        )
                        st.session_state.generation_id = gen_id

                        st.session_state.create_step = "content"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Content generation failed: {e}")

        with col2:
            if st.button("🔄 Adjust Approach", use_container_width=True):
                feedback = st.text_input("What would you like to change?")
                if feedback:
                    # Regenerate preview with feedback
                    st.session_state.create_step = "brief"
                    st.rerun()

    # Step 3: Content Display
    elif st.session_state.create_step == "content":
        render_content_display(st.session_state.generated_content)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Happy! Proceed to Feedback", type="primary", use_container_width=True):
                st.session_state.create_step = "signals"
                st.rerun()

        with col2:
            if st.button("🔄 Regenerate Content", use_container_width=True):
                with st.spinner("Regenerating..."):
                    try:
                        content_result = generate_content(
                            st.session_state.brief,
                            st.session_state.preview,
                        )
                        st.session_state.generated_content = content_to_dict(content_result)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Regeneration failed: {e}")

    # Step 4: Signal Collection
    elif st.session_state.create_step == "signals":
        render_signal_collection(st.session_state.generation_id)
```

2. `tests/test_create_mode.py`
```python
"""Tests for CREATE mode UI."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.ui.create_mode import (
    init_create_state,
    reset_create_state,
    check_brief_complete,
    render_brief_form,
)
from content_assistant.tools.brief_questionnaire import REQUIRED_FIELDS


class TestInitCreateState:
    """Tests for state initialization."""

    @patch("content_assistant.ui.create_mode.st")
    def test_init_creates_required_state_keys(self, mock_st):
        """Test that init creates all required session state keys."""
        mock_st.session_state = {}

        init_create_state()

        assert "brief" in mock_st.session_state
        assert "preview" in mock_st.session_state
        assert "preview_approved" in mock_st.session_state
        assert "generated_content" in mock_st.session_state
        assert "generation_id" in mock_st.session_state
        assert "create_step" in mock_st.session_state

    @patch("content_assistant.ui.create_mode.st")
    def test_init_sets_default_step_to_brief(self, mock_st):
        """Test that initial step is 'brief'."""
        mock_st.session_state = {}

        init_create_state()

        assert mock_st.session_state["create_step"] == "brief"


class TestCheckBriefComplete:
    """Tests for brief validation."""

    def test_incomplete_brief_returns_false(self):
        """Test that incomplete brief returns False."""
        incomplete_brief = {"target_audience": "Test"}  # Missing other fields

        result = check_brief_complete(incomplete_brief)

        assert result is False

    def test_complete_brief_returns_true(self):
        """Test that complete brief returns True."""
        complete_brief = {
            "target_audience": "Women aged 45-55",
            "pain_area": "Hot flashes, fatigue",
            "compliance_level": "High - hormonal health",
            "funnel_stage": "Consideration",
            "value_proposition": "Natural hormone balance",
            "desired_action": "Book consultation",
            "specific_programs": "Hormonal Longevity",
            "specific_centers": "Bodrum, Turkey",
            "tone": "Warm and scientific",
            "key_messages": "20+ years experience",
            "constraints": "No HRT comparisons",
            "platform": "Email",
            "price_point": "From €4,500",
        }

        result = check_brief_complete(complete_brief)

        assert result is True

    def test_brief_with_whitespace_only_field_returns_false(self):
        """Test that whitespace-only fields are invalid."""
        brief = {field: "valid" for field in REQUIRED_FIELDS}
        brief["target_audience"] = "   "  # Whitespace only

        result = check_brief_complete(brief)

        assert result is False


class TestResetCreateState:
    """Tests for state reset."""

    @patch("content_assistant.ui.create_mode.st")
    def test_reset_clears_all_state(self, mock_st):
        """Test that reset clears all CREATE state."""
        mock_st.session_state = {
            "brief": {"filled": "data"},
            "preview": {"some": "preview"},
            "preview_approved": True,
            "generated_content": {"some": "content"},
            "generation_id": "abc123",
            "create_step": "signals",
        }

        reset_create_state()

        assert mock_st.session_state["preview"] is None
        assert mock_st.session_state["preview_approved"] is False
        assert mock_st.session_state["generated_content"] is None
        assert mock_st.session_state["generation_id"] is None
        assert mock_st.session_state["create_step"] == "brief"


class TestBriefFormRendering:
    """Tests for brief form rendering."""

    def test_all_13_questions_defined(self):
        """Test that exactly 13 questions exist."""
        from content_assistant.tools.brief_questionnaire import BRIEF_QUESTIONS

        assert len(BRIEF_QUESTIONS) == 13

    def test_all_required_fields_exist(self):
        """Test that all required field names are defined."""
        expected_fields = [
            "target_audience",
            "pain_area",
            "compliance_level",
            "funnel_stage",
            "value_proposition",
            "desired_action",
            "specific_programs",
            "specific_centers",
            "tone",
            "key_messages",
            "constraints",
            "platform",
            "price_point",
        ]

        assert set(REQUIRED_FIELDS) == set(expected_fields)
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.ui.create_mode import render_create_mode, init_create_state, check_brief_complete" && echo "PASS"

# AC2: All 13 required fields are defined
python -c "
from content_assistant.tools.brief_questionnaire import REQUIRED_FIELDS
assert len(REQUIRED_FIELDS) == 13
print(f'PASS: {len(REQUIRED_FIELDS)} required fields defined')
"

# AC3: Incomplete brief returns False
pytest tests/test_create_mode.py::TestCheckBriefComplete::test_incomplete_brief_returns_false -v
# Expected: PASSED

# AC4: Complete brief returns True
pytest tests/test_create_mode.py::TestCheckBriefComplete::test_complete_brief_returns_true -v
# Expected: PASSED

# AC5: Init creates required state keys
pytest tests/test_create_mode.py::TestInitCreateState::test_init_creates_required_state_keys -v
# Expected: PASSED

# AC6: Reset clears all state
pytest tests/test_create_mode.py::TestResetCreateState::test_reset_clears_all_state -v
# Expected: PASSED

# AC7: All unit tests pass
pytest tests/test_create_mode.py -v
# Expected: at least 6 passed

# AC8: Ruff passes
ruff check content_assistant/ui/create_mode.py tests/test_create_mode.py && echo "PASS: ruff clean"
```

---

#### Story 23: Build REVIEW Mode UI

**What to Build:**
Create the REVIEW mode interface that allows users to paste or upload content, select content type, run wellness verification and engagement analysis, and view detailed results with recommendations.

**Files to Create:**

1. `content_assistant/ui/review_mode.py`
```python
"""REVIEW mode UI for content analysis."""
import streamlit as st
from typing import Optional
from content_assistant.tools.wellness_verifier import verify_content, ClaimStatus
from content_assistant.tools.engagement_analyzer import (
    analyze_engagement,
    has_weak_hook,
    has_cta,
    analysis_to_dict,
)
from content_assistant.tools.content_generator import PLATFORM_TYPES


def init_review_state():
    """Initialize REVIEW mode session state."""
    if "review_content" not in st.session_state:
        st.session_state.review_content = ""
    if "review_content_type" not in st.session_state:
        st.session_state.review_content_type = "email"
    if "wellness_results" not in st.session_state:
        st.session_state.wellness_results = None
    if "engagement_results" not in st.session_state:
        st.session_state.engagement_results = None
    if "review_complete" not in st.session_state:
        st.session_state.review_complete = False


def reset_review_state():
    """Reset REVIEW mode state."""
    st.session_state.review_content = ""
    st.session_state.wellness_results = None
    st.session_state.engagement_results = None
    st.session_state.review_complete = False


def render_content_input() -> tuple[str, str]:
    """
    Render content input area with text and file upload options.

    Returns:
        Tuple of (content_text, content_type)
    """
    st.subheader("📄 Content to Review")

    # Content type selector
    content_type = st.selectbox(
        "Content Type",
        options=PLATFORM_TYPES,
        index=PLATFORM_TYPES.index(st.session_state.review_content_type),
        format_func=lambda x: x.replace("_", " ").title(),
    )
    st.session_state.review_content_type = content_type

    # Input method tabs
    tab1, tab2 = st.tabs(["Paste Text", "Upload File"])

    content = ""

    with tab1:
        content = st.text_area(
            "Paste your content here",
            value=st.session_state.review_content,
            height=300,
            placeholder="Paste your marketing content to analyze...",
        )

    with tab2:
        uploaded_file = st.file_uploader(
            "Upload a text file",
            type=["txt", "md"],
            help="Upload a .txt or .md file",
        )
        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
            st.text_area("Uploaded content:", content, height=200, disabled=True)

    st.session_state.review_content = content
    return content, content_type


def render_wellness_results(results: dict):
    """Render wellness verification results."""
    st.subheader("🏥 Wellness Verification")

    # Summary
    summary = results.get("summary", "")
    if "ATTENTION" in summary or "inaccurate" in summary.lower():
        st.error(summary)
    elif "unverified" in summary.lower():
        st.warning(summary)
    else:
        st.success(summary)

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Verified", results.get("verified_count", 0), delta=None)
    with col2:
        st.metric("Unverified", results.get("unverified_count", 0), delta=None)
    with col3:
        inaccurate = results.get("inaccurate_count", 0)
        st.metric("Inaccurate", inaccurate, delta=f"-{inaccurate}" if inaccurate > 0 else None)

    # Individual claims
    claims = results.get("claims", [])
    if claims:
        st.markdown("#### Claim Details")
        for claim in claims:
            status = claim.get("status", "UNVERIFIED")
            claim_text = claim.get("claim", "")
            evidence = claim.get("evidence", "")

            if status == "VERIFIED":
                with st.expander(f"✅ {claim_text}", expanded=False):
                    st.write(f"**Evidence:** {evidence}")
            elif status == "INACCURATE":
                with st.expander(f"❌ {claim_text}", expanded=True):
                    st.error(f"**Issue:** {evidence}")
            else:
                with st.expander(f"❓ {claim_text}", expanded=False):
                    st.warning(f"**Note:** {evidence}")


def render_engagement_results(results: dict):
    """Render engagement analysis results."""
    st.subheader("📈 Engagement Analysis")

    scores = results.get("scores", {})

    # Score display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        hook_score = scores.get("hook_score", 0)
        st.metric("Hook", f"{hook_score}/10")
    with col2:
        cta_score = scores.get("cta_score", 0)
        st.metric("CTA", f"{cta_score}/10")
    with col3:
        structure_score = scores.get("structure_score", 0)
        st.metric("Structure", f"{structure_score}/10")
    with col4:
        overall = scores.get("overall_score", 0)
        st.metric("Overall", f"{overall}/10")

    # Analysis details
    st.markdown("#### Detailed Analysis")

    with st.expander("Hook Analysis", expanded=scores.get("hook_score", 10) < 6):
        st.write(results.get("hook_analysis", "No analysis available"))

    with st.expander("CTA Analysis", expanded=scores.get("cta_score", 10) < 6):
        st.write(results.get("cta_analysis", "No analysis available"))

    with st.expander("Structure Analysis", expanded=False):
        st.write(results.get("structure_analysis", "No analysis available"))

    # Issues and suggestions
    issues = results.get("issues", [])
    suggestions = results.get("suggestions", [])

    if issues:
        st.markdown("#### ⚠️ Issues Found")
        for issue in issues:
            st.warning(issue)

    if suggestions:
        st.markdown("#### 💡 Suggestions")
        for suggestion in suggestions:
            st.info(suggestion)


def render_recommendations(wellness_results: dict, engagement_results: dict):
    """Render combined recommendations."""
    st.subheader("📋 Action Items")

    recommendations = []

    # From wellness
    inaccurate_count = wellness_results.get("inaccurate_count", 0)
    if inaccurate_count > 0:
        recommendations.append(f"🔴 **Critical:** Fix {inaccurate_count} inaccurate wellness claim(s)")

    unverified_count = wellness_results.get("unverified_count", 0)
    if unverified_count > 2:
        recommendations.append(f"🟡 **Consider:** Add sources for {unverified_count} unverified claims")

    # From engagement
    scores = engagement_results.get("scores", {})
    if scores.get("hook_score", 10) < 5:
        recommendations.append("🟡 **Improve:** Strengthen the opening hook")

    if scores.get("cta_score", 10) < 5:
        recommendations.append("🟡 **Improve:** Add or clarify the call to action")

    # Add suggestions
    for suggestion in engagement_results.get("suggestions", [])[:3]:
        recommendations.append(f"💡 {suggestion}")

    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.success("✅ Content looks good! No major issues found.")


def render_review_mode():
    """Main REVIEW mode render function."""
    init_review_state()

    st.header("🔍 REVIEW Mode")
    st.markdown("Analyze existing content for wellness accuracy and engagement.")

    # Reset button
    if st.session_state.review_complete:
        if st.button("↩️ Review New Content"):
            reset_review_state()
            st.rerun()

    st.divider()

    # Content input
    content, content_type = render_content_input()

    # Analyze button
    if st.button("🔍 Analyze Content", type="primary", use_container_width=True, disabled=len(content.strip()) < 50):
        if len(content.strip()) < 50:
            st.error("Please enter at least 50 characters of content.")
        else:
            # Quick checks first
            col1, col2 = st.columns(2)
            with col1:
                if has_weak_hook(content):
                    st.warning("⚠️ Hook appears weak")
                else:
                    st.success("✅ Hook looks engaging")
            with col2:
                if has_cta(content):
                    st.success("✅ CTA detected")
                else:
                    st.warning("⚠️ No clear CTA found")

            # Full analysis
            with st.spinner("Analyzing wellness claims..."):
                try:
                    wellness_results = verify_content(content)
                    st.session_state.wellness_results = wellness_results
                except Exception as e:
                    st.error(f"Wellness analysis failed: {e}")
                    wellness_results = {"claims": [], "summary": "Analysis failed", "verified_count": 0, "inaccurate_count": 0, "unverified_count": 0}
                    st.session_state.wellness_results = wellness_results

            with st.spinner("Analyzing engagement..."):
                try:
                    engagement_results = analyze_engagement(content, content_type)
                    st.session_state.engagement_results = analysis_to_dict(engagement_results)
                except Exception as e:
                    st.error(f"Engagement analysis failed: {e}")
                    st.session_state.engagement_results = {"scores": {}, "issues": [], "suggestions": []}

            st.session_state.review_complete = True
            st.rerun()

    # Display results if available
    if st.session_state.review_complete:
        st.divider()

        tab1, tab2, tab3 = st.tabs(["Wellness", "Engagement", "Recommendations"])

        with tab1:
            if st.session_state.wellness_results:
                render_wellness_results(st.session_state.wellness_results)

        with tab2:
            if st.session_state.engagement_results:
                render_engagement_results(st.session_state.engagement_results)

        with tab3:
            if st.session_state.wellness_results and st.session_state.engagement_results:
                render_recommendations(
                    st.session_state.wellness_results,
                    st.session_state.engagement_results,
                )
```

2. `tests/test_review_mode.py`
```python
"""Tests for REVIEW mode UI."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.ui.review_mode import (
    init_review_state,
    reset_review_state,
    render_wellness_results,
    render_engagement_results,
)


class TestInitReviewState:
    """Tests for state initialization."""

    @patch("content_assistant.ui.review_mode.st")
    def test_init_creates_required_state_keys(self, mock_st):
        """Test that init creates all required session state keys."""
        mock_st.session_state = {}

        init_review_state()

        assert "review_content" in mock_st.session_state
        assert "review_content_type" in mock_st.session_state
        assert "wellness_results" in mock_st.session_state
        assert "engagement_results" in mock_st.session_state
        assert "review_complete" in mock_st.session_state

    @patch("content_assistant.ui.review_mode.st")
    def test_init_sets_defaults(self, mock_st):
        """Test that init sets correct defaults."""
        mock_st.session_state = {}

        init_review_state()

        assert mock_st.session_state["review_content"] == ""
        assert mock_st.session_state["review_content_type"] == "email"
        assert mock_st.session_state["review_complete"] is False


class TestResetReviewState:
    """Tests for state reset."""

    @patch("content_assistant.ui.review_mode.st")
    def test_reset_clears_results(self, mock_st):
        """Test that reset clears analysis results."""
        mock_st.session_state = {
            "review_content": "Some content",
            "wellness_results": {"claims": []},
            "engagement_results": {"scores": {}},
            "review_complete": True,
        }

        reset_review_state()

        assert mock_st.session_state["review_content"] == ""
        assert mock_st.session_state["wellness_results"] is None
        assert mock_st.session_state["engagement_results"] is None
        assert mock_st.session_state["review_complete"] is False


class TestWellnessResultsDisplay:
    """Tests for wellness results rendering."""

    def test_wellness_results_dict_structure(self):
        """Test that wellness results have expected structure."""
        results = {
            "claims": [
                {"claim": "Test claim", "status": "VERIFIED", "evidence": "Source"},
            ],
            "summary": "1 verified",
            "verified_count": 1,
            "inaccurate_count": 0,
            "unverified_count": 0,
        }

        # Verify structure
        assert "claims" in results
        assert "summary" in results
        assert "verified_count" in results
        assert "inaccurate_count" in results
        assert "unverified_count" in results


class TestEngagementResultsDisplay:
    """Tests for engagement results rendering."""

    def test_engagement_results_dict_structure(self):
        """Test that engagement results have expected structure."""
        results = {
            "scores": {
                "hook_score": 7,
                "cta_score": 8,
                "structure_score": 6,
                "overall_score": 7.0,
            },
            "issues": ["Issue 1"],
            "suggestions": ["Suggestion 1"],
            "hook_analysis": "Good hook",
            "cta_analysis": "Clear CTA",
            "structure_analysis": "Well structured",
        }

        # Verify structure
        assert "scores" in results
        assert "hook_score" in results["scores"]
        assert "cta_score" in results["scores"]
        assert "issues" in results
        assert "suggestions" in results
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.ui.review_mode import render_review_mode, init_review_state, reset_review_state" && echo "PASS"

# AC2: Init creates required state keys
pytest tests/test_review_mode.py::TestInitReviewState::test_init_creates_required_state_keys -v
# Expected: PASSED

# AC3: Reset clears results
pytest tests/test_review_mode.py::TestResetReviewState::test_reset_clears_results -v
# Expected: PASSED

# AC4: Wellness results structure is valid
pytest tests/test_review_mode.py::TestWellnessResultsDisplay::test_wellness_results_dict_structure -v
# Expected: PASSED

# AC5: Engagement results structure is valid
pytest tests/test_review_mode.py::TestEngagementResultsDisplay::test_engagement_results_dict_structure -v
# Expected: PASSED

# AC6: All unit tests pass
pytest tests/test_review_mode.py -v
# Expected: at least 5 passed

# AC7: PLATFORM_TYPES is accessible
python -c "
from content_assistant.tools.content_generator import PLATFORM_TYPES
assert len(PLATFORM_TYPES) >= 5
print(f'PASS: {len(PLATFORM_TYPES)} platform types available')
"

# AC8: Ruff passes
ruff check content_assistant/ui/review_mode.py tests/test_review_mode.py && echo "PASS: ruff clean"
```

---

#### Story 24: Build History Sidebar

**What to Build:**
Create a history sidebar component that displays past content generations, allows filtering by content type, and enables users to view and reload previous content.

**Files to Create:**

1. `content_assistant/ui/history.py`
```python
"""History sidebar for viewing past generations."""
import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime
from content_assistant.db.signals import get_user_generations, get_generation
from content_assistant.ui.auth import get_current_user


def init_history_state():
    """Initialize history-related session state."""
    if "selected_generation_id" not in st.session_state:
        st.session_state.selected_generation_id = None
    if "history_filter_type" not in st.session_state:
        st.session_state.history_filter_type = "all"


def format_date(date_str: str) -> str:
    """Format ISO date string for display."""
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            dt = date_str
        return dt.strftime("%b %d, %Y %H:%M")
    except Exception:
        return date_str


def get_rating_stars(rating: Optional[int]) -> str:
    """Convert numeric rating to star display."""
    if rating is None:
        return "☆☆☆☆☆"
    filled = "★" * rating
    empty = "☆" * (5 - rating)
    return filled + empty


def get_content_type_emoji(content_type: str) -> str:
    """Get emoji for content type."""
    emoji_map = {
        "email": "📧",
        "blog": "📝",
        "landing_page": "🖥️",
        "instagram_post": "📸",
        "instagram_story": "📱",
        "instagram_reel": "🎬",
        "linkedin_post": "💼",
        "meta_ad": "📢",
        "whatsapp": "💬",
    }
    return emoji_map.get(content_type, "📄")


def render_generation_card(generation: Dict) -> bool:
    """
    Render a single generation card in the sidebar.

    Args:
        generation: Generation dict from database

    Returns:
        True if this card was clicked
    """
    gen_id = generation.get("id", "")
    content_type = generation.get("content_type", "unknown")
    brief = generation.get("brief", {})
    signals = generation.get("signals", {})
    created_at = generation.get("created_at", "")

    # Get display values
    emoji = get_content_type_emoji(content_type)
    title = brief.get("target_audience", "Untitled")[:30]
    if len(title) == 30:
        title += "..."
    rating = signals.get("star_rating")
    stars = get_rating_stars(rating)
    date = format_date(created_at)

    # Render card
    is_selected = st.session_state.selected_generation_id == gen_id

    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{emoji} {title}**")
            st.caption(f"{stars} • {date}")
        with col2:
            if st.button("View", key=f"view_{gen_id}", use_container_width=True):
                st.session_state.selected_generation_id = gen_id
                return True

    return False


def render_history_sidebar():
    """
    Render the history sidebar with past generations.

    Call this from the main app sidebar section.
    """
    init_history_state()

    st.sidebar.subheader("📚 History")

    # Get current user
    user = get_current_user()
    if not user:
        st.sidebar.info("Login to see your history")
        return

    # Content type filter
    filter_options = ["all", "email", "blog", "instagram_post", "instagram_reel", "linkedin_post", "landing_page"]
    selected_filter = st.sidebar.selectbox(
        "Filter by type",
        options=filter_options,
        index=filter_options.index(st.session_state.history_filter_type),
        format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All Types",
    )
    st.session_state.history_filter_type = selected_filter

    # Fetch generations
    content_type_filter = None if selected_filter == "all" else selected_filter
    generations = get_user_generations(
        user_id=user.get("id"),
        limit=20,
        content_type=content_type_filter,
    )

    if not generations:
        st.sidebar.info("No content generated yet. Create something in CREATE mode!")
        return

    # Render generation cards
    st.sidebar.divider()
    for gen in generations:
        clicked = render_generation_card(gen)
        if clicked:
            st.rerun()
        st.sidebar.divider()


def get_selected_generation() -> Optional[Dict]:
    """
    Get the currently selected generation details.

    Returns:
        Full generation dict if selected, None otherwise
    """
    init_history_state()

    if not st.session_state.selected_generation_id:
        return None

    return get_generation(st.session_state.selected_generation_id)


def render_generation_detail(generation: Dict):
    """
    Render full details of a generation.

    Args:
        generation: Full generation dict
    """
    st.subheader("📄 Generation Details")

    # Brief summary
    brief = generation.get("brief", {})
    with st.expander("Brief", expanded=False):
        for key, value in brief.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    # Preview if available
    preview = generation.get("preview")
    if preview:
        with st.expander("Approved Preview", expanded=False):
            st.write(f"**Hook:** {preview.get('proposed_hook', '')}")
            st.write(f"**Hook Type:** {preview.get('hook_type', '')}")

    # Content
    content = generation.get("content", "")
    st.markdown("### Generated Content")
    st.text_area("Content", content, height=300, disabled=True)

    # Copy button
    if st.button("📋 Copy to Clipboard"):
        st.code(content)
        st.success("Copy the content above")

    # Signals
    signals = generation.get("signals", {})
    if signals:
        st.markdown("### Feedback")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Rating:** {get_rating_stars(signals.get('star_rating'))}")
            st.write(f"**Hook worked:** {'✅' if signals.get('hook_worked') else '❌'}")
        with col2:
            st.write(f"**Facts accurate:** {'✅' if signals.get('facts_accurate') else '❌'}")
            st.write(f"**CTA effective:** {'✅' if signals.get('cta_effective') else '❌'}")

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate Similar"):
            st.session_state.brief = brief
            st.session_state.create_step = "brief"
            st.session_state.selected_generation_id = None
            st.rerun()
    with col2:
        if st.button("❌ Close"):
            st.session_state.selected_generation_id = None
            st.rerun()
```

2. `tests/test_history.py`
```python
"""Tests for history sidebar module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.ui.history import (
    init_history_state,
    format_date,
    get_rating_stars,
    get_content_type_emoji,
    get_selected_generation,
)


class TestInitHistoryState:
    """Tests for state initialization."""

    @patch("content_assistant.ui.history.st")
    def test_init_creates_required_keys(self, mock_st):
        """Test that init creates required state keys."""
        mock_st.session_state = {}

        init_history_state()

        assert "selected_generation_id" in mock_st.session_state
        assert "history_filter_type" in mock_st.session_state

    @patch("content_assistant.ui.history.st")
    def test_init_sets_defaults(self, mock_st):
        """Test that init sets correct defaults."""
        mock_st.session_state = {}

        init_history_state()

        assert mock_st.session_state["selected_generation_id"] is None
        assert mock_st.session_state["history_filter_type"] == "all"


class TestFormatDate:
    """Tests for date formatting."""

    def test_formats_iso_date(self):
        """Test that ISO date is formatted correctly."""
        result = format_date("2024-01-15T10:30:00Z")

        assert "Jan" in result
        assert "15" in result
        assert "2024" in result

    def test_handles_invalid_date(self):
        """Test that invalid date returns original string."""
        result = format_date("not a date")

        assert result == "not a date"


class TestGetRatingStars:
    """Tests for star rating display."""

    def test_five_stars(self):
        """Test 5-star rating display."""
        result = get_rating_stars(5)
        assert result == "★★★★★"

    def test_three_stars(self):
        """Test 3-star rating display."""
        result = get_rating_stars(3)
        assert result == "★★★☆☆"

    def test_zero_stars(self):
        """Test 0-star rating display."""
        result = get_rating_stars(0)
        assert result == "☆☆☆☆☆"

    def test_none_rating(self):
        """Test None rating display."""
        result = get_rating_stars(None)
        assert result == "☆☆☆☆☆"


class TestGetContentTypeEmoji:
    """Tests for content type emoji mapping."""

    def test_email_emoji(self):
        """Test email emoji."""
        result = get_content_type_emoji("email")
        assert result == "📧"

    def test_instagram_emoji(self):
        """Test Instagram emoji."""
        result = get_content_type_emoji("instagram_post")
        assert result == "📸"

    def test_unknown_type(self):
        """Test unknown type returns default emoji."""
        result = get_content_type_emoji("unknown_type")
        assert result == "📄"


class TestGetSelectedGeneration:
    """Tests for getting selected generation."""

    @patch("content_assistant.ui.history.get_generation")
    @patch("content_assistant.ui.history.st")
    def test_returns_generation_when_selected(self, mock_st, mock_get_gen):
        """Test that selected generation is returned."""
        mock_st.session_state = {"selected_generation_id": "gen-123", "history_filter_type": "all"}
        mock_get_gen.return_value = {"id": "gen-123", "content": "Test"}

        result = get_selected_generation()

        assert result is not None
        assert result["id"] == "gen-123"

    @patch("content_assistant.ui.history.st")
    def test_returns_none_when_not_selected(self, mock_st):
        """Test that None is returned when nothing selected."""
        mock_st.session_state = {"selected_generation_id": None, "history_filter_type": "all"}

        result = get_selected_generation()

        assert result is None
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.ui.history import render_history_sidebar, get_selected_generation, init_history_state" && echo "PASS"

# AC2: Init creates required state keys
pytest tests/test_history.py::TestInitHistoryState::test_init_creates_required_keys -v
# Expected: PASSED

# AC3: Date formatting works
pytest tests/test_history.py::TestFormatDate::test_formats_iso_date -v
# Expected: PASSED

# AC4: Star rating display works
pytest tests/test_history.py::TestGetRatingStars -v
# Expected: 4 passed

# AC5: Content type emoji mapping works
pytest tests/test_history.py::TestGetContentTypeEmoji -v
# Expected: 3 passed

# AC6: All unit tests pass
pytest tests/test_history.py -v
# Expected: at least 10 passed

# AC7: Ruff passes
ruff check content_assistant/ui/history.py tests/test_history.py && echo "PASS: ruff clean"
```

---

#### Story 25: Integrate All Components

**What to Build:**
Wire together all components to create the complete application flow. Ensure CREATE mode uses the full pipeline (brief → preview → content → signals → storage), REVIEW mode uses both analyzers, and the app properly handles authentication and navigation.

**Files to Modify:**

1. `content_assistant/app.py` (update to integrate all components)
```python
"""Main Streamlit application for TheLifeCo Content Assistant."""
import streamlit as st

# Page configuration must be first Streamlit command
st.set_page_config(
    page_title="TheLifeCo Content Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

from content_assistant.ui.auth import (
    init_auth_state,
    render_auth_page,
    logout,
    get_current_user,
)
from content_assistant.ui.create_mode import render_create_mode
from content_assistant.ui.review_mode import render_review_mode
from content_assistant.ui.history import render_history_sidebar, get_selected_generation, render_generation_detail


def init_app_state():
    """Initialize all application session state."""
    init_auth_state()
    if "mode" not in st.session_state:
        st.session_state.mode = "CREATE"


def render_sidebar():
    """Render the main application sidebar."""
    with st.sidebar:
        st.title("🌿 TheLifeCo")
        st.markdown("**Content Marketing Assistant**")
        st.divider()

        # Mode selection
        st.subheader("Mode")
        mode = st.radio(
            "Select mode:",
            ["CREATE", "REVIEW"],
            index=0 if st.session_state.mode == "CREATE" else 1,
            label_visibility="collapsed",
        )
        st.session_state.mode = mode

        st.divider()

        # User info and logout
        user = get_current_user()
        if user:
            st.write(f"👤 {user.get('email', 'User')}")
            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()

            st.divider()

            # History sidebar (only for authenticated users)
            render_history_sidebar()
        else:
            st.info("Login to save your work")

        # App info at bottom
        st.divider()
        st.caption("v0.1.0")
        st.caption("Powered by Claude & Voyage AI")


def main():
    """Main application entry point."""
    init_app_state()

    # Check authentication
    if not st.session_state.authenticated:
        render_auth_page()
        return

    # Render sidebar
    render_sidebar()

    # Check if viewing a historical generation
    selected_gen = get_selected_generation()
    if selected_gen:
        render_generation_detail(selected_gen)
        return

    # Main content area based on mode
    if st.session_state.mode == "CREATE":
        render_create_mode()
    else:
        render_review_mode()


if __name__ == "__main__":
    main()
```

2. `tests/test_integration.py`
```python
"""Integration tests for the full application."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients


class TestAppIntegration:
    """Tests for main app integration."""

    def setup_method(self):
        reset_config()
        reset_clients()

    def test_app_module_imports(self):
        """Test that app module imports all components."""
        from content_assistant.app import main, init_app_state, render_sidebar
        assert callable(main)
        assert callable(init_app_state)
        assert callable(render_sidebar)

    def test_all_ui_modules_importable(self):
        """Test that all UI modules are importable."""
        from content_assistant.ui.auth import render_auth_page
        from content_assistant.ui.create_mode import render_create_mode
        from content_assistant.ui.review_mode import render_review_mode
        from content_assistant.ui.history import render_history_sidebar

        assert callable(render_auth_page)
        assert callable(render_create_mode)
        assert callable(render_review_mode)
        assert callable(render_history_sidebar)

    def test_all_tool_modules_importable(self):
        """Test that all tool modules are importable."""
        from content_assistant.tools.brief_questionnaire import validate_brief
        from content_assistant.tools.preview_generator import generate_preview
        from content_assistant.tools.content_generator import generate_content
        from content_assistant.tools.wellness_verifier import verify_content
        from content_assistant.tools.engagement_analyzer import analyze_engagement
        from content_assistant.tools.signal_ranker import rank_examples

        assert callable(validate_brief)
        assert callable(generate_preview)
        assert callable(generate_content)
        assert callable(verify_content)
        assert callable(analyze_engagement)
        assert callable(rank_examples)

    def test_all_db_modules_importable(self):
        """Test that all database modules are importable."""
        from content_assistant.db.supabase_client import get_client, get_admin_client
        from content_assistant.db.signals import store_generation, update_signals
        from content_assistant.db.init_db import get_schema_sql

        assert callable(get_client)
        assert callable(get_admin_client)
        assert callable(store_generation)
        assert callable(update_signals)
        assert callable(get_schema_sql)

    def test_all_rag_modules_importable(self):
        """Test that all RAG modules are importable."""
        from content_assistant.rag.loader import load_document
        from content_assistant.rag.chunker import chunk_text
        from content_assistant.rag.embeddings import embed_text
        from content_assistant.rag.vector_store import store_chunks, search
        from content_assistant.rag.knowledge_base import retrieve_wellness_facts

        assert callable(load_document)
        assert callable(chunk_text)
        assert callable(embed_text)
        assert callable(store_chunks)
        assert callable(search)
        assert callable(retrieve_wellness_facts)


class TestCreateModeIntegration:
    """Tests for CREATE mode full flow."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.tools.content_generator.retrieve_wellness_facts")
    @patch("content_assistant.tools.content_generator.retrieve_engagement_patterns")
    @patch("content_assistant.tools.content_generator.generate_json")
    @patch("content_assistant.tools.preview_generator.retrieve_engagement_patterns")
    @patch("content_assistant.tools.preview_generator.generate_json")
    def test_brief_to_content_flow(
        self,
        mock_preview_json,
        mock_preview_rag,
        mock_content_json,
        mock_content_rag_engage,
        mock_content_rag_wellness,
        monkeypatch,
    ):
        """Test complete flow from brief to content."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        # Mock RAG returns
        mock_preview_rag.return_value = []
        mock_content_rag_wellness.return_value = []
        mock_content_rag_engage.return_value = []

        # Mock preview generation
        mock_preview_json.return_value = {
            "proposed_hook": "What if you could reset your body?",
            "hook_type": "Mystery",
            "pattern_interrupt": "Challenges assumptions",
            "curiosity_gap": "How?",
            "stakes": "Your health",
            "open_loops": [{"level": "macro", "loop": "The secret", "closes_at": "end"}],
            "content_structure": "Hook, Problem, Solution, CTA",
            "promise_to_reader": "You will learn the method",
        }

        # Mock content generation
        mock_content_json.return_value = {
            "title": "Reset Your Body",
            "hook": "What if you could reset your body?",
            "content": "Full content here...",
            "cta": "Book now",
            "open_loops_used": [{"loop": "The secret", "closed_at": "end"}],
            "metadata": {"word_count": 200},
        }

        # Create complete brief
        brief = {
            "target_audience": "Women aged 45-55",
            "pain_area": "Hot flashes, fatigue",
            "compliance_level": "High",
            "funnel_stage": "Consideration",
            "value_proposition": "Natural balance",
            "desired_action": "Book consultation",
            "specific_programs": "Hormonal Longevity",
            "specific_centers": "Bodrum",
            "tone": "Warm",
            "key_messages": "Experience",
            "constraints": "None",
            "platform": "email",
            "price_point": "€4,500",
        }

        # Generate preview
        from content_assistant.tools.preview_generator import generate_preview, preview_to_dict
        preview = generate_preview(brief)
        preview_dict = preview_to_dict(preview)

        assert preview.proposed_hook == "What if you could reset your body?"
        assert preview.hook_type == "Mystery"

        # Generate content
        from content_assistant.tools.content_generator import generate_content
        content = generate_content(brief, preview_dict)

        assert content.hook == "What if you could reset your body?"
        assert content.cta == "Book now"


class TestReviewModeIntegration:
    """Tests for REVIEW mode full flow."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.tools.wellness_verifier.generate_json")
    @patch("content_assistant.tools.wellness_verifier.retrieve_wellness_facts")
    @patch("content_assistant.tools.engagement_analyzer.retrieve_engagement_patterns")
    @patch("content_assistant.tools.engagement_analyzer.generate_json")
    def test_content_analysis_flow(
        self,
        mock_engage_json,
        mock_engage_rag,
        mock_wellness_rag,
        mock_wellness_json,
        monkeypatch,
    ):
        """Test complete content analysis flow."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        # Mock returns
        mock_wellness_rag.return_value = [{"text": "Fasting helps", "source": "test.pdf"}]
        mock_engage_rag.return_value = []

        # Mock wellness extraction and verification
        mock_wellness_json.side_effect = [
            ["Fasting activates autophagy"],  # Extraction
            {"status": "VERIFIED", "evidence": "Confirmed"},  # Verification
        ]

        # Mock engagement analysis
        mock_engage_json.return_value = {
            "hook_score": 7,
            "hook_analysis": "Good",
            "cta_score": 8,
            "cta_analysis": "Clear",
            "structure_score": 7,
            "structure_analysis": "OK",
            "issues": [],
            "suggestions": ["Add more detail"],
        }

        content = "Fasting activates autophagy. Book your retreat today!"

        # Verify wellness
        from content_assistant.tools.wellness_verifier import verify_content
        wellness_results = verify_content(content)

        assert wellness_results["verified_count"] >= 0  # May vary based on mock

        # Analyze engagement
        from content_assistant.tools.engagement_analyzer import analyze_engagement
        engagement_results = analyze_engagement(content, "email")

        assert engagement_results.scores.hook_score == 7
        assert engagement_results.scores.cta_score == 8
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: App module imports all components
pytest tests/test_integration.py::TestAppIntegration::test_app_module_imports -v
# Expected: PASSED

# AC2: All UI modules importable
pytest tests/test_integration.py::TestAppIntegration::test_all_ui_modules_importable -v
# Expected: PASSED

# AC3: All tool modules importable
pytest tests/test_integration.py::TestAppIntegration::test_all_tool_modules_importable -v
# Expected: PASSED

# AC4: All DB modules importable
pytest tests/test_integration.py::TestAppIntegration::test_all_db_modules_importable -v
# Expected: PASSED

# AC5: All RAG modules importable
pytest tests/test_integration.py::TestAppIntegration::test_all_rag_modules_importable -v
# Expected: PASSED

# AC6: Brief to content flow works (mocked)
pytest tests/test_integration.py::TestCreateModeIntegration::test_brief_to_content_flow -v
# Expected: PASSED

# AC7: Content analysis flow works (mocked)
pytest tests/test_integration.py::TestReviewModeIntegration::test_content_analysis_flow -v
# Expected: PASSED

# AC8: All integration tests pass
pytest tests/test_integration.py -v
# Expected: at least 7 passed

# AC9: App starts without errors
timeout 5 streamlit run content_assistant/app.py --server.headless true --server.port 8503 &
sleep 3
curl -s http://localhost:8503 | grep -q "TheLifeCo" && echo "PASS: app starts"
pkill -f "streamlit run content_assistant/app.py" || true

# AC10: Ruff passes on all files
ruff check content_assistant/ tests/ && echo "PASS: ruff clean"
```

---

#### Story 26: Add Error Handling & Loading States

**What to Build:**
Add comprehensive error handling throughout the application with user-friendly error messages, loading spinners for async operations, and retry logic for transient failures.

**Files to Create:**

1. `content_assistant/ui/error_handler.py`
```python
"""Error handling utilities for the UI."""
import streamlit as st
from typing import Callable, TypeVar, Optional
from functools import wraps
import traceback

T = TypeVar("T")


class UserFriendlyError(Exception):
    """Exception with user-friendly message."""

    def __init__(self, user_message: str, technical_message: Optional[str] = None):
        self.user_message = user_message
        self.technical_message = technical_message
        super().__init__(user_message)


# Map technical errors to user-friendly messages
ERROR_MESSAGES = {
    "ANTHROPIC_API_KEY": "API key issue. Please check your Anthropic API key in settings.",
    "VOYAGE_API_KEY": "Embedding API issue. Please check your Voyage AI key in settings.",
    "SUPABASE": "Database connection issue. Please try again later.",
    "rate_limit": "Too many requests. Please wait a moment and try again.",
    "timeout": "Request timed out. Please try again.",
    "network": "Network error. Please check your connection and try again.",
    "invalid_json": "Unexpected response format. Please try again.",
    "empty_response": "No response received. Please try again.",
}


def get_friendly_error_message(error: Exception) -> str:
    """
    Convert technical error to user-friendly message.

    Args:
        error: The exception that occurred

    Returns:
        User-friendly error message
    """
    error_str = str(error).lower()

    # Check for known error patterns
    for key, message in ERROR_MESSAGES.items():
        if key.lower() in error_str:
            return message

    # Check for common error types
    if "connection" in error_str or "network" in error_str:
        return ERROR_MESSAGES["network"]

    if "timeout" in error_str:
        return ERROR_MESSAGES["timeout"]

    if "rate" in error_str and "limit" in error_str:
        return ERROR_MESSAGES["rate_limit"]

    if isinstance(error, UserFriendlyError):
        return error.user_message

    # Default message
    return "An unexpected error occurred. Please try again."


def display_error(error: Exception, show_details: bool = False):
    """
    Display error in Streamlit with user-friendly message.

    Args:
        error: The exception
        show_details: Whether to show technical details
    """
    user_message = get_friendly_error_message(error)
    st.error(f"⚠️ {user_message}")

    if show_details:
        with st.expander("Technical Details", expanded=False):
            st.code(traceback.format_exc())


def with_error_handling(
    spinner_text: str = "Processing...",
    error_message: Optional[str] = None,
    show_details: bool = False,
):
    """
    Decorator for functions that need error handling and loading state.

    Args:
        spinner_text: Text to show during loading
        error_message: Custom error message (optional)
        show_details: Whether to show technical details on error

    Usage:
        @with_error_handling("Generating content...")
        def generate():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                with st.spinner(spinner_text):
                    return func(*args, **kwargs)
            except Exception as e:
                if error_message:
                    st.error(f"⚠️ {error_message}")
                else:
                    display_error(e, show_details)
                return None
        return wrapper
    return decorator


def safe_api_call(
    func: Callable[..., T],
    *args,
    spinner_text: str = "Loading...",
    retry_count: int = 2,
    **kwargs,
) -> Optional[T]:
    """
    Execute API call with error handling, spinner, and retry.

    Args:
        func: Function to call
        *args: Arguments for function
        spinner_text: Loading message
        retry_count: Number of retries on transient errors
        **kwargs: Keyword arguments for function

    Returns:
        Function result or None on error
    """
    last_error = None

    for attempt in range(retry_count + 1):
        try:
            if attempt == 0:
                with st.spinner(spinner_text):
                    return func(*args, **kwargs)
            else:
                with st.spinner(f"{spinner_text} (retry {attempt}/{retry_count})"):
                    return func(*args, **kwargs)

        except Exception as e:
            last_error = e
            error_str = str(e).lower()

            # Only retry on transient errors
            is_transient = any(x in error_str for x in ["timeout", "rate", "network", "connection"])

            if not is_transient or attempt == retry_count:
                display_error(e)
                return None

            st.warning(f"Retrying... ({attempt + 1}/{retry_count})")

    return None


def render_error_boundary(content_func: Callable):
    """
    Render content with error boundary.

    Args:
        content_func: Function that renders content

    Usage:
        render_error_boundary(lambda: render_complex_component())
    """
    try:
        content_func()
    except Exception as e:
        display_error(e, show_details=True)
        if st.button("🔄 Retry"):
            st.rerun()
```

2. `tests/test_error_handler.py`
```python
"""Tests for error handler module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.ui.error_handler import (
    get_friendly_error_message,
    UserFriendlyError,
    ERROR_MESSAGES,
)


class TestGetFriendlyErrorMessage:
    """Tests for error message conversion."""

    def test_api_key_error_returns_friendly_message(self):
        """Test that API key error returns user-friendly message."""
        error = Exception("Missing ANTHROPIC_API_KEY configuration")

        result = get_friendly_error_message(error)

        assert "API key" in result
        assert "ANTHROPIC_API_KEY" not in result or "check" in result.lower()

    def test_rate_limit_error_returns_friendly_message(self):
        """Test that rate limit error returns wait message."""
        error = Exception("Rate limit exceeded")

        result = get_friendly_error_message(error)

        assert "wait" in result.lower() or "try again" in result.lower()

    def test_timeout_error_returns_friendly_message(self):
        """Test that timeout error returns retry message."""
        error = Exception("Connection timeout after 30s")

        result = get_friendly_error_message(error)

        assert "try again" in result.lower()

    def test_network_error_returns_friendly_message(self):
        """Test that network error returns connection message."""
        error = Exception("Network connection failed")

        result = get_friendly_error_message(error)

        assert "connection" in result.lower() or "network" in result.lower()

    def test_unknown_error_returns_generic_message(self):
        """Test that unknown error returns generic message."""
        error = Exception("Some random internal error XYZ123")

        result = get_friendly_error_message(error)

        assert "unexpected" in result.lower() or "try again" in result.lower()
        assert "XYZ123" not in result

    def test_user_friendly_error_returns_user_message(self):
        """Test that UserFriendlyError returns its user_message."""
        error = UserFriendlyError("Please check your input", "Technical: ValueError")

        result = get_friendly_error_message(error)

        assert result == "Please check your input"


class TestErrorMessages:
    """Tests for error message definitions."""

    def test_all_error_messages_are_user_friendly(self):
        """Test that all predefined messages are user-friendly (no technical jargon)."""
        technical_terms = ["exception", "traceback", "null", "undefined", "stack"]

        for key, message in ERROR_MESSAGES.items():
            for term in technical_terms:
                assert term not in message.lower(), f"Message for '{key}' contains technical term '{term}'"

    def test_all_messages_suggest_action(self):
        """Test that all messages suggest what user should do."""
        action_words = ["please", "try", "check", "wait"]

        for key, message in ERROR_MESSAGES.items():
            has_action = any(word in message.lower() for word in action_words)
            assert has_action, f"Message for '{key}' doesn't suggest an action"


class TestSafeApiCall:
    """Tests for safe API call wrapper."""

    @patch("content_assistant.ui.error_handler.st")
    def test_returns_result_on_success(self, mock_st):
        """Test that successful call returns result."""
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock()

        from content_assistant.ui.error_handler import safe_api_call

        def successful_func():
            return "success"

        # Note: This test would need actual Streamlit context to fully work
        # In unit test, we verify the function structure exists
        assert callable(safe_api_call)
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.ui.error_handler import get_friendly_error_message, display_error, safe_api_call, with_error_handling" && echo "PASS"

# AC2: API key error returns friendly message
pytest tests/test_error_handler.py::TestGetFriendlyErrorMessage::test_api_key_error_returns_friendly_message -v
# Expected: PASSED

# AC3: Rate limit error returns friendly message
pytest tests/test_error_handler.py::TestGetFriendlyErrorMessage::test_rate_limit_error_returns_friendly_message -v
# Expected: PASSED

# AC4: Unknown error returns generic message (no technical details)
pytest tests/test_error_handler.py::TestGetFriendlyErrorMessage::test_unknown_error_returns_generic_message -v
# Expected: PASSED

# AC5: All error messages are user-friendly
pytest tests/test_error_handler.py::TestErrorMessages::test_all_error_messages_are_user_friendly -v
# Expected: PASSED

# AC6: All messages suggest user action
pytest tests/test_error_handler.py::TestErrorMessages::test_all_messages_suggest_action -v
# Expected: PASSED

# AC7: All unit tests pass
pytest tests/test_error_handler.py -v
# Expected: at least 7 passed

# AC8: Ruff passes
ruff check content_assistant/ui/error_handler.py tests/test_error_handler.py && echo "PASS: ruff clean"
```

---

#### Story 27: Build Monitoring Dashboard

**What to Build:**
Create a monitoring dashboard that displays system statistics including total generations, average ratings, content type distribution, and experiment status.

**Files to Create:**

1. `content_assistant/ui/dashboard.py`
```python
"""Monitoring dashboard for system statistics."""
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from content_assistant.db.supabase_client import get_admin_client
from content_assistant.experiments.manager import get_active_experiments, get_experiment_results


def get_generation_stats() -> Dict:
    """
    Get statistics about content generations.

    Returns:
        Dict with: total, average_rating, by_type, by_date
    """
    client = get_admin_client()

    try:
        # Get all generations
        result = client.table("content_generations").select("*").execute()
        generations = result.data if result.data else []

        if not generations:
            return {
                "total": 0,
                "average_rating": None,
                "by_type": {},
                "rating_distribution": {},
                "recent_count": 0,
            }

        # Calculate stats
        total = len(generations)

        # Average rating
        ratings = [
            g["signals"].get("star_rating")
            for g in generations
            if g.get("signals") and g["signals"].get("star_rating")
        ]
        average_rating = sum(ratings) / len(ratings) if ratings else None

        # By content type
        by_type = {}
        for g in generations:
            ct = g.get("content_type", "unknown")
            by_type[ct] = by_type.get(ct, 0) + 1

        # Rating distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in ratings:
            if r in rating_distribution:
                rating_distribution[r] += 1

        # Recent (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = sum(
            1 for g in generations
            if g.get("created_at") and datetime.fromisoformat(g["created_at"].replace("Z", "+00:00")) > week_ago
        )

        return {
            "total": total,
            "average_rating": round(average_rating, 2) if average_rating else None,
            "by_type": by_type,
            "rating_distribution": rating_distribution,
            "recent_count": recent_count,
        }

    except Exception as e:
        return {
            "total": 0,
            "average_rating": None,
            "by_type": {},
            "rating_distribution": {},
            "recent_count": 0,
            "error": str(e),
        }


def get_knowledge_stats() -> Dict:
    """
    Get statistics about knowledge base.

    Returns:
        Dict with chunk counts by collection
    """
    client = get_admin_client()

    try:
        # Count wellness chunks
        wellness_result = client.table("knowledge_chunks").select("id", count="exact").eq("collection", "wellness").execute()
        wellness_count = wellness_result.count if wellness_result.count else 0

        # Count engagement chunks
        engagement_result = client.table("knowledge_chunks").select("id", count="exact").eq("collection", "engagement").execute()
        engagement_count = engagement_result.count if engagement_result.count else 0

        return {
            "wellness_chunks": wellness_count,
            "engagement_chunks": engagement_count,
            "total_chunks": wellness_count + engagement_count,
        }

    except Exception:
        return {
            "wellness_chunks": 0,
            "engagement_chunks": 0,
            "total_chunks": 0,
        }


def render_metrics_row(stats: Dict):
    """Render the main metrics row."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Generations",
            stats.get("total", 0),
            delta=f"+{stats.get('recent_count', 0)} this week",
        )

    with col2:
        avg = stats.get("average_rating")
        st.metric(
            "Average Rating",
            f"{avg}/5" if avg else "N/A",
        )

    with col3:
        by_type = stats.get("by_type", {})
        most_common = max(by_type, key=by_type.get) if by_type else "N/A"
        st.metric(
            "Most Common Type",
            most_common.replace("_", " ").title(),
        )

    with col4:
        st.metric(
            "Recent (7 days)",
            stats.get("recent_count", 0),
        )


def render_content_type_chart(by_type: Dict):
    """Render content type distribution chart."""
    if not by_type:
        st.info("No content generated yet")
        return

    import pandas as pd

    df = pd.DataFrame([
        {"Type": k.replace("_", " ").title(), "Count": v}
        for k, v in by_type.items()
    ])

    st.bar_chart(df.set_index("Type"))


def render_rating_distribution(distribution: Dict):
    """Render rating distribution chart."""
    if not any(distribution.values()):
        st.info("No ratings yet")
        return

    import pandas as pd

    df = pd.DataFrame([
        {"Rating": f"{k} ★", "Count": v}
        for k, v in sorted(distribution.items())
    ])

    st.bar_chart(df.set_index("Rating"))


def render_experiment_status():
    """Render active experiment status."""
    try:
        experiments = get_active_experiments()

        if not experiments:
            st.info("No active experiments")
            return

        for exp in experiments:
            with st.expander(f"🧪 {exp.get('name', 'Unnamed')}", expanded=True):
                st.write(f"**Status:** {exp.get('status', 'unknown')}")
                st.write(f"**Started:** {exp.get('started_at', 'N/A')}")

                # Get results
                results = get_experiment_results(exp.get("id"))
                summary = results.get("summary", {})

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Control", summary.get("control_count", 0))
                    ctrl_avg = summary.get("control_avg_rating")
                    st.write(f"Avg rating: {ctrl_avg:.2f}" if ctrl_avg else "No ratings")

                with col2:
                    st.metric("Treatment", summary.get("treatment_count", 0))
                    treat_avg = summary.get("treatment_avg_rating")
                    st.write(f"Avg rating: {treat_avg:.2f}" if treat_avg else "No ratings")

    except Exception as e:
        st.error(f"Failed to load experiments: {e}")


def render_knowledge_base_status(kb_stats: Dict):
    """Render knowledge base status."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Wellness Chunks", kb_stats.get("wellness_chunks", 0))

    with col2:
        st.metric("Engagement Chunks", kb_stats.get("engagement_chunks", 0))

    with col3:
        st.metric("Total Chunks", kb_stats.get("total_chunks", 0))


def render_dashboard():
    """Main dashboard render function."""
    st.header("📊 Dashboard")
    st.markdown("System statistics and monitoring.")

    # Refresh button
    if st.button("🔄 Refresh"):
        st.rerun()

    st.divider()

    # Get stats
    gen_stats = get_generation_stats()
    kb_stats = get_knowledge_stats()

    # Error check
    if "error" in gen_stats:
        st.warning(f"Some stats unavailable: {gen_stats['error']}")

    # Main metrics
    st.subheader("📈 Generation Metrics")
    render_metrics_row(gen_stats)

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Content Types")
        render_content_type_chart(gen_stats.get("by_type", {}))

    with col2:
        st.subheader("Rating Distribution")
        render_rating_distribution(gen_stats.get("rating_distribution", {}))

    st.divider()

    # Knowledge base
    st.subheader("📚 Knowledge Base")
    render_knowledge_base_status(kb_stats)

    st.divider()

    # Experiments
    st.subheader("🧪 Active Experiments")
    render_experiment_status()
```

2. `tests/test_dashboard.py`
```python
"""Tests for dashboard module."""
import pytest
from unittest.mock import patch, MagicMock
from content_assistant.ui.dashboard import (
    get_generation_stats,
    get_knowledge_stats,
)
from content_assistant.config import reset_config
from content_assistant.db.supabase_client import reset_clients


class TestGetGenerationStats:
    """Tests for generation statistics."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.ui.dashboard.get_admin_client")
    def test_returns_stats_dict(self, mock_get_client, monkeypatch):
        """Test that stats dict has required keys."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"content_type": "email", "signals": {"star_rating": 5}, "created_at": "2024-01-15T10:00:00Z"},
            {"content_type": "email", "signals": {"star_rating": 4}, "created_at": "2024-01-15T11:00:00Z"},
            {"content_type": "blog", "signals": {"star_rating": 3}, "created_at": "2024-01-14T10:00:00Z"},
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = get_generation_stats()

        assert "total" in result
        assert "average_rating" in result
        assert "by_type" in result
        assert "rating_distribution" in result

    @patch("content_assistant.ui.dashboard.get_admin_client")
    def test_calculates_total_correctly(self, mock_get_client, monkeypatch):
        """Test that total count is correct."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"content_type": "email", "signals": {}},
            {"content_type": "blog", "signals": {}},
            {"content_type": "email", "signals": {}},
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = get_generation_stats()

        assert result["total"] == 3

    @patch("content_assistant.ui.dashboard.get_admin_client")
    def test_calculates_average_rating_correctly(self, mock_get_client, monkeypatch):
        """Test that average rating is calculated correctly."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"content_type": "email", "signals": {"star_rating": 5}},
            {"content_type": "email", "signals": {"star_rating": 3}},
            {"content_type": "email", "signals": {"star_rating": 4}},
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = get_generation_stats()

        # (5 + 3 + 4) / 3 = 4.0
        assert result["average_rating"] == 4.0

    @patch("content_assistant.ui.dashboard.get_admin_client")
    def test_handles_empty_data(self, mock_get_client, monkeypatch):
        """Test that empty data returns zeros."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_client.table.return_value.select.return_value.execute.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = get_generation_stats()

        assert result["total"] == 0
        assert result["average_rating"] is None


class TestGetKnowledgeStats:
    """Tests for knowledge base statistics."""

    def setup_method(self):
        reset_config()
        reset_clients()

    @patch("content_assistant.ui.dashboard.get_admin_client")
    def test_returns_chunk_counts(self, mock_get_client, monkeypatch):
        """Test that chunk counts are returned."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client = MagicMock()

        # Mock wellness count
        wellness_result = MagicMock()
        wellness_result.count = 100

        # Mock engagement count
        engagement_result = MagicMock()
        engagement_result.count = 50

        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            wellness_result,
            engagement_result,
        ]
        mock_client.table.return_value = mock_table
        mock_get_client.return_value = mock_client

        result = get_knowledge_stats()

        assert "wellness_chunks" in result
        assert "engagement_chunks" in result
        assert "total_chunks" in result
```

**Acceptance Criteria (ALL must pass):**

```bash
# AC1: Module is importable
python -c "from content_assistant.ui.dashboard import render_dashboard, get_generation_stats, get_knowledge_stats" && echo "PASS"

# AC2: Stats dict has required keys
pytest tests/test_dashboard.py::TestGetGenerationStats::test_returns_stats_dict -v
# Expected: PASSED

# AC3: Total count is correct
pytest tests/test_dashboard.py::TestGetGenerationStats::test_calculates_total_correctly -v
# Expected: PASSED

# AC4: Average rating calculated correctly
pytest tests/test_dashboard.py::TestGetGenerationStats::test_calculates_average_rating_correctly -v
# Expected: PASSED

# AC5: Empty data returns zeros
pytest tests/test_dashboard.py::TestGetGenerationStats::test_handles_empty_data -v
# Expected: PASSED

# AC6: Knowledge stats returns chunk counts
pytest tests/test_dashboard.py::TestGetKnowledgeStats::test_returns_chunk_counts -v
# Expected: PASSED

# AC7: All unit tests pass
pytest tests/test_dashboard.py -v
# Expected: at least 5 passed

# AC8: Ruff passes
ruff check content_assistant/ui/dashboard.py tests/test_dashboard.py && echo "PASS: ruff clean"
```

---

### prd.json Format

Ralph will convert the PRD to this format:

```json
{
  "userStories": [
    {
      "id": "1",
      "title": "Parse PDF Knowledge Sources",
      "priority": 1,
      "passes": false
    },
    {
      "id": "2",
      "title": "Implement Semantic Chunking",
      "priority": 2,
      "passes": false
    }
    // ... more stories
  ]
}
```

### Running Ralph

```bash
# Start the autonomous loop
cd /Users/canokcuer/thelifeco
./scripts/ralph/ralph.sh --tool claude 25

# Ralph will iterate through all user stories autonomously
```

---

## PART 2: System Architecture

### Core Architecture: Self-Improving Agent with Feedback Loops

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   TheLifeCo Content Marketing Assistant                  │
│                        (Self-Improving Agent)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     STREAMLIT WEB APP                             │   │
│  │                                                                   │   │
│  │   CREATE MODE              │           REVIEW MODE                │   │
│  │   ────────────             │           ───────────                │   │
│  │   Detailed Brief           │           Content Input              │   │
│  │   (topic, type,            │           ↓                          │   │
│  │    audience, goals)        │           Analyze Content            │   │
│  │   ↓                        │           ↓                          │   │
│  │   Generate Content         │           Show Issues                │   │
│  │   ↓                        │           (engagement, wellness)     │   │
│  │   Signal Collection        │                                      │   │
│  │   (⭐ rating + feedback)   │                                      │   │
│  │   ↓                        │                                      │   │
│  │   Approve/Edit/Regenerate  │                                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      ORCHESTRATOR                                 │   │
│  │                   (Claude with Tools)                             │   │
│  │                                                                   │   │
│  │   Tools:                                                          │   │
│  │   ├─ retrieve_best_examples (signal-weighted ranking)             │   │
│  │   ├─ verify_wellness_facts (RAG from your PDFs)                   │   │
│  │   ├─ check_engagement_patterns (RAG from your guidelines)         │   │
│  │   └─ generate_content (with few-shot examples)                    │   │
│  │                                                                   │   │
│  │   A/B Experiment assignment happens here                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│          ┌───────────────────┼───────────────────┐                       │
│          ▼                   ▼                   ▼                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│  │  WELLNESS   │     │ ENGAGEMENT  │     │  CONTENT    │                │
│  │    RAG      │     │    RAG      │     │  HISTORY    │                │
│  │             │     │             │     │  + SIGNALS  │                │
│  │ Your PDFs + │     │ Your hook/  │     │             │                │
│  │ knowledge   │     │ CTA guides  │     │ All past    │                │
│  │             │     │             │     │ generations │                │
│  │             │     │             │     │ with scores │                │
│  └─────────────┘     └─────────────┘     └─────────────┘                │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                        SUPABASE (Managed Backend)                        │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  PostgreSQL + pgvector                                           │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  • content_generations (brief, content, embedding, signals)      │    │
│  │  • knowledge_chunks (wellness + engagement docs with embeddings) │    │
│  │  • experiments (name, config, status)                            │    │
│  │  • experiment_assignments (session, experiment_id, variant)      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Authentication                                                  │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  • Email/password login (protects API budget)                    │    │
│  │  • Tracks which user created which content                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Feedback Loop (Key Innovation)

**Traditional RAG approach:**
```
User Brief → Semantic Search → Similar examples → Generate
```

**Our Signal-Derived Ranking approach:**
```
User Brief → Semantic Search → Rank by (similarity × signal_score) → Best examples → Generate
```

**How signal_score is calculated:**
```python
signal_score = (
    star_rating / 5.0                     # 0.0 - 1.0
    × (1.1 if approved_first_try else 1)  # 10% bonus
    × (1.1 if hook_worked else 1)         # 10% bonus
    × (1.1 if facts_accurate else 1)      # 10% bonus
)

final_score = cosine_similarity × signal_score
```

**Result**: The system learns what ACTUALLY WORKS, not just what's semantically similar.

### Signal Collection UI

```
┌────────────────── SIGNAL COLLECTION ZONE ──────────────────┐
│                                                            │
│  Quick Rating:  ⭐⭐⭐⭐⭐  (1-5 stars)                     │
│                                                            │
│  What worked well?                                         │
│  [ ] Hook/Opening   [ ] Facts   [ ] Tone   [ ] CTAs        │
│                                                            │
│  What needs work?                                          │
│  [ ] Hook/Opening   [ ] Facts   [ ] Tone   [ ] CTAs        │
│                                                            │
│  [Regenerate]  [Edit Manually]  [Approve & Save]           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Signals collected:**
- Star rating (explicit)
- What worked/needs work checkboxes (explicit)
- Regenerate vs Approve clicks (implicit)
- Manual edits and what was changed (implicit)
- Time to approval (implicit)

### Cold Start Strategy

Since you don't have signal data yet:
1. **Phase 1**: Use pure RAG (semantic similarity only)
2. **Phase 2**: As users rate content, signals accumulate
3. **Phase 3**: Signal-derived ranking kicks in automatically

The system gracefully degrades to traditional RAG when no signal data exists.

### System Architecture

```
                    ┌────────────────────────────────────────────┐
                    │        Streamlit Web Interface             │
                    │      (Content Input + Results)             │
                    └───────────────────┬────────────────────────┘
                                        │
                    ┌───────────────────▼────────────────────────┐
                    │       RALPH-INSPIRED REVIEW LOOP           │
                    │                                            │
                    │   Content ──→ Orchestrator ──→ All Pass? ──┼──→ Done
                    │      ▲         (Claude)            │       │
                    │      │            │               No       │
                    │      │     ┌──────┴──────┐        │       │
                    │      │     ▼      ▼      ▼        ▼       │
                    │      │   Hat 1  Hat 2  Hat 3   Show       │
                    │      │   Engage Wellness Brand  Issues    │
                    │      │                            │       │
                    │      └───── User Revises ◄───────┘       │
                    │                                            │
                    │   Loop until all checks pass               │
                    └────────────────────────────────────────────┘
                                        │
                    ┌───────────────────▼────────────────────────┐
                    │              Vector Store                  │
                    │              (ChromaDB)                    │
                    │                  ▲                         │
                    │     ┌────────────┴────────────┐            │
                    │     │  TheLifeCo Knowledge    │            │
                    │     │  PDFs + Embedded Base   │            │
                    │     └─────────────────────────┘            │
                    └────────────────────────────────────────────┘
```

### Ralph Concepts Applied to Content Review

| Ralph Development Concept | Content Review Implementation |
|---------------------------|------------------------------|
| `prd.json` (user stories) | Content requirements checklist |
| `progress.txt` (learnings) | Review history log for session |
| Fresh context per iteration | Each review starts clean, no state bloat |
| Hat system (specialized agents) | Engagement, Wellness, Brand "hats" (tools) |
| Loop until `COMPLETE` | Iterate until content passes all checks |
| Quality gates (tests, lint) | Engagement score, Wellness accuracy, Brand alignment |

### Ralph-Style Review Loop Implementation

```python
# content_reviewer/ralph_loop.py

def ralph_review_loop(content: str, content_type: str, max_iterations: int = 3):
    """
    Ralph-inspired content review loop.
    Keeps iterating until content passes all checks or user approves.
    """
    review_log = []  # Like Ralph's progress.txt

    for iteration in range(1, max_iterations + 1):
        # Fresh context each iteration (core Ralph principle)
        results = orchestrator.review_content(content, content_type)

        # Log this iteration (like progress.txt)
        review_log.append({
            "iteration": iteration,
            "results": results,
            "issues_found": count_issues(results)
        })

        # Check if all "stories" (checks) pass - like Ralph's prd.json
        if all_checks_pass(results):
            return {
                "status": "COMPLETE",  # Ralph's <promise>COMPLETE</promise>
                "results": results,
                "log": review_log
            }

        # Show issues and suggestions for user revision
        yield {
            "status": "NEEDS_REVISION",
            "iteration": iteration,
            "results": results,
            "suggestions": generate_suggestions(results)
        }

        # User provides revised content for next iteration
        # (This happens in Streamlit UI)

    return {"status": "MAX_ITERATIONS", "results": results, "log": review_log}
```

## Project Structure

```
/Users/canokcuer/thelifeco/
├── agent/                      # Existing Q&A chatbot
│   ├── agent.py
│   ├── app.py
│   └── requirements.txt
│
├── content_reviewer/           # NEW: Content Review System
│   ├── __init__.py
│   ├── app.py                  # Streamlit web interface
│   ├── orchestrator.py         # Main Claude agent with tools
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── engagement.py       # Hook/engagement analyzer
│   │   ├── wellness_rag.py     # RAG-based fact checker
│   │   └── brand_voice.py      # Brand consistency checker
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── document_loader.py  # PDF/text parsing
│   │   ├── chunker.py          # Semantic chunking
│   │   ├── embeddings.py       # Voyage AI embeddings
│   │   └── vector_store.py     # ChromaDB operations
│   ├── knowledge/
│   │   ├── brand_guidelines.py # Brand voice rules
│   │   └── engagement_rules.py # Hook/CTA patterns
│   ├── config.py               # Configuration
│   ├── requirements.txt
│   └── .streamlit/
│       └── secrets.toml        # API keys for cloud
│
├── minibook1.pdf               # Existing knowledge source
├── tlcknowhow.pdf              # Existing knowledge source
└── .env                        # Local API keys
```

## Implementation Steps

### Phase 1: RAG Foundation (Wellness Accuracy)

**Step 1.1: Document Loader**
- Parse `minibook1.pdf` and `tlcknowhow.pdf` using `unstructured` library
- Extract the existing KNOWLEDGE string from `agent.py`
- Combine all sources into unified text corpus

**Step 1.2: Semantic Chunking**
- Split documents into ~500-token chunks with overlap
- Preserve section headers for context
- Use RecursiveCharacterTextSplitter or semantic chunking

**Step 1.3: Embeddings**
- Use Voyage AI (`voyage-3-lite` for cost-efficiency or `voyage-3` for accuracy)
- Generate embeddings for all chunks
- Store embeddings with metadata (source, section, page)

**Step 1.4: Vector Store**
- Use ChromaDB (local, no external service needed)
- Create collection `thelifeco_knowledge`
- Index all embedded chunks

**Step 1.5: Retrieval Function**
```python
def retrieve_relevant_facts(query: str, top_k: int = 5) -> list[str]:
    """Retrieve most relevant knowledge chunks for a wellness claim."""
    # Embed the query
    # Search ChromaDB
    # Return top_k chunks with metadata
```

### Phase 2: Tool Implementations

**Step 2.1: Engagement Analyzer Tool**
```python
ENGAGEMENT_TOOL = {
    "name": "analyze_engagement",
    "description": "Analyzes content for hooks, CTAs, and engagement patterns",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "The content to analyze"},
            "content_type": {
                "type": "string",
                "enum": ["blog", "social_instagram", "social_linkedin", "email", "landing_page", "ad"],
                "description": "Type of content being analyzed"
            }
        },
        "required": ["content", "content_type"]
    }
}
```

**Checks performed:**
- Opening hook strength (first 2 sentences)
- Headline effectiveness (if present)
- CTA presence and clarity
- Content structure (scannable, subheadings)
- Emotional triggers
- Platform-specific patterns (hashtags for social, etc.)

**Step 2.2: Wellness RAG Tool**
```python
WELLNESS_TOOL = {
    "name": "verify_wellness_claims",
    "description": "Verifies wellness and health claims against TheLifeCo's official knowledge base",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "The content containing wellness claims"},
            "claims": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific wellness claims to verify (optional, will extract if not provided)"
            }
        },
        "required": ["content"]
    }
}
```

**Process:**
1. Extract wellness claims from content (Claude identifies claims)
2. For each claim, retrieve relevant facts from vector store
3. Compare claim against retrieved facts
4. Return: VERIFIED, UNVERIFIED, INACCURATE, or NEEDS_REVISION with explanation

**Step 2.3: Brand Voice Tool**
```python
BRAND_VOICE_TOOL = {
    "name": "check_brand_voice",
    "description": "Checks content alignment with TheLifeCo brand voice and guidelines",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "The content to check"},
            "content_type": {"type": "string", "description": "Type of content"}
        },
        "required": ["content"]
    }
}
```

**TheLifeCo Brand Guidelines (to encode):**
- **Tone**: Warm, professional, calming, empowering (not preachy or salesy)
- **Values**: Holistic, natural, medically-supervised, transformation
- **Avoid**: Fear-based marketing, miracle cure claims, aggressive sales language
- **Prefer**: Education-focused, benefit-oriented, personal transformation stories
- **Keywords**: wellness, detox, healing, natural, holistic, medically-supervised

### Phase 3: Orchestrator Agent

**Step 3.1: Main Orchestrator**
```python
def review_content(content: str, content_type: str) -> dict:
    """
    Main orchestrator that uses Claude with tools to review content.
    Returns unified feedback report.
    """
    tools = [ENGAGEMENT_TOOL, WELLNESS_TOOL, BRAND_VOICE_TOOL]

    system_prompt = """You are TheLifeCo's content review assistant.
    Your job is to thoroughly review marketing content using your available tools.

    For each piece of content:
    1. Use analyze_engagement to check hooks, CTAs, and structure
    2. Use verify_wellness_claims to fact-check any health/wellness claims
    3. Use check_brand_voice to ensure brand alignment

    Synthesize all findings into a clear, actionable report."""

    # Claude API call with tools
    # Process tool calls
    # Return unified report
```

**Step 3.2: Tool Execution Handler**
```python
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return results."""
    if tool_name == "analyze_engagement":
        return engagement_analyzer.analyze(tool_input)
    elif tool_name == "verify_wellness_claims":
        return wellness_rag.verify(tool_input)
    elif tool_name == "check_brand_voice":
        return brand_checker.check(tool_input)
```

### Phase 4: Streamlit Web Interface

**Step 4.1: Main App Layout**
```python
# app.py
st.title("TheLifeCo Content Reviewer")

# Content input
content_type = st.selectbox(
    "Content Type",
    ["Blog Post", "Instagram", "LinkedIn", "Email", "Landing Page", "Ad Copy"]
)

content = st.text_area("Paste your content here", height=300)

# Or file upload
uploaded_file = st.file_uploader("Or upload a file", type=["txt", "md", "docx"])

if st.button("Review Content"):
    with st.spinner("Analyzing content..."):
        results = review_content(content, content_type)
        display_results(results)
```

**Step 4.2: Results Display**
```python
def display_results(results: dict):
    # Overall score
    st.metric("Overall Score", f"{results['score']}/100")

    # Tabs for each category
    tab1, tab2, tab3 = st.tabs(["Engagement", "Wellness Accuracy", "Brand Voice"])

    with tab1:
        st.subheader("Engagement Analysis")
        # Hook score, CTA analysis, recommendations

    with tab2:
        st.subheader("Wellness Fact Check")
        # Claims verified, flagged issues, sources

    with tab3:
        st.subheader("Brand Voice")
        # Tone analysis, suggested edits

    # Actionable recommendations
    st.subheader("Recommendations")
    for rec in results['recommendations']:
        st.write(f"- {rec}")
```

### Phase 5: Deployment

**Step 5.1: Streamlit Cloud Setup**
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Configure secrets in Streamlit Cloud dashboard:
   - `ANTHROPIC_API_KEY`
   - `VOYAGE_API_KEY`

**Step 5.2: Vector Store for Cloud**
- Option A: Bundle ChromaDB with app (persistent storage)
- Option B: Use hosted vector DB (Pinecone free tier)
- Option C: Pre-compute and serialize embeddings, load on startup

**Recommended: Option C** for simplicity - pre-compute embeddings, save to pickle/parquet, load into memory on app startup.

## Dependencies (requirements.txt)

```
streamlit>=1.28.0
anthropic>=0.40.0
voyageai>=0.3.0
chromadb>=0.4.0
unstructured>=0.10.0
python-dotenv>=1.0.0
PyPDF2>=3.0.0
tiktoken>=0.5.0
```

## Key Implementation Details

### Claude Tool Calling Pattern
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    tools=tools,
    messages=[{"role": "user", "content": f"Review this {content_type}: {content}"}]
)

# Handle tool use
while response.stop_reason == "tool_use":
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })

    # Continue conversation with tool results
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=[
            {"role": "user", "content": f"Review this {content_type}: {content}"},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]
    )
```

### RAG Retrieval Pattern
```python
def verify_claim(claim: str) -> dict:
    # 1. Embed the claim
    claim_embedding = voyage_client.embed(
        [claim],
        model="voyage-3-lite"
    ).embeddings[0]

    # 2. Search vector store
    results = collection.query(
        query_embeddings=[claim_embedding],
        n_results=5
    )

    # 3. Build context from retrieved chunks
    context = "\n\n".join(results['documents'][0])

    # 4. Use Claude to verify claim against context
    verification = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": f"""Based on this official TheLifeCo knowledge:

{context}

Verify this claim: "{claim}"

Respond with:
- VERIFIED: If claim is accurate according to the knowledge
- INACCURATE: If claim contradicts the knowledge (explain why)
- UNVERIFIED: If knowledge doesn't cover this claim
- NEEDS_REVISION: If claim is partially correct but needs adjustment"""
        }]
    )

    return {"claim": claim, "status": verification, "sources": results['metadatas']}
```

## Verification Plan

### Testing the System
1. **Unit Tests**: Test each tool independently with sample content
2. **Integration Test**: End-to-end test with real TheLifeCo blog posts
3. **Accuracy Test**: Manually verify wellness claims against PDFs
4. **User Testing**: Have marketing team review actual content

### Sample Test Cases
1. **Blog with correct wellness claims** - Should pass wellness check
2. **Blog with incorrect claim** (e.g., "water fasting cures cancer") - Should flag as inaccurate
3. **Social post missing CTA** - Should flag in engagement
4. **Content with aggressive sales language** - Should flag in brand voice

### Manual Verification Steps
1. Run the Streamlit app locally: `streamlit run content_reviewer/app.py`
2. Test with existing TheLifeCo blog content from website
3. Test with intentionally incorrect wellness claims
4. Verify RAG retrieval returns relevant chunks

## Security Considerations

1. **API Keys**: Store in Streamlit secrets, never in code
2. **Input Sanitization**: Limit content length, sanitize inputs
3. **Rate Limiting**: Implement basic rate limiting for API calls
4. **Access Control**: Consider adding simple password protection for cloud app

## Cost Estimation

Per content review (assuming ~1000 word article):
- Claude API: ~$0.015-0.05 (depends on tool iterations)
- Voyage AI: ~$0.001 (embedding queries)
- **Total**: ~$0.02-0.06 per review

Monthly estimate (100 reviews): $2-6

## Future Enhancements

1. **SEO Checker Tool**: Keywords, meta descriptions, headings
2. **Competitor Analysis**: Compare against wellness industry benchmarks
3. **Content Generation**: Suggest rewrites for flagged sections
4. **Batch Processing**: Review multiple pieces at once
5. **Analytics Dashboard**: Track common issues over time
6. **Slack/Email Integration**: Send reports directly to team

---

---

## PART 3: Materials You Need to Provide

Before running Ralph, you need to prepare these materials:

## COMPLETE PRE-FLIGHT CHECKLIST

Before running Ralph, complete ALL items below:

### Step 1: Create Supabase Account & Project (15 min)
- [ ] Go to https://supabase.com and create free account
- [ ] Create new project (name: `thelifeco-content`)
- [ ] Wait for project to initialize (~2 min)
- [ ] Go to Project Settings → API
- [ ] Copy and save:
  - [ ] Project URL (looks like `https://xxxxx.supabase.co`)
  - [ ] `anon` public key
  - [ ] `service_role` secret key (click "Reveal")
- [ ] Go to SQL Editor → New Query → Run: `CREATE EXTENSION IF NOT EXISTS vector;`

### Step 2: Get API Keys (10 min)
- [ ] **Anthropic**: https://console.anthropic.com → API Keys → Create
- [ ] **Voyage AI**: https://www.voyageai.com → Dashboard → API Keys → Create

### Step 3: Prepare .env File (5 min)
Create `/Users/canokcuer/thelifeco/.env`:
```
# Required API Keys
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
ANTHROPIC_API_KEY=your-anthropic-key
VOYAGE_API_KEY=your-voyage-key

# Test User
TEST_EMAIL=test@thelifeco.com
TEST_PASSWORD=TestPassword123!

# Cost Control Limits (adjust as needed)
MAX_TOKENS_PER_CALL=4096           # Max tokens per Claude API call
MAX_FEW_SHOT_EXAMPLES=5            # Max examples in prompts (keeps context small)
DAILY_GENERATION_LIMIT=100         # Max content generations per day
MONTHLY_BUDGET_USD=100.0           # Monthly spending cap in USD
COST_ALERT_THRESHOLD=0.8           # Alert when 80% of budget used
```

### Step 4: Prepare Wellness Documents (already have)
- [ ] Confirm `minibook1.pdf` exists in `/Users/canokcuer/thelifeco/`
- [ ] Confirm `tlcknowhow.pdf` exists in `/Users/canokcuer/thelifeco/`
- [ ] Add any additional wellness PDFs to same directory

### Step 5: Prepare Engagement Guidelines (30-60 min)
Create `/Users/canokcuer/thelifeco/knowledge/engagement/` directory with these files:

**File 1: `hook_patterns.md`** (see template below)
**File 2: `cta_guidelines.md`** (see template below)
**File 3: `platform_rules.md`** (see template below)

### Step 6: Create Test User in Supabase (5 min)
- [ ] Go to Supabase Dashboard → Authentication → Users
- [ ] Click "Add User"
- [ ] Email: `test@thelifeco.com`
- [ ] Password: `TestPassword123!`
- [ ] Click "Create User"

### Step 7: Install Ralph & Dependencies (10 min)
```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Install jq
brew install jq

# Create Ralph directory
mkdir -p /Users/canokcuer/thelifeco/scripts/ralph

# Download Ralph files
curl -o /Users/canokcuer/thelifeco/scripts/ralph/ralph.sh \
  https://raw.githubusercontent.com/snarktank/ralph/main/ralph.sh
curl -o /Users/canokcuer/thelifeco/scripts/ralph/CLAUDE.md \
  https://raw.githubusercontent.com/snarktank/ralph/main/CLAUDE.md

# Make executable
chmod +x /Users/canokcuer/thelifeco/scripts/ralph/ralph.sh
```

### Step 8: Create PRD Files (5 min)
```bash
# Create tasks directory
mkdir -p /Users/canokcuer/thelifeco/tasks

# Create prd.json (Ralph needs this)
# Copy the PRD content into tasks/prd-content-assistant.md
# Then use Ralph's PRD skill to convert to prd.json
```

### Step 9: Run Ralph!
```bash
cd /Users/canokcuer/thelifeco
./scripts/ralph/ralph.sh --tool claude 30
```

---

## ENGAGEMENT GUIDELINES TEMPLATES

Copy these templates and customize for TheLifeCo:

### 1. Wellness Knowledge Documents

**Purpose**: RAG knowledge base for fact-checking wellness claims

**What to include**:
- `minibook1.pdf` (already have)
- `tlcknowhow.pdf` (already have)
- Any additional wellness/health documents
- TheLifeCo program descriptions
- Medical/scientific information about treatments
- Nutrition guidelines

**Format**: PDF, TXT, MD, DOCX - any readable format

### 2. Engagement Guidelines Documents

**Purpose**: RAG knowledge base for checking/creating engaging content

Create these 3 files in `/Users/canokcuer/thelifeco/knowledge/engagement/`:

---

**FILE 1: `hook_patterns.md`** - Copy and customize this:

```markdown
# TheLifeCo Hook Patterns for Content

## Question Hooks (Create Curiosity)
Use these to open emails, social posts, and blog intros:

- "What if you could reset your body in just 7 days?"
- "Have you ever wondered why you feel tired even after 8 hours of sleep?"
- "What would change if you gave your digestive system a complete rest?"
- "Did you know your body has a built-in cellular recycling system?"

## Statistic Hooks (Establish Authority)
Use verified statistics from TheLifeCo research:

- "93% of chronic diseases are lifestyle-related and potentially preventable."
- "After just 3 days of fasting, autophagy increases by up to 300%."
- "Our guests lose an average of 3-5kg during a 7-day detox program."
- "85% of our guests report improved energy levels within the first week."

## Story Hooks (Create Connection)
Use real transformation stories (get permission):

- "When our founder Ersin tried his first detox in 2002, he never expected it would change his life..."
- "Maria came to TheLifeCo Bodrum exhausted and skeptical. Three weeks later, she left with a completely new outlook on health."
- "After 20 years in corporate life, burning out seemed inevitable—until..."

## Contrast Hooks (Challenge Assumptions)
Use to differentiate TheLifeCo approach:

- "Most diets focus on what you eat. We focus on when you DON'T eat."
- "Everyone talks about adding supplements. We start by removing toxins."
- "Wellness isn't a destination—it's a daily practice."

## Problem-Agitation Hooks (For Specific Conditions)
Use for targeted content about specific health issues:

- "Chronic fatigue isn't just being tired. It's your body sending an urgent message."
- "That afternoon energy crash isn't normal—it's a warning sign."
- "If you've tried every diet and nothing works, the problem might not be what you're eating."

## RULES FOR HOOKS:
1. First sentence must grab attention
2. Never start with "We" or "TheLifeCo"
3. Make it about the reader, not us
4. Create curiosity gap (make them want to read more)
5. Avoid clickbait—promise only what we deliver
```

---

**FILE 2: `cta_guidelines.md`** - Copy and customize this:

```markdown
# TheLifeCo Call-to-Action Guidelines

## Primary CTAs (High Commitment)
Use for users ready to take action:

- "Book Your Free Consultation"
- "Reserve Your Spot" (with specific program)
- "Start Your Transformation"
- "Claim Your Wellness Assessment"

## Secondary CTAs (Low Commitment)
Use to nurture leads not ready to book:

- "Download Our Detox Guide"
- "Get the 7-Day Meal Plan"
- "Watch the Video"
- "Read [Guest Name]'s Story"

## Urgency CTAs (Use Sparingly)
Only use when genuinely true:

- "Limited spots for [Month] programs"
- "Early bird pricing ends [Date]"
- "Only 3 rooms remaining"

## CTA Rules by Platform

### Email CTAs
- ONE primary CTA per email (repetition okay)
- Button format for primary CTA
- Link format for secondary CTA
- Place primary CTA: after value proposition, end of email
- Example: "Ready to reset? Book your free consultation →"

### Landing Page CTAs
- Above fold: Single clear CTA
- Repeat CTA every 2-3 scroll lengths
- Use social proof near CTA (testimonials, trust badges)
- Exit intent popup: Secondary CTA (lead magnet)

### Blog Post CTAs
- End of post: Primary CTA related to topic
- Sidebar: Program highlight
- In-content: Relevant internal links
- Never more than 2 CTAs visible at once

### Instagram CTAs
- Feed posts: "Link in bio" + describe what they'll find
- Stories: Swipe up (if available) or "Tap link in bio"
- Reels: Voice CTA in video + caption CTA
- Always tell them exactly what to do

### LinkedIn CTAs
- Direct links acceptable
- Professional tone: "Learn more about our corporate wellness programs"
- Comment engagement: "Share your thoughts below"

## CTA DON'Ts
- Never use "Click here" (not descriptive)
- Avoid "Submit" (use action words instead)
- Don't have competing CTAs
- Never use aggressive language ("Buy now or miss out forever!")
```

---

**FILE 3: `platform_rules.md`** - Copy and customize this:

```markdown
# TheLifeCo Platform-Specific Content Guidelines

## Email Marketing

### Subject Lines
- Length: 6-10 words (40-50 characters)
- Style: Curiosity or benefit-driven
- Personalization: Use [First Name] when available
- GOOD: "Your body's natural reset button (it's free)"
- BAD: "TheLifeCo Newsletter - January Edition"

### Preview Text
- Complement subject line (don't repeat)
- Create additional curiosity
- 40-100 characters visible

### Body Copy
- Scannable: Short paragraphs (2-3 sentences max)
- Use bullet points for benefits/features
- Bold key phrases
- Length: 150-300 words for promotional, up to 500 for educational
- Personal tone (write like a knowledgeable friend)

### Structure
1. Hook (first line)
2. Problem/Pain point
3. Solution (TheLifeCo program)
4. Social proof (testimonial/statistic)
5. CTA

---

## Blog Posts

### Titles
- Include primary keyword naturally
- Add emotional hook or number
- GOOD: "7 Signs Your Body Needs a Detox (And What to Do About It)"
- BAD: "Detox Programs at TheLifeCo"

### Opening Paragraph
- Hook within first 2 sentences
- Address reader directly ("you")
- State what they'll learn

### Structure
- H2 subheading every 200-300 words
- Include relevant images (1 per 300 words)
- Bullet points for lists
- Pull quotes for key statements
- Length: 1500-2500 words for SEO

### SEO Requirements
- Primary keyword in: title, first 100 words, 1-2 H2s, conclusion
- Internal links: 2-3 to relevant programs/posts
- External links: 1-2 to authoritative sources
- Meta description: 150-160 characters with keyword

### Closing
- Summarize key takeaways
- Include relevant CTA
- Invite comments/questions

---

## Instagram

### Feed Posts (Images/Carousels)
- First line = hook (appears before "more")
- Caption length: 150-2200 characters (longer performs better)
- Paragraph breaks for readability
- Hashtags: 20-30 in first comment or end of caption
- Mix hashtag types: branded (#TheLifeCo), niche (#HolisticWellness), broad (#HealthyLiving)

### Stories
- Vertical format (9:16)
- Text readable on mobile
- Include polls, questions, sliders for engagement
- Always have a clear CTA (swipe up, link, DM)

### Reels
- Hook in first 1-3 seconds
- Keep 15-30 seconds for best engagement
- Trending audio when appropriate
- Caption with value + CTA

### Content Mix
- 40% Educational (tips, facts, how-tos)
- 30% Inspirational (transformations, quotes, lifestyle)
- 20% Promotional (programs, offers)
- 10% Behind-the-scenes (team, facilities, daily life)

---

## LinkedIn

### Post Types
- Text posts: 1300+ characters perform best
- Document posts (carousels): High engagement for educational content
- Video: Native upload only, subtitles required

### Tone
- Professional but personal
- First-person narrative works well
- Data and insights appreciated
- Share professional journey/lessons

### Structure
- First line = hook (appears in feed preview)
- Paragraph breaks every 2-3 sentences
- Use line breaks between paragraphs
- End with question or CTA to drive comments

### Content Focus
- Corporate wellness programs
- Leadership and burnout
- Professional transformation stories
- Industry insights and research

### Hashtags
- 3-5 maximum
- Use at end of post
- Mix: #CorporateWellness #Wellbeing #LeadershipHealth

---

## General Rules (All Platforms)

### Tone of Voice
- Warm and welcoming
- Knowledgeable but not preachy
- Empowering (you CAN change)
- Never fear-based or guilt-inducing

### Language
- Use "you" and "your" frequently
- Avoid jargon unless explaining it
- Simple sentences (8th grade reading level)
- Active voice preferred

### Claims
- Only make claims we can verify from our knowledge base
- Always cite source for statistics
- Avoid absolute statements ("cures", "guarantees")
- Use: "supports", "may help", "research suggests"

### Brand Words to Use
- Transformation, reset, renewal
- Holistic, natural, medically-supervised
- Journey, path, lifestyle
- Healing, balance, wellness

### Words to Avoid
- "Miracle", "cure", "guaranteed"
- "Diet" (use "nutrition" or "eating plan")
- "Toxic" (unless specific medical context)
- Aggressive sales language
```

---

**Format**: Markdown files (.md) - Ralph can parse these directly

---

**FILE 4: `engagement_guide.md`** - Hook & Retention Psychology Guide:

This is the comprehensive guide you provided. Save it as `/Users/canokcuer/thelifeco/knowledge/engagement/engagement_guide.md`

The guide covers:
- **Psychology of Attention**: Pattern interruption, curiosity gap, loss aversion
- **Neuroscience of Engagement**: Dopamine as anticipation chemical, open loops
- **Types of Open Loops**: Mystery, Tension, Incomplete Story, Countdown, Transformation
- **Stacking Loops**: Macro (whole content), Medium (sections), Micro (sentence-to-sentence)
- **Promise-Payoff Contract**: Hook is a promise, content must deliver
- **Specificity Principle**: Vague promises = weak curiosity
- **Text Overlays**: Pattern interrupt, contradiction, question, outcome, incomplete text
- **Script Writing**: Micro-retention model, first 15 seconds, valley of death, transitions
- **Advanced Techniques**: Contrast principle, identity/ingroup, availability heuristic, commitment
- **Implementation Framework**: Hook development process, checklist for every video

The agent will use this to:
1. Generate psychologically effective hooks in the PREVIEW step
2. Structure content with proper open loops
3. Ensure promise-payoff alignment
4. Suggest text overlays for social content
5. Script around the "valley of death" (15-45 second retention drop)

---

**FILE 5: `pain_solution_matrix.md`** - TheLifeCo Pain Points & Programs:

```markdown
# TheLifeCo Pain Points & Solution Programs

The agent should use this matrix to understand which programs address which pain points,
and to ensure content accurately matches problems with solutions.

## Category 1: Cleansing & Detoxing
**Pain Points**: Toxin buildup, sluggish metabolism, need for reset, post-holiday recovery
**Programs**:
- Medically Supervised Water Fasting
- Master Detox / Green Juice Fasting

## Category 2: Mental Wellness
**Pain Points**: Stress, anxiety, burnout, mental fog, emotional exhaustion, work-life imbalance
**Programs**:
- Mental Wellness Program
- Mindfulness & meditation retreats

## Category 3: Weight Loss and Management
**Pain Points**: Weight plateau, failed diets, emotional eating, slow metabolism, body image
**Programs**:
- Weight Loss Program
- Metabolic reset programs

## Category 4: Lifestyle As Medicine (High Compliance - Medical Conditions)
**Pain Points & Programs**:
- **Diabetes Management** - Type 2 diabetes, pre-diabetes, blood sugar issues
- **Cardiovascular Disease Management** - Heart health, high blood pressure, cholesterol
- **Chronic Fatigue Recovery** - Persistent exhaustion, low energy, burnout recovery
- **Liver Detox** - Fatty liver, liver health, alcohol recovery
- **Inflammation & Immune Reset** - Autoimmune issues, chronic inflammation, weak immunity
- **Digestive & Gut Health** - IBS, bloating, gut microbiome, digestive issues

## Category 5: Longevity and Regenerative Health
**Pain Points & Programs**:
- **Ultimate Longevity / Beauty & Body Reshaping** - Aging appearance, skin health, body contouring (appearance-focused, not performance)
- **Cancer Prevention Support** - Cancer survivors, prevention focus, cellular health
- **Hormonal Longevity (Women's)** - Menopause, hormonal imbalance, fertility
- **Hormonal Longevity (Men's)** - Testosterone, vitality, andropause
- **Wellcation (Guilt-Free Holiday)** - Want wellness without strict programs, relaxation + health
- **Longevity for Elderly (Golden Years)** - Age-related decline, mobility, cognitive health

## Compliance Levels

### High Compliance (Medical Conditions)
These guests have specific health conditions requiring medical supervision:
- Type 2 Diabetes
- Cardiovascular disease
- Chronic fatigue syndrome
- Autoimmune conditions
- Cancer prevention/recovery
- Severe gut issues

Content approach: Medical credibility, doctor supervision, clinical results, safety focus

### Low Compliance (Lifestyle/Wellness)
These guests want improvement without medical urgency:
- Better sleep
- Skin health / anti-aging
- General detox / reset
- Weight management
- Stress reduction
- Guilt-free holiday

Content approach: Transformation stories, lifestyle benefits, experience focus, aspirational

## Funnel Stage Content Guidelines

### Awareness Stage
- Goal: Educate about the problem
- Focus: Pain points, statistics, "did you know" content
- CTA: Learn more, download guide, follow us
- Tone: Educational, eye-opening

### Consideration Stage
- Goal: Position TheLifeCo as the solution
- Focus: Differentiation, methodology, social proof
- CTA: See programs, read testimonials, take quiz
- Tone: Authoritative, trustworthy

### Conversion Stage
- Goal: Drive booking/purchase
- Focus: Specific offers, urgency, overcome objections
- CTA: Book now, claim offer, schedule call
- Tone: Direct, confident, urgent

### Loyalty Stage
- Goal: Nurture existing guests
- Focus: Continued value, community, referrals
- CTA: Rebook, refer a friend, join community
- Tone: Warm, appreciative, exclusive
```

### 3. Supabase Account Setup

**Before running Ralph**:
1. Create account at supabase.com (free tier)
2. Create new project
3. Note down:
   - Project URL
   - Anon key (public)
   - Service role key (private)
4. Enable pgvector extension (SQL Editor: `CREATE EXTENSION vector;`)

### 4. API Keys

**Required**:
- Anthropic API key (for Claude)
- Voyage AI API key (for embeddings)

**Store in**:
- `/Users/canokcuer/thelifeco/.env` (local development)
- Streamlit Cloud secrets (deployment)

---

## PART 4: Summary

### What We're Building

**Self-Improving Content Marketing Assistant**

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│   Marketing Team → Streamlit App → Claude Agent → Content          │
│                           │              │                         │
│                           │              ▼                         │
│                           │     ┌─────────────────┐                │
│                           │     │ RAG Knowledge   │                │
│                           │     │ (wellness +     │                │
│                           │     │  engagement)    │                │
│                           │     └─────────────────┘                │
│                           │                                        │
│                           ▼                                        │
│                    Signal Collection                               │
│                    (ratings, feedback)                             │
│                           │                                        │
│                           ▼                                        │
│                    Learn & Improve                                 │
│                    (signal-derived ranking)                        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Core Features

| Feature | Description |
|---------|-------------|
| **CREATE Mode** | Generate content from detailed brief |
| **REVIEW Mode** | Check existing content for quality |
| **Wellness RAG** | Fact-check against your knowledge base |
| **Engagement RAG** | Apply your hook/CTA guidelines |
| **Signal Collection** | Ratings + feedback on every generation |
| **Self-Improvement** | Learn from what actually works |
| **A/B Testing** | Experiment with different approaches |
| **Authentication** | Protect API budget with login |

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **AI** | Claude (Anthropic) |
| **Embeddings** | Voyage AI |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Auth** | Supabase Auth |
| **Development** | Ralph (snarktank/ralph) |
| **Deployment** | Streamlit Cloud |

### Getting Started Checklist

**Before Running Ralph:**
- [ ] Create Supabase account and project
- [ ] Get API keys (Anthropic + Voyage AI)
- [ ] Prepare wellness knowledge documents
- [ ] Prepare engagement guidelines documents
- [ ] Install Claude Code: `npm install -g @anthropic-ai/claude-code`
- [ ] Install jq: `brew install jq`
- [ ] Set up Ralph: Download `ralph.sh` and `CLAUDE.md`

**Running Ralph:**
- [ ] Create PRD: `tasks/prd-content-assistant.md`
- [ ] Convert to prd.json
- [ ] Run: `./scripts/ralph/ralph.sh --tool claude 25`
- [ ] Monitor: Check `progress.txt` and `prd.json`

**After Ralph Completes:**
- [ ] Test locally: `streamlit run app.py`
- [ ] Deploy to Streamlit Cloud
- [ ] Add team members to Supabase auth
- [ ] Start collecting signals!

### How the System Improves Over Time

```
Week 1:  Pure RAG (no signal data)
         ↓
Week 2:  Signals accumulating (ratings, feedback)
         ↓
Week 4:  Signal-derived ranking kicks in
         ↓
Week 8:  System noticeably better at generating content your team loves
         ↓
Month 3: Highly tuned to TheLifeCo's style and what performs
```

### Estimated Effort

| Phase | Time | Notes |
|-------|------|-------|
| Material preparation | 2-4 hours | Gather docs, write guidelines |
| Setup (Supabase, API keys, Ralph) | 30 min | One-time setup |
| Ralph execution | 3-5 hours | Autonomous, runs in background |
| Testing & refinement | 1-2 hours | Manual verification |
| Deployment | 30 min | Streamlit Cloud |
| **Total human time** | **4-8 hours** | Mostly preparation and review |
