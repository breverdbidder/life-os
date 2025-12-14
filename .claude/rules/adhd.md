# ADHD Task Management Rules

## Task State Transitions

All tasks MUST follow this state machine:

```
INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED
                                           ↘ ABANDONED (detect pattern)
                                           ↘ BLOCKED (external dependency)
                                           ↘ DEFERRED (intentional delay)
```

## Intervention Triggers

1. **Context Switch Detection**
   - User asks about different topic without closing current task
   - Action: Log potential abandonment, ask for closure

2. **Time-Based Intervention**
   - Level 1 (0-30 min): "📌 Quick check: [task] - still on it?"
   - Level 2 (30-60 min): "🔄 Pattern detected. Continue or defer?"
   - Level 3 (>60 min): "⚠️ ACCOUNTABILITY: [task] started [time] ago. Status?"

3. **Session End**
   - Task incomplete when session ends
   - Action: Mark as ABANDONED, log pattern

## ADHD Intervention Strategies

- **Micro-commitment**: "Just step 1? [tiny action] That's it."
- **Body doubling**: "Let's do together. You: [action]. Me: ⏱️ Waiting..."
- **Chunking**: "Step 1 only. Confirm when done."

## Logging Requirements

Every task state change MUST be logged to Supabase `tasks` table with:
- `task_id`
- `state`
- `transition_reason`
- `timestamp`
- `domain` (BUSINESS/MICHAEL/FAMILY/PERSONAL)
