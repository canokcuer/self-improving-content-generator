# TheLifeCo Content Assistant - Agent Instructions

This document contains project-specific instructions for AI agents working on this codebase.

## Project Overview

Building a self-improving AI content assistant for TheLifeCo's marketing team that:
1. Creates content (emails, landing pages, social posts, blogs, ads)
2. Reviews existing content for wellness accuracy and engagement
3. Learns over time through signal-derived feedback loops

## Critical Reference

**ALWAYS read the relevant section of PLAN.md before implementing any story.**

PLAN.md contains:
- Complete code examples for each story
- Exact file paths and structures
- Acceptance criteria with verification commands
- Test code to implement

## Development Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Run quality checks
ruff check content_assistant/ tests/
pytest tests/ -v -k 'not integration'

# Run Streamlit app
streamlit run content_assistant/app.py --server.headless true
```

## Project Structure

```
content_assistant/
├── __init__.py          # Package init with version
├── app.py               # Main Streamlit entry point
├── config.py            # Configuration management
├── db/                  # Database layer
│   ├── __init__.py
│   ├── supabase_client.py
│   ├── schema.sql
│   └── init_db.py
├── rag/                 # RAG pipeline
│   ├── __init__.py
│   ├── loader.py        # Document loading
│   ├── chunker.py       # Text chunking
│   ├── embeddings.py    # Voyage AI embeddings
│   └── vector_store.py  # pgvector operations
├── tools/               # Claude tools
│   ├── __init__.py
│   ├── claude_client.py # Anthropic client
│   ├── generator.py     # Content generation
│   ├── reviewer.py      # Content review
│   └── signals.py       # Signal collection
├── experiments/         # A/B framework
│   └── __init__.py
└── ui/                  # Streamlit components
    ├── __init__.py
    ├── auth.py
    ├── create_mode.py
    ├── review_mode.py
    └── history.py

tests/
├── __init__.py
├── conftest.py
├── test_config.py
├── test_supabase_client.py
├── test_schema.py
├── test_loader.py
├── test_chunker.py
└── ...
```

## Key Patterns

### 1. Configuration
Always use `get_config()` to access configuration:
```python
from content_assistant.config import get_config
config = get_config()
```

### 2. Database Access
Use appropriate client based on operation:
```python
from content_assistant.db.supabase_client import get_client, get_admin_client

# Regular operations (respects RLS)
client = get_client()

# Admin operations (bypasses RLS)
admin_client = get_admin_client()
```

### 3. Error Handling
Create specific exception classes for each module:
```python
class LoaderError(Exception):
    """Raised when document loading fails."""
    pass
```

### 4. Testing
- Unit tests mock external services (Supabase, Voyage, Anthropic)
- Integration tests are marked with `@pytest.mark.integration`
- Use fixtures from conftest.py for common test data

### 5. Embeddings
All embeddings are 1024-dimensional (Voyage AI):
```python
embedding vector(1024)  -- in SQL
```

## Quality Gates

Before committing, ensure:
1. `ruff check .` passes with no errors
2. `pytest tests/ -v -k 'not integration'` passes
3. If UI changes, verify the app starts: `timeout 3 streamlit run content_assistant/app.py --server.headless true`

## Commit Message Format

```
feat: [story-N] - Story Title

- What was implemented
- Files changed
```

## Knowledge Base Files

The project includes TheLifeCo knowledge documents:
- `minibook1.pdf` / `minibook1.txt` - Wellness mini-book
- `tlcknowhow.pdf` - Operational know-how

These are used for RAG-based fact checking and content verification.

## The 13 Socratic Questions

Every content brief must include:
1. Target Audience
2. Pain Area (CRUCIAL)
3. Compliance Level (High/Low)
4. Funnel Stage (Awareness/Consideration/Conversion/Loyalty)
5. Value Proposition
6. Desired Action
7. Specific Programs
8. Specific Centers
9. Tone
10. Key Messages
11. Constraints
12. Platform
13. Price Point

## Signal Collection

Signals for learning:
- Star rating (1-5)
- "What worked" checkboxes
- "What needs work" checkboxes
- Implicit: Approve vs Regenerate
- Implicit: Manual edits
