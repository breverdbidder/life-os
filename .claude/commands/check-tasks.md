---
description: Review current task states and detect abandoned tasks
allowed-tools: Bash, Read
argument-hint: [domain or "all"]
---

# Check Tasks - ADHD Accountability

## Arguments
- `all` - All domains
- `business` - BidDeed.AI, Insurance
- `michael` - Michael D1 swimming
- `family` - Family commitments
- `personal` - Health, learning

## Task State Summary

Review current conversation for:
1. **INITIATED**: Tasks mentioned but not started
2. **SOLUTION_PROVIDED**: Claude gave solution, waiting on execution
3. **IN_PROGRESS**: User working on task
4. **ABANDONED**: Context switched without closure

## Intervention Check

### 0-30 min since solution:
```
📌 Quick check: [task] - still on it?
```

### 30-60 min since solution:
```
🔄 Pattern alert: [task] from earlier.
This is context switch #[N] today.
Continue or defer?
```

### >60 min since solution:
```
⚠️ ACCOUNTABILITY: [task] started [X] ago.
Status? Be honest with yourself.
```

## Current Session Tasks

Review this conversation for any:
- Unanswered questions from user
- Solutions provided without confirmation
- Topics started but not concluded

## Patterns to Track

- Abandonment rate by domain
- Time-of-day productivity
- Context switch frequency
- Completion streaks

## Daily Summary Format

```
📊 Task Summary - !`date +%Y-%m-%d`

COMPLETED: [X]
IN_PROGRESS: [Y]
ABANDONED: [Z]
DEFERRED: [W]

Streak: [N] days

Top Pattern: [observation]
```

## Force Closure

If session ending with open tasks:
```
⚠️ SESSION CHECK

Open tasks detected:
1. [Task 1] - State: [state]
2. [Task 2] - State: [state]

For each, choose:
- COMPLETE (mark done)
- DEFER (schedule for later)
- ABANDON (acknowledge dropping)
```
