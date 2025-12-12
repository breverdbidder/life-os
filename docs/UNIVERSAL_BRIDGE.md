# Life OS Universal Bridge

## Overview

The Universal Bridge is the core integration pattern that connects **conversations with Claude Opus 4.5 (AI Architect)** to **all Life OS domains** via Supabase. One interface, all domains tracked.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LIFE OS - UNIVERSAL BRIDGE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ARIEL SAYS ANYTHING → CLAUDE ROUTES TO CORRECT TABLE → TRACKED       │
│                                                                         │
│   "Michael swam 52.4 in the 100"     → michael_swim_times              │
│   "Log my sleep - 7 hours"           → health_logs                      │
│   "Shabbat dinner Friday"            → family_events                    │
│   "I need to review the Dec 17 list" → tasks (ADHD tracked)            │
│   "Watched a video on LangGraph"     → learning_sessions               │
│   "Deploy BECA fix"                  → orchestrated_tasks (Claude Code) │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Architecture

```
┌──────────────────────┐
│  Claude Opus 4.5     │
│  (AI Architect)      │
│  claude.ai chat      │
└──────────┬───────────┘
           │
           │  Natural Language
           ▼
┌──────────────────────┐
│  Universal Bridge    │
│  life_os_bridge.py   │
│  - Parses intent     │
│  - Routes to table   │
│  - Formats data      │
└──────────┬───────────┘
           │
           │  REST API (curl/httpx)
           ▼
┌──────────────────────┐
│  Supabase            │
│  mocerqjnksmhcjzxrewo│
│  - 20+ tables        │
│  - All domains       │
└──────────┬───────────┘
           │
           │  Triggers & Queries
           ▼
┌──────────────────────┐
│  Downstream Systems  │
│  - LangGraph         │
│  - Claude Code       │
│  - Daily Reports     │
│  - ADHD Tracking     │
└──────────────────────┘
```

## Domain Tables

### 🏢 BUSINESS (BidDeed.AI)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `orchestrated_tasks` | Claude Code task queue | task_id, status, priority, tsf |
| `langgraph_state` | Workflow state machine | workflow_id, pending_nodes, completed_nodes |
| `langgraph_transitions` | State change audit log | from_node, to_node, trigger |
| `historical_auctions` | Past auction data | case_number, sale_price, outcome |
| `bid_decisions` | Bid/skip decisions | decision, max_bid, reasoning |
| `everest_ascent_stages` | 12-stage pipeline config | stage_name, stage_order |

### 🏊 MICHAEL SWIMMING

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `michael_swim_times` | Race/practice times | event, time_seconds, meet_name |
| `michael_nutrition` | Daily nutrition | calories, protein_g, is_keto_day |
| `michael_recruiting` | D1 coach outreach | school, coach_name, status |

### 👨‍👩‍👦 FAMILY

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `family_events` | Family calendar | title, event_type, date |

### 🧠 ADHD/PRODUCTIVITY

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `tasks` | Task tracking | title, domain, status, complexity |
| `task_states` | State transitions | task_id, from_state, to_state |
| `activities` | Activity log | activity_type, duration |
| `daily_metrics` | Daily productivity | tasks_completed, focus_minutes |
| `focus_scores` | Focus quality tracking | score, factors |
| `task_interventions` | ADHD interventions | intervention_type, task_id |
| `abandonment_patterns` | Pattern detection | reason, pattern_notes |
| `task_completion_streaks` | Streak tracking | streak_count, domain |

### 💡 INSIGHTS & LEARNING

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `insights` | Insights & realizations | title, insight_type, action_taken |
| `learning_sessions` | YouTube/article logs | topic, source, key_takeaways |

### ❤️ HEALTH

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `health_logs` | Daily health metrics | sleep_hours, energy_level, focus_quality |

### 🎯 GOALS

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `goals` | Goal tracking | title, target_date, progress |

## Usage

### Python Module

```python
from life_os_bridge import LifeOSBridge

bridge = LifeOSBridge()

# 🏊 Michael Swimming
bridge.log_swim_time("100 Free", 52.45, "Practice")
bridge.log_nutrition(calories=2000, protein_g=150, is_keto_day=True)
bridge.log_recruiting_contact("University of Florida", "Coach Smith")

# ❤️ Health
bridge.log_health(sleep_hours=7.5, energy_level=8, focus_quality=9)

# 💡 Learning
bridge.log_learning(
    topic="LangGraph Multi-Agent Systems",
    source="YouTube",
    key_takeaways=["State machines", "Checkpointing"],
    duration_minutes=25
)

# 🧠 ADHD Tasks
bridge.create_task(
    title="Review Dec 17 auction list",
    domain="BUSINESS",
    priority="high",
    complexity=6
)

# 👨‍👩‍👦 Family
bridge.log_family_event("Shabbat Dinner", "Shabbat", "2025-12-13")

# 🏢 Deploy to Claude Code
bridge.deploy_to_claude_code(
    objective="Fix BECA anti-bot detection",
    priority="P0",
    repository="breverdbidder/brevard-bidder-scraper",
    target_file="src/scrapers/beca_manus_v22.py"
)

# 📊 Queries
queue = bridge.get_orchestration_queue()
summary = bridge.get_daily_summary()
progress = bridge.get_swim_progress("100 Free")
```

### CLI

```bash
# Check Claude Code queue
python life_os_bridge.py --action queue

# Get daily summary
python life_os_bridge.py --action summary

# Log swim time
python life_os_bridge.py --action swim --data '{"event": "100 Free", "time_seconds": 52.45}'

# Log health
python life_os_bridge.py --action health --data '{"sleep_hours": 7.5, "energy_level": 8}'

# Create task
python life_os_bridge.py --action task --data '{"title": "Review auction list", "domain": "BUSINESS"}'

# Deploy to Claude Code
python life_os_bridge.py --action deploy --data '{"objective": "Fix scraper", "priority": "P0"}'
```

### From Claude.ai Conversation

Just tell Claude naturally:

| You Say | Claude Does |
|---------|-------------|
| "Michael's 50 Free was 23.5 at practice" | `bridge.log_swim_time("50 Free", 23.5, "Practice")` |
| "Log 7 hours sleep, energy 6" | `bridge.log_health(sleep_hours=7, energy_level=6)` |
| "Shabbat dinner at 6pm Friday" | `bridge.log_family_event("Shabbat Dinner", "Shabbat", "2025-12-13")` |
| "Deploy a P0 fix for BECA scraper" | `bridge.deploy_to_claude_code(...)` |
| "What's in the Claude Code queue?" | `bridge.get_orchestration_queue()` |

## Environment Variables

```bash
SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
SUPABASE_KEY=your_service_role_key
```

## Integration with LangGraph

The bridge's `deploy_to_claude_code()` method creates Task Specification Format (TSF) entries that the LangGraph orchestrator picks up:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Claude Opus 4.5 calls bridge.deploy_to_claude_code()       │
│                          │                                      │
│                          ▼                                      │
│  2. TSF inserted to orchestrated_tasks table                   │
│                          │                                      │
│                          ▼                                      │
│  3. LangGraph Orchestrator (every 30 min) picks up task        │
│                          │                                      │
│                          ▼                                      │
│  4. Claude Code Mobile/Web/CLI executes                        │
│                          │                                      │
│                          ▼                                      │
│  5. PR created, status updated, workflow advances              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## ADHD Optimizations

The bridge is designed for ADHD-friendly workflow:

1. **Zero context switching** - One interface for everything
2. **Natural language** - No need to remember table names
3. **Automatic tracking** - Tasks are logged with timestamps
4. **Pattern detection** - Abandonment patterns logged for analysis
5. **Interventions** - System can trigger accountability reminders

## Files

| File | Location | Purpose |
|------|----------|---------|
| `life_os_bridge.py` | `lib/life_os_bridge.py` | Main Python module |
| `UNIVERSAL_BRIDGE.md` | `docs/UNIVERSAL_BRIDGE.md` | This documentation |
| `bridge_config.json` | `config/bridge_config.json` | Table mappings |

---

**Author**: Claude Opus 4.5 (AI Architect)  
**Owner**: Ariel Shapira, Everest Capital USA  
**Created**: December 12, 2025
