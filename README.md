# TheLifeCo Self-Improving Content Marketing Assistant

A self-improving AI content assistant for TheLifeCo's marketing team that creates and reviews content, learns from user feedback, and improves over time.

## Overview

| Aspect | Decision |
|--------|----------|
| Business Goal | Maximize content performance (engagement, conversions) |
| Core Thesis | Maximize content quality |
| Modes | CREATE + REVIEW + MONITOR |
| Content Types | Email, landing pages, social media, blog posts |
| Interface | Streamlit web app |
| AI | Claude Opus 4.5 (Anthropic) |
| Storage | Supabase (PostgreSQL + pgvector + auth) |
| Embeddings | Voyage AI (voyage-3, 1024 dimensions) |
| Learning | Signal-derived ranking of few-shot examples |

## Agent Architecture (EPA-GONCA-CAN)

The system uses a sophisticated multi-agent architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                   (Streamlit create_mode)                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    EPA (Main Orchestrator)                   │
│                                                             │
│  • Interacts directly with users via Socratic questioning   │
│  • Collects ALL 13 required brief fields before generation  │
│  • Coordinates sub-agents (GONCA, CAN, Review)              │
│  • Reviews ALL output before presenting to user             │
│  • Uses Claude Opus 4.5 for maximum quality                 │
└────────┬──────────────────────┬──────────────────┬─────────┘
         │                      │                  │
         ▼                      ▼                  ▼
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│     GONCA      │   │      CAN       │   │     Review     │
│(Wellness Expert)│   │ (Storytelling) │   │   (Feedback)   │
│                │   │                │   │                │
│ • Program info │   │ • Hooks        │   │ • Analyzes     │
│ • Center details│  │ • Content body │   │   feedback     │
│ • Verified facts│  │ • CTAs         │   │ • Routes to    │
│ • Compliance   │   │ • Hashtags     │   │   right agent  │
└────────────────┘   └────────────────┘   └────────────────┘
```

### The 13 Required Brief Fields

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

## Key Features

- **CREATE Mode**: Generate content through EPA's Socratic conversation
- **REVIEW Mode**: Analyze existing content for wellness accuracy and engagement
- **MONITOR Mode**: Track system usage and costs
- **Self-Improving**: Learns from user feedback (star ratings, checkboxes) to improve over time
- **A/B Testing**: Built-in experiment framework for testing variations
- **Strict Fact Policy**: Only uses verified TheLifeCo information from GONCA
- **Full Context**: CAN receives complete brief + wellness facts for best content

## Quick Start

### Prerequisites
- Python 3.11+
- Supabase account with pgvector extension
- Anthropic API key (Claude Opus 4.5)
- Voyage AI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/thelifeco/content-assistant.git
cd content-assistant

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and fill in your keys
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your credentials:

```env
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_service_key
ANTHROPIC_API_KEY=your_anthropic_key
VOYAGE_API_KEY=your_voyage_key

# Model Configuration (Opus 4.5 recommended)
CLAUDE_MODEL=claude-opus-4-5-20251101
VOYAGE_MODEL=voyage-3
EMBEDDING_DIMENSION=1024
```

### Load Knowledge Base

```bash
# Load all knowledge files into vector database
python scripts/load_knowledge_with_delay.py
```

### Run the Application

```bash
streamlit run content_assistant/app.py
```

## Project Structure

```
content_assistant/
├── agents/
│   ├── epa_agent.py       # Main orchestrator (EPA)
│   ├── gonca_agent.py     # Wellness sub-agent (GONCA)
│   ├── can_agent.py       # Storytelling sub-agent (CAN)
│   ├── review_subagent.py # Feedback analyzer
│   ├── types.py           # Shared type definitions
│   └── base_agent.py      # Base agent class
├── ui/
│   ├── epa_create_mode.py # EPA-based create mode UI
│   ├── review_mode.py     # Review mode UI
│   └── auth.py            # Authentication
├── rag/
│   ├── knowledge_base.py  # Knowledge base operations
│   ├── vector_store.py    # Vector storage (pgvector)
│   └── embeddings.py      # Voyage AI embeddings
├── services/
│   └── api_client.py      # API client for backend
└── app.py                 # Main Streamlit app
```

## Testing

```bash
# Run architecture tests
python scripts/test_epa_architecture.py

# Run full flow test (requires API keys)
python scripts/test_epa_architecture.py --test full
```

## Knowledge Structure

Agent-specific knowledge folders live under `knowledge/`:

```
knowledge/
├── orchestrator/
├── wellness/
│   └── centers/
├── storytelling/
└── brand/
```

## Documentation

- [EPA Architecture](./docs/EPA_ARCHITECTURE.md) - Detailed architecture documentation
- [PLAN.md](./PLAN.md) - Original PRD and implementation plan
- [ARCHITECTURE_CHANGES.md](./ARCHITECTURE_CHANGES.md) - Architecture changes and migration guide
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Implementation details

## License

Proprietary - TheLifeCo
