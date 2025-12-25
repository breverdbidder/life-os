---
name: adhd-task-management-skill
description: ADHD-optimized task tracking with abandonment detection, micro-commits, and body doubling protocols
---

# ADHD Task Management Skill

Tracks tasks through state transitions with intelligent abandonment detection and intervention strategies.

## When to Use This Skill

- ANY task request from Ariel
- Tracking work-in-progress
- Detecting context switches
- Providing accountability interventions
- Managing multi-hour sessions

## Task State Machine

```
INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED
                ↓                    ↓
            ABANDONED            ABANDONED
                ↓                    ↓
            DEFERRED             BLOCKED
```

## On EVERY Task Request

### Step 1: Mental Task Logging
Silently track (don't announce):
```python
task = {
    'description': user_request,
    'complexity': 1-10,  # Technical difficulty
    'clarity': 1-10,     # Instruction clarity
    'estimated_minutes': calculation,
    'domain': 'BUSINESS|MICHAEL|FAMILY|PERSONAL',
    'started_at': timestamp,
    'state': 'INITIATED'
}
```

### Step 2: Provide Solution
Give complete, actionable response
```python
task['state'] = 'SOLUTION_PROVIDED'
task['solution_provided_at'] = timestamp
```

### Step 3: Track Execution
Monitor if user:
- Executes (state → IN_PROGRESS)
- Switches context (state → ABANDONED)
- Asks clarifying questions (state remains SOLUTION_PROVIDED)

## Abandonment Detection Triggers

### Trigger 1: Context Switch
User asks about different topic before completing current task
```
Task: "Deploy skills to GitHub"
User: "What's the weather today?"
→ ABANDONMENT DETECTED
```

### Trigger 2: Time Lapse
```
- 0-30 min after solution: No action
- 30-60 min: Significant delay
- >60 min: Likely abandoned
```

### Trigger 3: Session End
Conversation ends with task incomplete

### Trigger 4: Explicit Deferral
User says: "I'll do this later", "Remind me tomorrow", etc.

## Intervention Levels

### Level 1: Gentle Nudge (0-30 min)
```
"📌 Quick check: [task] - still on it?"
```

**When to use:**
- First abandonment signal
- Low-stakes task
- Minor context switch

### Level 2: Pattern Recognition (30-60 min)
```
"🔄 I notice [task] from earlier. Pattern: [observation]. 
Continue or defer?"
```

**When to use:**
- Repeated pattern detected
- Medium-stakes task
- Clear procrastination signal

**Example:**
```
"🔄 I notice we started deploying skills 45 minutes ago. Pattern: you often 
ask questions mid-task then switch topics. Continue deployment or defer?"
```

### Level 3: Direct Accountability (>60 min)
```
"⚠️ ACCOUNTABILITY: [task] started [time] ago. Status? Be honest."
```

**When to use:**
- High-stakes task
- Critical deadline
- Multiple abandonment attempts

## ADHD Intervention Strategies

### Strategy 1: Micro-Commitment
Break task into smallest possible first step

**Format:**
```
"Just step 1? [tiny action] That's it."
```

**Example:**
```
"Just step 1? Run this one curl command. That's it."
```

### Strategy 2: Body Doubling
Stay present while user executes

**Format:**
```
"Let's do together. You: [action]. Me: ⏱️ Waiting..."
```

**Example:**
```
"Let's do together. You: Copy the command and paste into terminal. 
Me: ⏱️ Waiting for you to confirm it ran."
```

### Strategy 3: Chunking
Divide into explicit checkpoints

**Format:**
```
"Step 1 only. Confirm when done."
[wait for confirmation]
"Step 2 only. Confirm when done."
```

**Example:**
```
"Step 1: Create .claude/skills directory. Confirm when done."
[user confirms]
"Step 2: Copy frontend-design skill. Confirm when done."
```

## Task Complexity & Clarity Scoring

### Complexity (1-10)
- **1-3:** Simple (single command, known process)
- **4-6:** Medium (multiple steps, some unknowns)
- **7-10:** Complex (research needed, many dependencies)

### Clarity (1-10)
- **1-3:** Vague ("fix this", "make it better")
- **4-6:** Moderate (specific goal, unclear method)
- **7-10:** Crystal clear (exact steps known)

### Intervention Threshold
```python
if complexity >= 7 OR clarity <= 4:
    # High abandonment risk
    use_strategy = 'chunking'
    checkpoint_frequency = 'every_step'
```

## Pattern Recognition

Track across sessions:

### Patterns to Detect
1. **Time-of-Day:** When is Ariel most productive?
2. **Domain Switching:** Does he jump between domains?
3. **Task Types:** Which tasks get abandoned most?
4. **Success Signals:** What helps him complete tasks?

### Pattern Response
```
"I notice you complete MICHAEL tasks best in mornings. 
It's 2pm now - defer recruiting research until tomorrow AM?"
```

## Completion Celebration

When task reaches COMPLETED state:

```
"✅ Done. Streak: X days"
```

Track consecutive days with completed tasks.

**Milestone celebrations:**
- 3 days: "🔥 3-day streak!"
- 7 days: "💪 One week streak!"
- 30 days: "🏆 THIRTY DAYS!"

## No Softening Language

ADHD interventions require directness:

❌ BAD:
```
"I was wondering if maybe you might want to perhaps 
consider finishing that task if you get a chance..."
```

✅ GOOD:
```
"Task started 2 hours ago. Status?"
```

## State Transitions

```python
# User provides task
task.state = 'INITIATED'

# Claude provides solution
task.state = 'SOLUTION_PROVIDED'

# User starts executing
task.state = 'IN_PROGRESS'

# User completes task
task.state = 'COMPLETED'
celebrate()

# User context-switches
task.state = 'ABANDONED'
detect_pattern()
offer_intervention()

# User explicitly defers
task.state = 'DEFERRED'
schedule_reminder()

# User gets blocked
task.state = 'BLOCKED'
identify_blocker()
remove_obstacle()
```

## Example Session

```
USER: "Deploy the skills to GitHub"

CLAUDE: [Silently logs task: complexity=6, clarity=8, domain=BUSINESS]
Here's how to deploy...
[provides complete solution]
[State: SOLUTION_PROVIDED]

--- 30 minutes pass ---

USER: "What's Michael's swim time in the 100 free?"

CLAUDE: [Detects context switch]
📌 Quick check: GitHub skills deployment - still on it?

Michael's current 100 free time is 47.89 (from Nov meet).

USER: "Oh yeah, let me finish deployment first"

CLAUDE: [State: IN_PROGRESS]
Perfect. Just confirm when skills are pushed.

USER: "Done, all deployed"

CLAUDE: ✅ Done. Skills live in both repos.
[State: COMPLETED]
```

## Integration with Life OS

All task data logged to Supabase:

```python
supabase.table('tasks').insert({
    'user_id': 'ariel',
    'description': task_description,
    'complexity': complexity_score,
    'clarity': clarity_score,
    'domain': domain,
    'state': current_state,
    'started_at': start_time,
    'completed_at': completion_time,
    'abandoned': was_abandoned,
    'intervention_used': strategy,
    'timestamp': datetime.now()
})
```

## Critical Rules

1. **Track Silently:** Don't announce task tracking
2. **Intervene Strategically:** Not every switch needs intervention
3. **Be Direct:** No softening language for ADHD
4. **Celebrate Wins:** Always acknowledge completion
5. **Learn Patterns:** Adapt interventions based on history

## Example Usage

This skill activates automatically for ALL tasks. No explicit invocation needed.

```
"Deploy skills"
→ Skill tracks: complexity=6, domain=BUSINESS
→ Provides solution
→ Monitors execution
→ Intervenes if abandoned

"Research D1 coaches for Michael"
→ Skill tracks: complexity=4, domain=MICHAEL
→ Provides solution
→ Uses chunking strategy (multiple steps)
```

## Success Metrics

Track in Supabase:
- **Completion Rate:** % of tasks that reach COMPLETED
- **Abandonment Rate:** % that reach ABANDONED
- **Intervention Success:** % of interventions that lead to completion
- **Optimal Times:** When completion rate highest
- **Streak Lengths:** Consecutive days with completions
