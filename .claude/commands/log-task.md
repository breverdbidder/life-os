---
description: Log a new task with ADHD tracking
allowed-tools:
  - Write
  - Bash
argument-hint: <task description>
---

# Log Task Command

Log a new task with ADHD-optimized tracking.

## Process

1. Parse task description from $ARGUMENTS
2. Assess complexity (1-10)
3. Determine domain (BUSINESS/MICHAEL/FAMILY/PERSONAL)
4. Estimate time
5. Set initial state to INITIATED
6. Log to Supabase tasks table

## Output

```
📋 Task Logged
━━━━━━━━━━━━━━
Task: $ARGUMENTS
Complexity: [1-10]
Domain: [domain]
Est. Time: [minutes]
State: INITIATED

Starting now...
```

Then immediately provide solution to move to SOLUTION_PROVIDED state.
