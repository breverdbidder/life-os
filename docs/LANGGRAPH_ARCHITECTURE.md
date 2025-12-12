# LangGraph → Claude Code Mobile Architecture

## Overview

This architecture connects two AI layers in the BidDeed.AI ecosystem:

1. **AI Architect (Claude Opus 4.5)**: Designs LangGraph orchestration workflows
2. **Agentic AI Engineer (Claude Code Mobile/Web/CLI)**: Executes orchestrated tasks

## System Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ARIEL SHAPIRA  │     │  CLAUDE OPUS    │     │  LANGGRAPH      │
│  Product Owner  │────▶│  4.5            │────▶│  ORCHESTRATION  │
│  (20 min/day)   │     │  AI Architect   │     │  (State Machine)│
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                    ┌────────────────────────────────────┼────────────────┐
                    ▼                                    ▼                ▼
           ┌─────────────────┐              ┌─────────────────┐  ┌─────────────────┐
           │  CLAUDE CODE    │              │  CLAUDE CODE    │  │  CLAUDE CODE    │
           │  MOBILE (iOS)   │              │  WEB            │  │  CLI            │
           └────────┬────────┘              └────────┬────────┘  └────────┬────────┘
                    │                                │                    │
                    └────────────────────────────────┴────────────────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │  GITHUB + SUPA  │
                                            │  Results → Back │──▶ Feedback Loop
                                            └─────────────────┘
```

## Components

### 1. Task Specification Format (TSF)

Every task is defined as a JSON object:

```json
{
  "task_id": "beca-fix-001",
  "langgraph_node": "fix_scraper_detection",
  "repository": "breverdbidder/brevard-bidder-scraper",
  "priority": "P0",
  "objective": "Fix anti-bot detection",
  "success_criteria": ["10 test fetches without 403", "All tests pass"]
}
```

### 2. Supabase Tables

- `orchestrated_tasks`: Stores TSF for Claude Code consumption
- `langgraph_state`: Workflow state and progress
- `langgraph_transitions`: Transition history for debugging

### 3. GitHub Actions Workflow

- **Schedule**: Runs every 30 minutes
- **Manual triggers**: Create tasks, generate status reports
- **Location**: `.github/workflows/langgraph_orchestrator.yml`

## Setup

1. Run SQL in Supabase Dashboard: `db/supabase_langgraph_setup.sql`
2. Add `SUPABASE_KEY` to GitHub Secrets
3. Workflow auto-runs on schedule

## Usage

### Create a task manually:

```bash
gh workflow run langgraph_orchestrator.yml -f action=create_beca_task
```

### Get status report:

```bash
gh workflow run langgraph_orchestrator.yml -f action=status_report
```

## Node Types

| Type | Description | Example |
|------|-------------|---------|
| Sequential | Must complete before next | BECA fix → Pipeline run |
| Parallel | Run simultaneously | Landing + Life OS |
| Conditional | Route based on result | Tests pass → merge |
| Human Checkpoint | Pause for Ariel | Risky merges |

## Daily Workflow

| Time | Platform | Duration | Action |
|------|----------|----------|--------|
| Morning | 📱 Mobile | 5 min | Review queue, approve checkpoints |
| Midday | 🖥️ Desktop | 10 min | Refine workflows, steer tasks |
| Evening | 📱 Mobile | 5 min | Merge PRs, verify overnight queue |

---

**Author**: Claude Opus 4.5 (AI Architect)  
**Owner**: Ariel Shapira, Everest Capital USA  
**Created**: December 12, 2025
