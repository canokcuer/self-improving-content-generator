# Ralph Agent Instructions - TheLifeCo Content Assistant

You are an autonomous coding agent building TheLifeCo's Self-Improving Content Marketing Assistant.

## CRITICAL: Read PLAN.md Before Implementing

The file `/Users/canokcuer/thelifeco/PLAN.md` contains **complete implementation details** for every story including:
- Exact code to write (copy it!)
- File paths and structures
- Test code
- Acceptance criteria with verification commands

**Before implementing ANY story:**
1. Read `scripts/ralph/prd.json` to identify the current story
2. Search PLAN.md for "#### Story N:" to find the implementation details
3. Follow the specifications exactly

## Your Task

1. Read the PRD at `scripts/ralph/prd.json`
2. Read the progress log at `scripts/ralph/progress.txt` (check Codebase Patterns section first)
3. Read `AGENTS.md` for project conventions
4. Check you're on the correct branch from PRD `branchName`. If not, check it out or create from main.
5. Pick the **highest priority** user story where `passes: false`
6. **READ PLAN.md** for that story's implementation details (search for "#### Story N:")
7. Implement that single user story following PLAN.md specifications
8. Run quality checks
9. If checks pass, commit ALL changes
10. Update the PRD to set `passes: true` for the completed story
11. Append your progress to `scripts/ralph/progress.txt`

## Project Setup

```bash
# Working directory
cd /Users/canokcuer/thelifeco

# Activate virtual environment (ALWAYS do this first)
source .venv/bin/activate

# Quality checks
ruff check content_assistant/ tests/
pytest tests/ -v -k 'not integration'

# Test Streamlit app starts (for UI stories)
timeout 3 streamlit run content_assistant/app.py --server.headless true
```

## Quality Requirements

Before committing, ALL of these must pass:

```bash
source .venv/bin/activate
ruff check content_assistant/ tests/
pytest tests/ -v -k 'not integration'
```

- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns from PLAN.md

## Commit Message Format

```
feat: [story-N] - Story Title

- Brief description of what was implemented
```

Example:
```
feat: [story-1] - Initialize Project Structure

- Created content_assistant package with all subdirectories
- Added requirements.txt with pinned dependencies
- Created test fixtures in conftest.py
```

## Progress Report Format

APPEND to `scripts/ralph/progress.txt`:
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
---
```

## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.

If ALL 27 stories are complete and passing, reply with:
<promise>COMPLETE</promise>

If there are still stories with `passes: false`, end your response normally (another iteration will pick up the next story).

## Important Reminders

- Work on ONE story per iteration
- ALWAYS read PLAN.md for implementation details before coding
- Commit after each successful story
- Update prd.json to mark `passes: true`
- Use the exact code from PLAN.md - it has been designed to pass acceptance criteria
- Run quality checks BEFORE committing
