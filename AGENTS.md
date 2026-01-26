# TheLifeCo Content Assistant - Agent Instructions

This document contains project-specific instructions for AI agents working on this codebase.

## Project Overview

Building a self-improving AI content assistant for TheLifeCo's marketing team that:
1. Creates content (emails, landing pages, social posts, blogs, ads)
2. Reviews existing content for wellness accuracy and engagement
3. Learns over time through signal-derived feedback loops

## Agent Architecture (EPA-GONCA-ALP)

The system uses a multi-agent architecture with Claude Opus 4.5:

### EPA (Main Orchestrator)
- **Role**: Interacts directly with users, coordinates sub-agents
- **File**: `content_assistant/agents/epa_agent.py`
- **Responsibilities**:
  - Socratic questioning to collect 13 required brief fields
  - Invoking GONCA for wellness facts
  - Invoking ALP for content creation
  - Reviewing all output before presenting to user
  - Routing feedback to appropriate sub-agent

### GONCA (Wellness Expert Sub-Agent)
- **Role**: Provides verified TheLifeCo information
- **File**: `content_assistant/agents/gonca_agent.py`
- **Responsibilities**:
  - Program details and benefits
  - Center information (Antalya, Bodrum, Phuket, Sharm)
  - Compliance guidance for health claims
  - Verified facts from knowledge base

### ALP (Storytelling Sub-Agent)
- **Role**: Creates engaging content with full context
- **File**: `content_assistant/agents/alp_agent.py`
- **Receives**:
  - Complete brief (all 13 fields)
  - Wellness facts from GONCA
  - User voice preferences
  - Style guidance
  - Conversation context
- **Creates**: Hooks, content body, CTAs, hashtags

### Review Sub-Agent
- **Role**: Analyzes user feedback
- **File**: `content_assistant/agents/review_subagent.py`
- **Determines**: Whether to route to GONCA (wellness issues) or ALP (storytelling issues)

## Critical Reference

**ALWAYS read the relevant section of PLAN.md before implementing any story.**

For the new EPA architecture, also read:
- `docs/EPA_ARCHITECTURE.md` - Detailed architecture documentation

## Development Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Run quality checks
ruff check content_assistant/ tests/
pytest tests/ -v -k 'not integration'

# Run architecture tests
python scripts/test_epa_architecture.py

# Run Streamlit app
streamlit run content_assistant/app.py --server.headless true
```

## Project Structure

```
content_assistant/
├── __init__.py          # Package init with version
├── app.py               # Main Streamlit entry point
├── config.py            # Configuration management
├── agents/              # Agent system (EPA-GONCA-ALP)
│   ├── __init__.py
│   ├── types.py         # Shared types (ContentBrief, EPAState, etc.)
│   ├── base_agent.py    # Base agent class
│   ├── subagent_base.py # Base for sub-agents
│   ├── epa_agent.py     # EPA main orchestrator
│   ├── gonca_agent.py   # GONCA wellness sub-agent
│   ├── alp_agent.py     # ALP storytelling sub-agent
│   ├── review_subagent.py # Feedback analyzer
│   ├── orchestrator.py  # (Legacy) Old orchestrator
│   ├── coordinator.py   # (Legacy) Old coordinator
│   └── ...
├── db/                  # Database layer
│   ├── supabase_client.py
│   ├── schema.sql
│   └── init_db.py
├── rag/                 # RAG pipeline
│   ├── loader.py        # Document loading
│   ├── chunker.py       # Text chunking
│   ├── embeddings.py    # Voyage AI embeddings
│   ├── vector_store.py  # pgvector operations
│   └── knowledge_base.py # Knowledge base operations
├── ui/                  # Streamlit components
│   ├── auth.py
│   ├── epa_create_mode.py  # EPA-based create mode (active)
│   ├── create_mode.py      # (Legacy) Old create mode
│   └── review_mode.py
└── services/
    └── api_client.py    # API client

tests/
├── conftest.py
├── test_config.py
└── ...

scripts/
├── test_epa_architecture.py  # Architecture tests
└── load_knowledge_with_delay.py  # Knowledge loader
```

## Key Patterns

### 1. Configuration
Always use `get_config()` to access configuration:
```python
from content_assistant.config import get_config
config = get_config()
```

Model is configured via `.env`:
```env
CLAUDE_MODEL=claude-opus-4-5-20251101
```

### 2. Agent Creation
EPA is the main agent, sub-agents are invoked as tools:
```python
from content_assistant.agents import EPAAgent

epa = EPAAgent()  # Uses Opus 4.5 from config
response = epa.process_message_sync("I want to create content...")
```

### 3. Sub-Agent Invocation
EPA calls sub-agents via tools:
```python
# In EPA's tool handlers:
gonca = self._get_gonca_agent()
response = gonca.process_request(wellness_request)
```

### 4. Database Access
Use appropriate client based on operation:
```python
from content_assistant.db.supabase_client import get_client, get_admin_client

# Regular operations (respects RLS)
client = get_client()

# Admin operations (bypasses RLS)
admin_client = get_admin_client()
```

### 5. Error Handling
Create specific exception classes for each module:
```python
class LoaderError(Exception):
    """Raised when document loading fails."""
    pass
```

### 6. Testing
- Unit tests mock external services (Supabase, Voyage, Anthropic)
- Integration tests are marked with `@pytest.mark.integration`
- Use `scripts/test_epa_architecture.py` for architecture tests

### 7. Embeddings
All embeddings are 1024-dimensional (Voyage AI voyage-3):
```python
embedding vector(1024)  -- in SQL
```

## Quality Gates

Before committing, ensure:
1. `ruff check .` passes with no errors
2. `pytest tests/ -v -k 'not integration'` passes
3. `python scripts/test_epa_architecture.py` passes
4. If UI changes, verify the app starts: `streamlit run content_assistant/app.py --server.headless true`

## Commit Message Format

```
feat: [story-N] - Story Title

- What was implemented
- Files changed
```

## Knowledge Base

The knowledge base is stored in Supabase with pgvector:
- 662 chunks across 16 sources
- Sources include program info, center details, storytelling guides
- GONCA has full access (no source filtering)

To reload knowledge base:
```bash
python scripts/load_knowledge_with_delay.py
```

## The 13 Required Brief Fields

EPA must collect ALL of these before generating content:

1. **Target Audience** - Who is this content for?
2. **Pain Area** (CRUCIAL) - What problem are we addressing?
3. **Compliance Level** - High (medical) or Low (general wellness)
4. **Funnel Stage** - awareness/consideration/conversion/loyalty
5. **Value Proposition** - What unique value are we offering?
6. **Desired Action** - What should readers do?
7. **Specific Programs** - Which TheLifeCo programs to feature
8. **Specific Centers** - Which centers (Antalya, Bodrum, Phuket, Sharm)
9. **Tone** - Voice and style (professional, casual, inspirational)
10. **Key Messages** - Core points to communicate
11. **Constraints** - Things to avoid
12. **Platform** - Where will this be published
13. **Price Points** - Pricing information to include

For **Conversion** funnel stage, also collect:
- Campaign price
- Campaign duration
- Campaign center
- Campaign deadline

## Signal Collection

Signals for learning:
- Star rating (1-5)
- "What worked" checkboxes
- "What needs work" checkboxes
- Implicit: Approve vs Regenerate
- Implicit: Manual edits

## Model Configuration

All agents use Claude Opus 4.5:
- **EPA**: Full orchestrator capabilities
- **GONCA**: Lower temperature (0.3) for factual accuracy
- **ALP**: Higher temperature (0.8) for creativity
- **Review**: Lower temperature (0.3) for analytical work
