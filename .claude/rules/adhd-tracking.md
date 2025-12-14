---
paths: src/**/*.py
---

# ADHD Task Tracking Rules - Life OS

## Task State Machine

```
INITIATED
    ↓ (Claude provides solution)
SOLUTION_PROVIDED
    ↓ (User starts execution)
IN_PROGRESS
    ↓
┌───────────────────────────────────────┐
│  COMPLETED  │  ABANDONED  │  BLOCKED  │  DEFERRED  │
└───────────────────────────────────────┘
```

## Mandatory Tracking Fields

Every task must track:
- `task_id`: Unique identifier
- `description`: What needs to be done
- `domain`: BUSINESS | MICHAEL | FAMILY | PERSONAL
- `complexity`: 1-10 scale
- `clarity`: 1-10 scale (how clear is the request)
- `estimated_minutes`: Time estimate
- `state`: Current state
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Abandonment Detection

### Triggers
1. **Context Switch**: User asks about different topic without closing current task
2. **Session End**: Task left in INITIATED or IN_PROGRESS
3. **Timeout**: >30 minutes since SOLUTION_PROVIDED with no update
4. **Explicit**: User says "nevermind", "forget it", "later"

### Detection Code Pattern
```python
def detect_abandonment(task: Task, current_time: datetime) -> bool:
    if task.state == "SOLUTION_PROVIDED":
        if (current_time - task.updated_at).minutes > 30:
            return True
    return False
```

## Intervention Protocol

### Level 1 (0-30 min)
```
📌 Quick check: [task] - still on it?
```

### Level 2 (30-60 min)
```
🔄 I notice [task] from earlier. Pattern: [observation]. Continue or defer?
```

### Level 3 (>60 min)
```
⚠️ ACCOUNTABILITY: [task] started [time] ago. Status? Be honest.
```

## ADHD-Specific Strategies

### Micro-Commitment
"Just step 1? [tiny action] That's it."

### Body Doubling
"Let's do together. You: [action]. Me: ⏱️ Waiting..."

### Chunking
"Step 1 only. Confirm when done."

## Logging to Supabase

All task state changes logged to `tasks` table:
```python
await supabase.table("tasks").insert({
    "task_id": task.id,
    "state": task.state,
    "domain": task.domain,
    "timestamp": datetime.now().isoformat()
})
```

## Forbidden Behaviors

- NEVER let user abandon without acknowledgment
- NEVER ignore context switches
- NEVER skip intervention levels
- NEVER use softening language

## Celebration on Completion

```
✅ Done. Streak: X days
```

Track completion streaks in `task_completion_streaks` table.
