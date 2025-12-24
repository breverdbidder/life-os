# LIFO RULE - Last In First Out Task Execution

## Rule Definition
**ALWAYS resume from the last command/task state. NEVER start from scratch.**

## Implementation

### 1. Task Stack Tracking
```python
# Store in PROJECT_STATE.json or memory
task_stack = [
    {
        "id": "task_003",
        "command": "Convert top 3 stages to skills",
        "status": "IN_PROGRESS",
        "timestamp": "2025-12-24T18:30:00Z",
        "context": {
            "top_3_stages": ["lien_priority", "report_gen", "max_bid"],
            "baseline_data": "dec3_auction_baseline_analysis.md",
            "skills_created": []
        }
    },
    {
        "id": "task_002",
        "command": "Run reports on previous auctions",
        "status": "COMPLETED",
        "timestamp": "2025-12-24T18:25:00Z",
        "output": "dec3_auction_baseline_analysis.md"
    },
    {
        "id": "task_001",
        "command": "Deploy Jan 7 2026 metrics workflow",
        "status": "COMPLETED",
        "timestamp": "2025-12-24T18:15:00Z"
    }
]
```

### 2. Resume Protocol

**When user says "Resume" or "Continue":**

```python
def resume():
    # Get last task from stack
    current_task = task_stack[-1]  # LIFO - Last In First Out
    
    if current_task['status'] == 'IN_PROGRESS':
        # Resume from where we left off
        context = current_task['context']
        
        # Example: If creating skills
        if current_task['command'] == 'Convert top 3 stages to skills':
            remaining_skills = [
                s for s in context['top_3_stages'] 
                if s not in context['skills_created']
            ]
            
            # Continue with next skill
            create_skill(remaining_skills[0])
    else:
        # Last task completed, what's next?
        print(f"Last task completed: {current_task['command']}")
        print("What's next?")
```

### 3. State Persistence

**After EVERY action:**
```python
def update_task_state(task_id, updates):
    # Update PROJECT_STATE.json
    task = find_task(task_id)
    task.update(updates)
    save_to_project_state(task)
    
    # Update memory
    update_memory(f"Task {task_id}: {updates}")
```

### 4. Anti-Pattern Detection

**NEVER do this:**
```python
# ❌ BAD - Starting from scratch
def handle_request(user_message):
    if "create skills" in user_message:
        # Start fresh skill creation
        create_all_skills_from_beginning()
```

**ALWAYS do this:**
```python
# ✅ GOOD - Resume from state
def handle_request(user_message):
    if "resume" in user_message.lower() or "continue" in user_message.lower():
        current_state = load_current_state()
        resume_from(current_state)
    else:
        # New request - but still check if related to existing task
        related_task = find_related_in_progress_task(user_message)
        if related_task:
            resume_from(related_task)
        else:
            start_new_task(user_message)
```

## Triggers for LIFO Resume

1. User says: "Resume", "Continue", "Keep going"
2. User references last task: "Finish that", "Complete the skills"
3. User asks about status: "Where are we?"
4. New session starts - check for IN_PROGRESS tasks

## Current State Check

**Before starting ANY task:**
```python
# Check task stack
in_progress = [t for t in task_stack if t['status'] == 'IN_PROGRESS']

if in_progress:
    print(f"⚠️  Found in-progress task: {in_progress[-1]['command']}")
    print(f"   Started: {in_progress[-1]['timestamp']}")
    print(f"   Resuming...")
    resume_task(in_progress[-1])
else:
    # Safe to start new task
    start_new_task()
```

## Integration with Memory

**Memory format:**
```
Task Stack (LIFO):
- [IN_PROGRESS] Convert top 3 stages to skills (2025-12-24 18:30)
  - lien_priority: PENDING
  - report_gen: PENDING  
  - max_bid: PENDING
  
- [COMPLETED] Run reports on previous auctions (2025-12-24 18:25)
  - Output: dec3_auction_baseline_analysis.md
  
- [COMPLETED] Deploy Jan 7 2026 workflow (2025-12-24 18:15)
```

## Deployment to Both Repos

This LIFO rule should be added to:
- `.claude/rules/lifo-resume.md` (BrevardBidder)
- `.claude/rules/lifo-resume.md` (Life OS)

## Example Usage

**User:** "Resume"

**Claude checks stack:**
```
Last task: Convert top 3 stages to skills
Status: IN_PROGRESS
Created: 0/3 skills
Next: Create lien_priority skill
```

**Claude action:**
```python
# Don't ask, just execute
create_lien_priority_skill()
create_report_gen_skill()
create_max_bid_skill()
deploy_all_skills()
generate_savings_report()
```

**Claude response:**
"✅ Resumed skill creation. Created 3 skills and deployed. Savings: $424/year."

NOT: "Want me to create skills?" ❌

## Critical Rules

1. **NEVER ask what to do next** - check the stack and resume
2. **NEVER start from scratch** - always check for in-progress tasks
3. **ALWAYS update state** - after every action
4. **Pop completed tasks** - move to history, keep stack clean

## State File Format

**PROJECT_STATE.json:**
```json
{
  "task_stack": [...],
  "current_task_id": "task_003",
  "last_checkpoint": "2025-12-24T18:30:00Z",
  "execution_mode": "autonomous"
}
```

---

**Status:** DEFINED - Ready to deploy to both repos
