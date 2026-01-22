# TheLifeCo Self-Improving Content Marketing Assistant

A self-improving AI content assistant for TheLifeCo's marketing team that creates and reviews content, learns from user feedback, and improves over time.

## Overview

| Aspect | Decision |
|--------|----------|
| Business Goal | Maximize content performance (engagement, conversions) |
| Core Thesis | Maximize content quality |
| Modes | CREATE + REVIEW |
| Content Types | Email, landing pages, social media, blog posts |
| Interface | Streamlit web app |
| AI | Claude (Anthropic) |
| Storage | Supabase (PostgreSQL + pgvector + auth) |
| Embeddings | Voyage AI |
| Learning | Signal-derived ranking of few-shot examples |

## Key Features

- **CREATE Mode**: Generate content from detailed briefs (13-question Socratic questionnaire)
- **REVIEW Mode**: Analyze existing content for wellness accuracy and engagement
- **Self-Improving**: Learns from user feedback (star ratings, checkboxes) to improve over time
- **A/B Testing**: Built-in experiment framework for testing variations
- **Strict Fact Policy**: Only uses verified TheLifeCo information

## Documentation

See [PLAN.md](./PLAN.md) for the complete architecture, PRD with 27 user stories, and implementation details.

## Knowledge Base Files

- `minibook1.pdf` / `minibook1.txt` - TheLifeCo wellness mini-book
- `tlcknowhow.pdf` - TheLifeCo know-how guide

## Development

This project uses [Ralph](https://github.com/snarktank/ralph) for autonomous development with Claude Code.

```bash
# Install dependencies (after setup)
pip install -r requirements.txt

# Run the app (after implementation)
streamlit run content_assistant/app.py
```

## License

Proprietary - TheLifeCo
