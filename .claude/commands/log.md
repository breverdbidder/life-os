---
description: Log an insight or activity to Supabase
allowed-tools: Bash(gh:*), Bash(python:*)
argument-hint: [category] [content]
---

# Log to Supabase

## Arguments
- `$1`: Category (learning, michael_swim, health_log, tasks, claude_performance)
- `$2...`: Content description

## Categories

| Category | Table | Purpose |
|----------|-------|---------|
| learning | insights | Learning sessions |
| michael_swim | michael_swim_times | Swim performance |
| health_log | health_logs | Health tracking |
| tasks | tasks | ADHD task tracking |
| claude_performance | insights | AI performance scoring |

## Logging Command

```bash
gh workflow run insert_insight.yml \
  -f category="$1" \
  -f content="$ARGUMENTS"
```

## Quick Log Examples

### Learning Session
```bash
/log learning "YouTube: AI agents tutorial - key insight: use checkpoints"
```

### Michael Swim Time
```bash
/log michael_swim "50 Free: 23.45 at Harry Meisel meet"
```

### Health Log
```bash
/log health_log "Sleep: 7hrs, Energy: 7/10, Focus: 8/10"
```

## Verify Logged

```bash
gh run list --workflow=insert_insight.yml --limit=3
```
