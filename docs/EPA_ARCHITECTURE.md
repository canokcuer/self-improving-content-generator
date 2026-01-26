# EPA-GONCA-ALP Architecture

## Overview

This document describes the new agent architecture for TheLifeCo Content Assistant, featuring EPA as the main orchestrator with GONCA and ALP as sub-agents.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                               │
│                          (Streamlit create_mode.py)                       │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           EPA (Main Orchestrator)                         │
│                                                                          │
│  Responsibilities:                                                       │
│  • Direct user interaction through Socratic questioning                  │
│  • Collect ALL 13 required brief fields before content generation        │
│  • Coordinate sub-agents (GONCA, ALP, Review)                           │
│  • Review ALL sub-agent output before presenting to user                 │
│  • Make final adjustments for quality and alignment                      │
│  • Route feedback to appropriate sub-agent for revisions                 │
│                                                                          │
│  Has FULL ACCESS to:                                                     │
│  • Knowledge base (no source filtering)                                  │
│  • All sub-agents via tool calls                                         │
│  • User conversation history                                             │
│                                                                          │
│  Tools:                                                                  │
│  • search_knowledge - Search entire knowledge base                       │
│  • consult_gonca - Get wellness facts from GONCA                        │
│  • consult_alp - Get content from ALP (requires complete brief)         │
│  • analyze_feedback - Analyze user feedback                              │
└────────┬────────────────────────┬────────────────────────┬───────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     GONCA       │    │      ALP        │    │     Review      │
│ (Wellness Expert)│    │(Storytelling)   │    │(Feedback Analyzer)│
│                 │    │                 │    │                 │
│ Provides:       │    │ Creates:        │    │ Analyzes:       │
│ • Program info  │    │ • Hooks         │    │ • User feedback │
│ • Center details│    │ • Content body  │    │ • Categorizes   │
│ • Verified facts│    │ • CTAs          │    │ • Routes issues │
│ • Compliance    │    │ • Hashtags      │    │ • Extracts      │
│   guidance      │    │ • Open loops    │    │   requests      │
│                 │    │                 │    │                 │
│ Knowledge:      │    │ Receives:       │    │ Returns:        │
│ • Full KB access│    │ • FULL context  │    │ • Feedback type │
│                 │    │ • Brief         │    │ • Suggested     │
│                 │    │ • Wellness facts│    │   action        │
│                 │    │ • User voice    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┴────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    Knowledge Base       │
                    │  (Supabase + pgvector)  │
                    │                         │
                    │  • Programs & services  │
                    │  • Center information   │
                    │  • Wellness content     │
                    │  • Brand guidelines     │
                    │  • Storytelling patterns│
                    └─────────────────────────┘
```

## Workflow Stages

### Stage 1: Briefing (EPA)

```
EPA <──> User
    │
    │ Socratic questioning to collect:
    │
    │ REQUIRED (13 fields):
    │ 1. Target Audience
    │ 2. Pain Area (CRUCIAL - drives everything)
    │ 3. Compliance Level (high/low)
    │ 4. Funnel Stage (awareness/consideration/conversion/loyalty)
    │ 5. Value Proposition
    │ 6. Desired Action
    │ 7. Specific Programs
    │ 8. Specific Centers
    │ 9. Tone
    │ 10. Key Messages
    │ 11. Constraints
    │ 12. Platform
    │ 13. Price Points
    │
    │ + Campaign fields for conversion stage:
    │   - Campaign price
    │   - Campaign duration
    │   - Campaign center
    │   - Campaign deadline
    │
    └──> Brief Complete? ──NO──> Continue questioning
              │
              YES
              │
              ▼
```

### Stage 2: Consulting GONCA (Wellness Facts)

```
EPA ──[consult_gonca]──> GONCA
                           │
                           │ GONCA searches knowledge base for:
                           │ • Program details
                           │ • Center information
                           │ • Verified wellness facts
                           │ • Compliance guidance
                           │
                           ▼
                    WellnessResponse
                    ┌─────────────────────┐
                    │ verified_facts: []   │
                    │ program_details: {}  │
                    │ center_info: {}      │
                    │ wellness_guidance    │
                    │ confidence_level     │
                    │ warnings: []         │
                    └─────────────────────┘
                           │
                           ▼
                    EPA stores response
```

### Stage 3: Consulting ALP (Content Creation)

```
EPA ──[consult_alp]──> ALP
                        │
                        │ ALP receives FULL context:
                        │ • Complete brief (all 13 fields)
                        │ • Wellness facts from GONCA
                        │ • User voice preferences
                        │ • Style guidance
                        │ • Conversation context
                        │ • Previous feedback (if revision)
                        │
                        ▼
                 ALP creates content using:
                 • Best storytelling framework
                 • Platform-specific format
                 • Brand voice guidelines
                        │
                        ▼
                 StorytellingResponse
                 ┌─────────────────────┐
                 │ hook                 │
                 │ hook_type            │
                 │ content              │
                 │ call_to_action       │
                 │ hashtags             │
                 │ open_loops           │
                 │ storytelling_framework│
                 │ word_count           │
                 │ alternative_hooks    │
                 │ confidence_notes     │
                 └─────────────────────┘
                        │
                        ▼
                 EPA reviews content
```

### Stage 4: EPA Review & Presentation

```
EPA reviews ALP's content:
├── Does it address the Pain Area?
├── Are facts from GONCA used correctly?
├── Does it match requested tone?
├── Is it appropriate for platform?
├── Is the CTA clear and compelling?
│
└──> Make adjustments if needed
         │
         ▼
    Present to User
```

### Stage 5: Feedback Loop

```
User provides feedback
         │
         ▼
EPA ──[analyze_feedback]──> Review Sub-Agent
                              │
                              │ Analyzes feedback:
                              │ • Wellness issues?
                              │ • Storytelling issues?
                              │ • Both?
                              │ • Approved?
                              │
                              ▼
                       FeedbackAnalysis
                       ┌─────────────────────┐
                       │ feedback_type       │
                       │ wellness_issues     │
                       │ storytelling_issues │
                       │ specific_requests   │
                       │ suggested_action    │
                       └─────────────────────┘
                              │
                              ▼
EPA routes based on feedback_type:
├── "wellness" ──> Consult GONCA again
├── "storytelling" ──> Consult ALP again (with feedback)
├── "both" ──> GONCA then ALP
└── "approved" ──> Finalize
```

## Data Flow

### ContentBrief (13 Required Fields)

```python
ContentBrief:
  # Required (must have all before content generation)
  target_audience: str
  pain_area: str          # CRUCIAL - the north star
  compliance_level: enum  # high or low
  funnel_stage: enum      # awareness/consideration/conversion/loyalty
  value_proposition: str
  desired_action: str
  specific_programs: list[str]
  specific_centers: list[str]
  tone: str
  key_messages: list[str]
  constraints: str
  platform: enum
  price_points: str

  # Campaign (required for conversion stage)
  has_campaign: bool
  campaign_price: str
  campaign_duration: str
  campaign_center: str
  campaign_deadline: str
```

### Sub-Agent Requests

```
WellnessRequest:
├── query: str
├── brief: ContentBrief
├── context: str
└── specific_topics: list[str]

StorytellingRequest:
├── brief: ContentBrief           # Full brief
├── wellness_facts: WellnessResponse  # From GONCA
├── user_voice: str
├── style_guidance: str
├── conversation_context: str
├── previous_feedback: str        # If revision
└── iteration_number: int

FeedbackRequest:
├── user_feedback: str
├── generated_content: StorytellingResponse
├── brief: ContentBrief
└── wellness_facts: WellnessResponse
```

## Key Design Decisions

### 1. EPA Has Full Knowledge Access
- No source filtering for EPA
- Can search entire knowledge base
- Sub-agents also have full access (needed for accurate information)

### 2. ALP Receives FULL Context
- Not just a "topic" or "summary"
- Complete brief with all 13 fields
- All verified facts from GONCA
- User voice and style preferences
- Relevant conversation context
- Previous feedback for iterations

### 3. EPA Reviews Everything
- All sub-agent output goes through EPA
- EPA can make adjustments before presenting to user
- Ensures consistency and quality

### 4. Feedback Routes Intelligently
- Wellness issues → GONCA
- Storytelling issues → ALP
- Both → GONCA first, then ALP with updated facts

### 5. Pain Area is the North Star
- Most crucial field in the brief
- EPA asks about it early and deeply
- ALP's content must address it specifically

## File Structure

```
content_assistant/agents/
├── types.py              # Shared types: ContentBrief, WellnessResponse, etc.
├── epa_agent.py          # EPA main orchestrator
├── gonca_agent.py        # GONCA wellness sub-agent
├── alp_agent.py          # ALP storytelling sub-agent
├── review_subagent.py    # Review feedback analyzer
├── base_agent.py         # Base class (existing)
└── __init__.py           # Updated exports
```

## UI Integration

### Stage Indicator Updates

```python
# In create_mode.py
STAGE_INFO = {
    EPAStage.BRIEFING: {
        "name": "Briefing",
        "description": "Understanding your content needs",
        "thinking": "EPA is gathering requirements..."
    },
    EPAStage.CONSULTING_GONCA: {
        "name": "Research",
        "description": "EPA is consulting GONCA (wellness expert)",
        "thinking": "Gathering verified facts..."
    },
    EPAStage.CONSULTING_ALP: {
        "name": "Creating",
        "description": "EPA is consulting ALP (storytelling expert)",
        "thinking": "Crafting your content..."
    },
    EPAStage.REVIEWING: {
        "name": "Review",
        "description": "EPA is reviewing content",
        "thinking": "Quality checking..."
    },
    ...
}
```

### Sub-Agent Indicators

```
[EPA is consulting GONCA...]  # When consult_gonca tool is called
[EPA is consulting ALP...]    # When consult_alp tool is called
[EPA is analyzing feedback...] # When analyze_feedback is called
```

## Migration from Current Architecture

### Current (AgentCoordinator)
- State machine routing between stages
- Each agent is independent
- Limited context passing
- No central review

### New (EPA)
- EPA orchestrates everything
- Sub-agents invoked as tools
- Full context to ALP
- EPA reviews all output

### Migration Steps
1. Create new agent files (types, epa, gonca, can, review) ✓
2. Update create_mode.py to use EPA instead of AgentCoordinator
3. Update conversation persistence for EPAState
4. Retire old coordinator and stage-based agents
5. Test end-to-end flow
