# TheLifeCo Content Assistant - Architecture Changes Summary

**Last Updated:** January 23, 2025
**Purpose:** Document major architecture changes for session continuity

---

## Overview

The TheLifeCo Content Assistant is being transformed from a **form-based content generator** to a **fully agentic, conversational system** with self-improving capabilities.

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
- **Orchestrator Agent:** Conversational briefing, funnel detection
- **Wellness Agent:** Fact verification against knowledge base
- **Storytelling Agent:** Content creation with engagement optimization
- **Review Agent:** Feedback collection, learning extraction

**Pipeline Flow:**
```
User → Orchestrator (brief) → Wellness (verify) → Storytelling (preview → content) → Review (feedback)
```

**Why:**
- Separation of concerns (each agent specializes)
- Better fact accuracy through dedicated verification
- Structured feedback enables learning
- Easier to improve individual components

---

### 3. From Session-Based → Forever Conversations

**Before:**
- Each session started fresh
- No way to continue editing content
- History showed generations, not conversations

**After:**
- Conversations persist in database
- Users can continue where they left off
- Full message history preserved
- Edit content through ongoing dialogue

**Why:**
- Content often needs multiple iterations
- Users return to refine over days/weeks
- Better context for follow-up requests

---

### 4. From Flat Knowledge → Agent-Specific Knowledge

**Before:**
```
knowledge/
├── brand_usps.md
├── hook_patterns.md
├── wellness_knowhow.md
└── ... (all flat)
```

**After:**
```
knowledge/
├── orchestrator/
│   ├── funnel_stages.md        # Marketing funnel definitions
│   ├── briefing_guidelines.md  # How to conduct conversations
│   └── clarification_patterns.md # Common clarification questions
├── wellness/
│   ├── wellness_knowhow.md
│   ├── programs_and_offerings.md
│   ├── thelifeco_method.md
│   ├── pain_solution_matrix.md
│   └── centers/
│       ├── center_antalya.md
│       ├── center_bodrum.md
│       ├── center_phuket.md
│       └── center_sharm.md
├── storytelling/
│   ├── hook_patterns.md
│   ├── engagement_guide.md
│   ├── platform_rules.md
│   └── cta_guidelines.md
└── brand/
    └── brand_usps.md
```

**Why:**
- Each agent accesses only relevant knowledge
- Faster, more focused searches
- Easier to maintain and update
- Clear ownership of knowledge areas

---

### 5. From Basic Feedback → Self-Improving Learning System

**Before:**
- Star rating (1-5)
- "What worked" checkboxes
- Few-shot examples from high-rated content

**After:**
- Structured + open-ended feedback
- Learning extraction from feedback patterns
- Admin review queue for learnings
- Approved learnings applied to future generations
- Role-based access (user, editor, admin)

**Learning Types:**
- **Pattern:** "Users prefer shorter hooks on Instagram"
- **Preference:** "User X prefers formal tone"
- **Correction:** "Don't say X, say Y instead"
- **Style:** "Wellness content works better with statistics"

**Why:**
- System improves over time
- Admin control over what's learned
- Patterns identified across multiple users
- Quality control through review process

---

### 6. Marketing Funnel Integration

**New Feature:** Content automatically aligned to funnel stage

**Funnel Stages:**
1. **Awareness:** Educate, create problem awareness (soft CTAs)
2. **Consideration:** Help decide, differentiate (medium CTAs)
3. **Conversion:** Drive bookings, specific offers (strong CTAs)
4. **Loyalty:** Retain, encourage referrals (relationship CTAs)

**How It Works:**
- Orchestrator detects funnel stage from conversation
- Storytelling Agent adapts content style
- CTAs match the stage
- Campaign details collected for conversion content

**Why:**
- Content should match where audience is in journey
- Different stages need different approaches
- Prevents mismatch (e.g., hard sell to unaware audience)

---

### 7. Dynamic Campaign/Pricing Collection

**Before:** Pricing stored in knowledge base (static)

**After:** Orchestrator asks user during conversation:
- "Is this for a specific campaign/promotion?"
- "What's the price point?"
- "What duration?" (3-day, 7-day, etc.)
- "Which center(s)?"
- "Any deadline/limited availability?"

**Why:**
- Pricing changes frequently
- Campaigns are time-limited
- More accurate than outdated KB
- User always has latest info

---

### 8. From Form UI → Chat UI

**Before:**
- Multi-step form wizard
- Fixed question sequence
- No back-and-forth

**After:**
- Chat interface (like ChatGPT/Claude)
- Message bubbles for user and agents
- Agent status indicator
- Real-time conversation flow
- Side panel with brief summary

**Why:**
- More natural interaction
- Easier to clarify and iterate
- Matches user expectations from AI tools
- Better for "continue conversation" feature

---

## New Database Tables

### 1. agent_configurations
Stores settings for each agent (system prompt, model, tools, etc.)

### 2. agent_learnings
Stores learnings extracted from feedback
- learning_type, content, confidence_score
- is_approved (admin approval)
- times_applied, success_rate

### 3. feedback_reviews
Detailed feedback with admin review workflow
- rating, feedback_text, what_worked, what_needs_work
- admin_review_status, admin_notes

### 4. conversations
Persistent conversation storage
- messages (JSONB array)
- current_agent, agent_state
- brief_data, funnel_stage, campaign_info

### 5. user_roles
Role-based access control
- role: user, editor, admin, super_admin
- permissions (granular)

---

## New Files Created

### Agents (`content_assistant/agents/`)
| File | Purpose |
|------|---------|
| `__init__.py` | Exports all agents and data classes |
| `base_agent.py` | Base class with Claude tool use, conversation management |
| `orchestrator.py` | Conversational briefing, funnel detection, campaign collection |
| `wellness_agent.py` | Fact verification against knowledge base |
| `storytelling_agent.py` | Content creation with hooks and engagement |
| `review_agent.py` | Feedback collection, learning extraction |
| `coordinator.py` | Sequential agent execution, state management |

### Database (`content_assistant/db/`)
| File | Purpose |
|------|---------|
| `conversations.py` | CRUD operations for conversation persistence |
| `schema.sql` | Updated with 5 new tables |

### Knowledge Base (`knowledge/`)
| Folder | Purpose |
|--------|---------|
| `orchestrator/` | Briefing guidelines, funnel stages, clarification patterns |
| `wellness/` | Programs, therapies, center info |
| `wellness/centers/` | Center-specific information |
| `storytelling/` | Hooks, engagement, platform rules, CTAs |
| `brand/` | Brand USPs and voice |

---

## Configuration Changes

### `config.py`
- Default model changed to `claude-opus-4-5-20250114`

### `generation/claude_client.py`
- Added Opus 4.5 pricing
- Updated pricing comment year

---

## Remaining Tasks

### High Priority
1. **#19 Chat UI** - Replace form with chat interface
2. **#2-6 Bug fixes** - OAuth, password reset, feedback field, history

### After Implementation
3. **#20 Integration testing** - End-to-end validation

---

## How Agents Work Together

### AgentCoordinator Flow:

```python
coordinator = AgentCoordinator()

# Stage 1: Orchestrator (conversational briefing)
while not brief_complete:
    response = coordinator.process_message(user_input)
    # Agent asks clarifying questions
    # Detects funnel stage
    # Collects campaign info if conversion

# Stage 2: Wellness (automatic)
# Verifies brief against knowledge base
# Provides verified facts for content

# Stage 3: Storytelling Preview
# Generates hook + open loops + promise
# User approves or requests changes

# Stage 4: Storytelling Content
# Generates full content based on approved preview

# Stage 5: Review
# Collects feedback
# Extracts learnings
# Queues for admin review if needed
```

### Agent Tools:
Each agent has access to specific tools:
- **Orchestrator:** search_knowledge, get_similar_content, get_program_details, get_center_info
- **Wellness:** verify_program, verify_center, verify_wellness_claim, get_verified_facts
- **Storytelling:** get_hook_patterns, get_platform_rules, get_engagement_tactics, get_cta_templates
- **Review:** store_feedback, extract_learning, queue_for_review, get_approved_learnings

---

## Key Design Decisions

1. **Pricing NOT in Knowledge Base:** Collected dynamically from user
2. **Doctor Info NOT Required:** Deprioritized, can be added later
3. **Sequential Agent Execution:** Not parallel, each agent builds on previous
4. **Admin Approval for Learnings:** Prevents bad patterns from being applied
5. **Campaign Details Only for Conversion:** Other funnel stages don't need pricing

---

## To Continue Development

1. Read this file for context
2. Check `TaskList` for pending tasks
3. Key files to understand:
   - `content_assistant/agents/coordinator.py` - Main orchestration
   - `content_assistant/agents/orchestrator.py` - Briefing logic
   - `content_assistant/db/schema.sql` - Database structure
   - `knowledge/orchestrator/funnel_stages.md` - Funnel definitions

---

## Testing the New Architecture

```python
from content_assistant.agents import AgentCoordinator

# Create coordinator
coordinator = AgentCoordinator()

# Process user messages
result = coordinator.process_message("I want to create content about our detox program")
print(result["response"])  # Agent's response
print(result["stage"])     # Current stage
print(result["stage_complete"])  # Whether to move to next stage

# Continue conversation
result = coordinator.process_message("It's for Instagram, targeting busy professionals")
# ... and so on
```

---

## Contact / Questions

This document serves as the handoff between sessions. If continuing development:
1. Review pending tasks with `TaskList`
2. Understand the agent flow in `coordinator.py`
3. Check UI changes needed in `ui/create_mode.py`
