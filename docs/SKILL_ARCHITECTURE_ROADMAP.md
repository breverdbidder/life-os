# Shapira Ecosystem Skill Architecture
## BidDeed.AI + Life OS Unified Framework

**Version:** 1.0.0  
**Date:** December 19, 2025  
**Status:** PRODUCTION DEPLOYMENT

---

## Executive Summary

This document establishes the permanent skill architecture for the Shapira ecosystem, adapting Anthropic's skill-creator framework for BidDeed.AI (foreclosure intelligence) and Life OS (ADHD-optimized productivity). Skills function as executable nodes within our LangGraph orchestration layer.

### Architecture Principles

1. **Context Window Efficiency** - Skills share the context window; every token must justify its cost
2. **Progressive Disclosure** - Metadata → SKILL.md → References (load only when needed)
3. **LangGraph Native** - Skills deploy as nodes with defined input/output schemas
4. **Domain Isolation** - BidDeed.AI, Life OS, and Shared skills remain separated

---

## Ecosystem Skill Taxonomy

```
shapira-skills/
├── shared/                         # Cross-ecosystem utilities
│   ├── supabase-integration/       # Database operations
│   ├── smart-router/               # LLM routing (FREE tier optimization)
│   ├── github-deployment/          # Auto-deploy workflows
│   └── cloudflare-pages/           # Frontend deployment
│
├── biddeed-ai/                     # Foreclosure intelligence
│   ├── auction-analysis/           # Property analysis pipeline
│   ├── lien-discovery/             # AcclaimWeb/RealTDM integration
│   ├── max-bid-calculator/         # ROI-based bid formulas
│   ├── bcpao-scraper/              # Property appraiser data
│   └── report-generator/           # DOCX auction reports
│
└── life-os/                        # ADHD productivity
    ├── task-tracker/               # State machine for tasks
    ├── michael-d1-swimming/        # Swim analytics + recruiting
    ├── learning-capture/           # YouTube/podcast insights
    └── adhd-interventions/         # Abandonment detection
```

---

## Skill Structure Standard

Every skill follows Anthropic's canonical structure:

```
skill-name/
├── SKILL.md                    # Required: metadata + instructions
├── scripts/                    # Optional: executable Python/Bash
│   └── main.py
├── references/                 # Optional: detailed docs loaded on-demand
│   └── api_reference.md
└── assets/                     # Optional: templates, images, fonts
    └── template.pptx
```

### SKILL.md Template

```yaml
---
name: skill-name
description: >
  [WHAT it does] + [WHEN to use it]. Include specific triggers:
  file types, scenarios, keywords that activate this skill.
---

# Skill Name

## Overview
1-2 sentences explaining what this skill enables.

## Workflow
Sequential steps with clear decision points.

## LangGraph Integration
- **Input Schema:** { required fields }
- **Output Schema:** { return structure }
- **State Updates:** What gets persisted

## Resources
- `scripts/main.py` - Executable logic
- `references/api.md` - Detailed API docs
```

---

## LangGraph Deployment Pattern

Skills integrate with our orchestration layer as nodes:

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AuctionState(TypedDict):
    case_number: str
    property_address: str
    liens: list
    max_bid: float
    recommendation: str  # BID | REVIEW | SKIP

# Skill as LangGraph node
def lien_discovery_node(state: AuctionState) -> AuctionState:
    """Execute lien-discovery skill as graph node."""
    # Skill logic here
    state["liens"] = discovered_liens
    return state

# Graph composition
graph = StateGraph(AuctionState)
graph.add_node("scrape", bcpao_scraper_node)
graph.add_node("liens", lien_discovery_node)
graph.add_node("calculate", max_bid_node)
graph.add_edge("scrape", "liens")
graph.add_edge("liens", "calculate")
```

---

## Priority Skills - Phase 1 (Week 1-2)

### 1. supabase-integration (Shared)
**Purpose:** Unified database operations for both ecosystems  
**Triggers:** "log this", "save to database", "query insights"  
**Scripts:** `insert_insight.py`, `query_activities.py`

### 2. auction-analysis (BidDeed.AI)
**Purpose:** Full 12-stage Everest Ascent pipeline  
**Triggers:** Foreclosure analysis, auction date, case number lookup  
**Scripts:** Pipeline orchestration, stage executors

### 3. task-tracker (Life OS)
**Purpose:** ADHD task state machine with interventions  
**Triggers:** Task creation, status updates, abandonment detection  
**References:** Intervention strategies, pattern recognition

### 4. michael-d1-swimming (Life OS)
**Purpose:** SwimCloud analytics + D1 recruiting tracker  
**Triggers:** Swim times, meet results, recruiting outreach  
**Scripts:** Time improvement analysis, rival comparison

---

## Phase 2 (Week 3-4)

### 5. lien-discovery (BidDeed.AI)
**Purpose:** AcclaimWeb + RealTDM automated search  
**Triggers:** HOA foreclosure, lien priority, senior mortgage  
**Scripts:** Anti-detection scraping, document parsing

### 6. smart-router (Shared)
**Purpose:** Multi-tier LLM routing for cost optimization  
**Triggers:** Any LLM call within ecosystem  
**Scripts:** Router logic, tier selection, token tracking

### 7. adhd-interventions (Life OS)
**Purpose:** Proactive accountability system  
**Triggers:** Context switch, task pending >30min, session end  
**References:** Intervention levels, micro-commitment templates

---

## Deployment Process

### Step 1: Initialize Skill
```bash
python3 /mnt/skills/examples/skill-creator/scripts/init_skill.py \
  auction-analysis --path /home/claude/skills/biddeed-ai
```

### Step 2: Implement Resources
- Write SKILL.md with proper frontmatter
- Add scripts for deterministic operations
- Create references for detailed documentation

### Step 3: Validate
```bash
python3 /mnt/skills/examples/skill-creator/scripts/quick_validate.py \
  /home/claude/skills/biddeed-ai/auction-analysis
```

### Step 4: Package
```bash
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py \
  /home/claude/skills/biddeed-ai/auction-analysis
```

### Step 5: Deploy to GitHub
```bash
# Push to .claude/skills/ in appropriate repo
git add .claude/skills/auction-analysis/
git commit -m "feat(skills): deploy auction-analysis skill"
git push origin main
```

---

## Repository Integration

### BidDeed.AI (brevard-bidder-scraper)
```
.claude/skills/
├── brevard-bidder-ai/     # Existing - needs migration
├── foreclosure-analysis/   # Existing - needs migration
├── safe-reader/            # Existing - keep
├── auction-analysis/       # NEW
├── lien-discovery/         # NEW
├── max-bid-calculator/     # NEW
└── report-generator/       # NEW
```

### Life OS (life-os)
```
.claude/skills/
├── task-tracker/           # NEW
├── michael-d1-swimming/    # NEW
├── learning-capture/       # NEW
└── adhd-interventions/     # NEW
```

### Shared Skills (both repos)
```
.claude/skills/shared/
├── supabase-integration/
├── smart-router/
├── github-deployment/
└── cloudflare-pages/
```

---

## Governance Rules

1. **One Skill = One Domain** - No kitchen sink skills
2. **Description = Trigger** - Put all activation logic in YAML description
3. **SKILL.md < 500 lines** - Split to references if larger
4. **Test Before Package** - Run scripts, verify outputs
5. **Version in Commits** - Semantic versioning in commit messages

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Context efficiency | <5K tokens/skill | Token counter |
| Trigger accuracy | >90% correct activation | Manual audit |
| LangGraph integration | All skills as nodes | Code review |
| Documentation coverage | 100% frontmatter complete | Validation script |

---

## Next Actions

1. ☐ Create skill directories in both repos
2. ☐ Implement supabase-integration (shared foundation)
3. ☐ Migrate existing skills to new structure
4. ☐ Deploy auction-analysis with full pipeline
5. ☐ Deploy task-tracker with ADHD interventions
6. ☐ Create GitHub Actions for skill validation

---

*Document maintained by AI Architect (Claude Opus 4.5)*  
*Last updated: December 19, 2025*
