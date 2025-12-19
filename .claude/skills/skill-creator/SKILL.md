---
name: skill-creator
description: Meta-skill for creating new BidDeed.AI and Life OS skills using Anthropic's official framework. Use when users want to create a new skill, update an existing skill, or extend Claude's capabilities with specialized knowledge for foreclosure analysis, auction intelligence, ADHD task tracking, swim performance, or any BidDeed.AI/Life OS workflow. Triggers on "create a skill", "new skill for", "build a skill", "skill for X".
---

# BidDeed.AI Skill Creator

Create production-ready skills for the BidDeed.AI ecosystem and Life OS platform.

## What Skills Provide

1. **Specialized workflows** - Multi-step procedures (Everest Ascent pipeline stages)
2. **Tool integrations** - API wrappers (BCPAO, AcclaimWeb, RealTDM, Supabase)
3. **Domain expertise** - Foreclosure law, lien priority, max bid formulas
4. **Bundled resources** - Scripts, templates, reference docs

## Core Principles

### Concise is Key
- Claude is already smart. Only add context Claude doesn't have.
- Challenge each piece: "Does this justify its token cost?"
- Prefer examples over explanations.
- Keep SKILL.md under 200 lines.

### Freedom Levels
- **High freedom**: Text instructions for context-dependent decisions
- **Medium freedom**: Pseudocode with parameters
- **Low freedom**: Exact scripts for fragile operations (e.g., AcclaimWeb scraping)

## Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown body (instructions)
├── scripts/           # Executable code
├── references/        # Load-on-demand docs
└── assets/           # Templates, images
```

### What NOT to Include
- README.md, CHANGELOG.md, INSTALLATION_GUIDE.md
- User-facing documentation
- Setup/testing procedures

## Progressive Disclosure

1. **Metadata** (~100 tokens) - Always in context
2. **SKILL.md body** (<500 lines) - Loaded when triggered
3. **References/Scripts** - Loaded only when Claude needs them

## Creating a New Skill

### Step 1: Understand the Skill
Ask clarifying questions:
- "What should this skill do?"
- "What triggers would activate it?"
- "What's an example workflow?"

### Step 2: Plan Resources
Analyze each use case:
- What scripts would be rewritten repeatedly? → scripts/
- What documentation would Claude reference? → references/
- What templates/assets are needed? → assets/

### Step 3: Initialize
Run the initialization script:

```bash
python scripts/init_skill.py <skill-name> --path /home/claude/skills
```

### Step 4: Edit the Skill

**Frontmatter:**
```yaml
---
name: skill-name
description: What it does AND when to use it. Include trigger patterns.
---
```

**Body patterns:**
- Workflow-based: Sequential steps (best for Everest Ascent stages)
- Task-based: Different operations (best for tool collections)
- Reference/Guidelines: Standards or specifications

### Step 5: Package
```bash
python scripts/package_skill.py /home/claude/skills/skill-name
```

### Step 6: Deploy to GitHub
Auto-commit to:
- BidDeed.AI: `.claude/skills/` in `breverdbidder/brevard-bidder-scraper`
- Life OS: `.claude/skills/` in `breverdbidder/life-os`

## BidDeed.AI Skill Patterns

### Everest Ascent Stage Skill
```markdown
---
name: stage-03-title-search
description: Execute Stage 3 of Everest Ascent - AcclaimWeb title search. Triggers on "title search", "chain of title", "recorded docs for [property]".
---

# Stage 3: Title Search

## Execution
1. Extract owner name from BCPAO data
2. Search AcclaimWeb for recorded documents
3. Build chain of title
4. Identify encumbrances

## Script
See `scripts/title_search.py` for AcclaimWeb automation.

## Output
Returns to pipeline state:
- `documents`: List of recorded instruments
- `encumbrances`: Mortgages, liens, judgments
- `clean_title`: boolean
```

### Life OS Task Skill
```markdown
---
name: task-tracker
description: ADHD-optimized task state tracking for Life OS. Triggers on "log task", "track this", "task status", "abandonment check".
---

# Task Tracker

## States
INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED/ABANDONED/BLOCKED/DEFERRED

## Abandonment Detection
- Context switch without closure
- >30 min after solution
- Session ends incomplete

## Interventions
See `references/adhd-interventions.md` for Level 1/2/3 protocols.
```

## LangGraph Integration

Skills deploy as LangGraph nodes:

```python
from langgraph.graph import StateGraph

class SkillState(TypedDict):
    input: dict
    output: dict
    errors: list

def skill_node(state: SkillState) -> SkillState:
    # Load SKILL.md
    # Execute scripts if needed
    # Return updated state
    pass
```

## Resources

- `scripts/init_skill.py` - Scaffold new skill
- `scripts/package_skill.py` - Validate and package
- `references/workflows.md` - Sequential/conditional patterns
- `references/output-patterns.md` - Template and example patterns
