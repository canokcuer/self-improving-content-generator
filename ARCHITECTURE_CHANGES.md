# TheLifeCo Content Assistant - Architecture Changes Summary

**Last Updated:** January 26, 2026
**Purpose:** Document major architecture changes for session continuity

---

## Current Architecture: EPA-GONCA-CAN

The system now uses a **true orchestrator pattern** where EPA is the main agent that coordinates sub-agents as tools.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                   (Streamlit epa_create_mode.py)             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    EPA (Main Orchestrator)                   │
│                     Claude Opus 4.5                          │
│                                                             │
│  • Interacts directly with users via Socratic questioning   │
│  • Collects ALL 13 required brief fields before generation  │
│  • Invokes sub-agents as TOOLS (not separate stages)        │
│  • Reviews ALL output before presenting to user             │
│  • Routes feedback to appropriate sub-agent                 │
└────────┬──────────────────────┬──────────────────┬─────────┘
         │                      │                  │
    [consult_gonca]        [consult_can]    [analyze_feedback]
         │                      │                  │
         ▼                      ▼                  ▼
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│     GONCA      │   │      CAN       │   │     Review     │
│   Opus 4.5     │   │   Opus 4.5     │   │   Opus 4.5     │
│  temp=0.3      │   │  temp=0.8      │   │  temp=0.3      │
│                │   │                │   │                │
│ • Program info │   │ • Full context │   │ • Categorizes  │
│ • Center info  │   │ • Hooks        │   │   feedback     │
│ • Verified facts│  │ • Content body │   │ • Routes to    │
│ • Compliance   │   │ • CTAs         │   │   right agent  │
└────────────────┘   └────────────────┘   └────────────────┘
```

---

## What Changed and Why

### 1. From 13-Question Form → Conversational Briefing

**Before:**
- Rigid 13-question form (transformation goal, audience, pain point, etc.)
- Users had to answer all questions sequentially
- No flexibility or clarification

**After:**
- Natural conversation with Orchestrator Agent
- Agent asks clarifying questions until 100% aligned
- All 13 Socratic questions are enforced before progressing
- Proactive suggestions based on context
- Campaign/pricing collected dynamically when needed (not stored in KB)

**Why:**
- Better user experience
- More accurate briefs through clarification
- Flexibility for different content needs
- Agent can suggest approaches user didn't consider

---

### 2. From Single Generator → Multi-Agent Pipeline

**Before:**
- Single Claude call for content generation
- Limited fact-checking
- No structured feedback loop

**After:**
- **Orchestrator Agent (EPA):** Conversational briefing, funnel detection
- **Wellness Agent (GONCA):** Fact verification against knowledge base
- **Storytelling Agent (CAN):** Content creation with engagement optimization
- **Review Agent:** Feedback collection, learning extraction

---

### 3. From One-Shot → Persistent Conversations

**Before:**
- Single request-response interactions
- No memory of previous sessions

**After:**
- Conversations persist in database with full agent state
- Users can continue where they left off
- Full message history preserved
- Edit content through ongoing dialogue

**Why:**
- Content often needs multiple iterations
- Users return to refine over days/weeks
- Better context for follow-up requests

---

## Key Changes from Previous Architecture

### Before: State Machine Pipeline (AgentCoordinator)

```
User → Orchestrator → Wellness → Storytelling (Preview) → Storytelling (Content) → Review
         (stage 1)    (stage 2)      (stage 3)               (stage 4)          (stage 5)
```

**Problems:**
- Each agent was an independent stage
- Limited context passing between stages
- No central review before user sees content
- Source filtering blocked knowledge access

### After: True Orchestrator Pattern (EPA)

```
User ←→ EPA
        │
        ├── [consult_gonca] → GONCA (returns wellness facts)
        │
        ├── [consult_can] → CAN (returns content with FULL context)
        │
        └── [analyze_feedback] → Review (routes feedback)
```

**Benefits:**
- EPA maintains full conversation context
- Sub-agents are tools, not stages
- CAN receives COMPLETE brief + wellness facts
- EPA reviews everything before user sees it
- No source filtering - full knowledge access

---

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
- Campaign price, duration, center, deadline

---

## New Files Created

### Agent Types (`content_assistant/agents/types.py`)
- `ContentBrief` - All 13 required fields + validation
- `EPAState`, `EPAStage` - State management
- `WellnessRequest`, `WellnessResponse` - GONCA communication
- `StorytellingRequest`, `StorytellingResponse` - CAN communication
- `FeedbackRequest`, `FeedbackAnalysis` - Review communication

### New Agents
| File | Purpose |
|------|---------|
| `epa_agent.py` | Main orchestrator - Socratic questioning, sub-agent coordination |
| `gonca_agent.py` | Wellness sub-agent - TheLifeCo knowledge, fact verification |
| `can_agent.py` | Storytelling sub-agent - Content creation with FULL context |
| `review_subagent.py` | Feedback analyzer - Routes to GONCA or CAN |
| `subagent_base.py` | Base class for sub-agents |

### Updated Files
| File | Change |
|------|--------|
| `content_assistant/agents/__init__.py` | Exports new agents and types |
| `content_assistant/ui/__init__.py` | Defaults to EPA create mode |
| `content_assistant/ui/epa_create_mode.py` | New UI for EPA |
| `content_assistant/app.py` | Uses EPA create mode |
| `.env` | `CLAUDE_MODEL=claude-opus-4-5-20251101` |

### Documentation
| File | Purpose |
|------|---------|
| `docs/EPA_ARCHITECTURE.md` | Detailed architecture documentation |
| `scripts/test_epa_architecture.py` | Architecture test script |

---

## Model Configuration

All agents use **Claude Opus 4.5** (`claude-opus-4-5-20251101`):

| Agent | Temperature | Purpose |
|-------|-------------|---------|
| EPA | 0.7 | Balanced for conversation |
| GONCA | 0.3 | Lower for factual accuracy |
| CAN | 0.8 | Higher for creativity |
| Review | 0.3 | Lower for analytical work |

---

## Data Flow

### Content Generation Flow

1. **User → EPA**: "I want to create Instagram content about weight loss"

2. **EPA Briefing** (Socratic questioning until 13 fields collected):
   - Target audience?
   - Pain area (CRUCIAL)?
   - ...all 13 fields...

3. **EPA → GONCA** (via `consult_gonca` tool):
   - Request: WellnessRequest with query + brief context
   - Response: WellnessResponse with verified facts, program details, compliance guidance

4. **EPA → CAN** (via `consult_can` tool):
   - Request: StorytellingRequest with FULL CONTEXT:
     - Complete brief (all 13 fields)
     - Wellness facts from GONCA
     - User voice preferences
     - Style guidance
     - Conversation context
   - Response: StorytellingResponse with hook, content, CTA, hashtags

5. **EPA Review**: EPA reviews CAN's content, makes adjustments if needed

6. **EPA → User**: Final content presented

### Feedback Flow

1. **User → EPA**: Feedback on generated content
2. **EPA → Review** (via `analyze_feedback` tool): Analyze feedback
3. **Review returns**: FeedbackAnalysis with feedback_type and suggested_action
4. **EPA routes**:
   - "wellness" → Consult GONCA again
   - "storytelling" → Consult CAN again with feedback
   - "both" → GONCA then CAN
   - "approved" → Finalize

---

## Legacy Files (Deprecated)

The following files are kept for backward compatibility but are not used:

| File | Status |
|------|--------|
| `orchestrator.py` | Deprecated - replaced by `epa_agent.py` |
| `wellness_agent.py` | Deprecated - replaced by `gonca_agent.py` |
| `storytelling_agent.py` | Deprecated - replaced by `can_agent.py` |
| `review_agent.py` | Deprecated - replaced by `review_subagent.py` |
| `coordinator.py` | Deprecated - EPA handles coordination |
| `create_mode.py` | Deprecated - replaced by `epa_create_mode.py` |

---

## Testing

### Run Architecture Tests

```bash
# All tests
python scripts/test_epa_architecture.py

# Specific tests
python scripts/test_epa_architecture.py --test types
python scripts/test_epa_architecture.py --test brief
python scripts/test_epa_architecture.py --test epa
python scripts/test_epa_architecture.py --test gonca
python scripts/test_epa_architecture.py --test can
python scripts/test_epa_architecture.py --test full  # Requires API keys
```

### Verify Models

```python
from content_assistant.agents import EPAAgent, GONCAAgent, CANAgent
from content_assistant.agents.review_subagent import ReviewSubAgent

epa = EPAAgent()
gonca = GONCAAgent()
can = CANAgent()
review = ReviewSubAgent()

# All should be claude-opus-4-5-20251101
print(f"EPA: {epa.model}")
print(f"GONCA: {gonca.model}")
print(f"CAN: {can.model}")
print(f"Review: {review.model}")
```

---

## To Continue Development

1. Read this file and `docs/EPA_ARCHITECTURE.md` for context
2. All agents use Opus 4.5 - confirmed in `.env`
3. Key files to understand:
   - `content_assistant/agents/epa_agent.py` - Main orchestrator
   - `content_assistant/agents/types.py` - Type definitions
   - `content_assistant/ui/epa_create_mode.py` - UI
4. Run `python scripts/test_epa_architecture.py` to verify everything works

---

## Known Issues and Mitigations

### Issue: Streamlit Warning
**Warning:** "missing ScriptRunContext" when running outside Streamlit
**Status:** Safe to ignore - appears when importing Streamlit modules in non-Streamlit context

### Issue: API Costs
**Risk:** Opus 4.5 is expensive ($15/M input, $75/M output)
**Mitigation:** Consider caching, sub-agent result reuse, or Sonnet for non-critical paths

### Issue: Rate Limits
**Risk:** High volume could hit rate limits
**Mitigation:** Implement retry with backoff, consider request queuing
