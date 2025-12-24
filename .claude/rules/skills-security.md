# Skills Security & Discovery Rules

## Core Principle
Skills directories are **READ-ONLY** for all agents. Agents can discover, read, and execute skills but CANNOT modify them.

## Locked Directories
- `.claude/skills/*` (all subdirectories)
- `/mnt/skills/public/*`
- `/mnt/skills/examples/*`
- `/mnt/skills/user/*`

## Required Workflow

### Before Complex Tasks
1. **DISCOVER SKILLS FIRST**
   ```python
   from tools.discover_skills import discover_skills
   skills = discover_skills(format="list")
   ```
   - Search for relevant skills before writing new code
   - Reuse existing skills when available
   - Only create new code if no skill exists

### When Skill Exists
2. **READ SKILL CONTENT**
   ```python
   from tools.discover_skills import get_skill_content
   content = get_skill_content("skill-name")
   ```
   - Follow instructions in SKILL.md
   - Execute scripts defined in the skill
   - Maintain consistency with skill patterns

### Creating New Skills
3. **STAGING AREA ONLY**
   - New skills MUST go to: `/tmp/new_skills/` or `/mnt/user-data/outputs/new_skills/`
   - NEVER write to `.claude/skills/` directly
   - Log new skill creation to Supabase insights table
   - Human will review and manually move to production

## Security Violations

### FORBIDDEN Operations
- ❌ Writing to `.claude/skills/*`
- ❌ Deleting from `.claude/skills/*`
- ❌ Modifying files in `.claude/skills/*`
- ❌ Creating files in `.claude/skills/*`
- ❌ Renaming in `.claude/skills/*`

### ALLOWED Operations
- ✅ Reading SKILL.md files
- ✅ Executing scripts from skills
- ✅ Listing skills directory
- ✅ Creating skills in staging area

## Pre-flight Check
Before ANY file write operation that could affect skills directories:
```python
from tools.validate_skills_security import validate_operation
is_valid, error = validate_operation("write", filepath)
if not is_valid:
    raise SecurityError(error)
```

## Enforcement
- GitHub Actions blocks PR/pushes to skills directories
- `validate_skills_security.py` enforces at runtime
- File system permissions in sandbox
- All violations logged to Supabase

## Examples

### ✅ CORRECT: Discover and Use Skill
```python
# Step 1: Discover
skills = discover_skills()
# Finds "max-bid-calculation" skill exists

# Step 2: Read
content = get_skill_content("max-bid-calculation")
# Gets SKILL.md instructions

# Step 3: Execute
# Follow instructions, run scripts, produce output
```

### ❌ INCORRECT: Direct Modification
```python
# This will FAIL security check
with open('.claude/skills/my-skill/SKILL.md', 'w') as f:
    f.write("new content")  # BLOCKED
```

### ✅ CORRECT: Create New Skill
```python
# Step 1: Create in staging
staging_path = Path("/tmp/new_skills/property-valuation")
staging_path.mkdir(parents=True, exist_ok=True)

# Step 2: Write SKILL.md
(staging_path / "SKILL.md").write_text(skill_content)

# Step 3: Log for review
# Insert to Supabase insights: category='new_skill', path=staging_path
```

## Benefits of This System

1. **Token Efficiency**
   - First exploration: 76K tokens
   - Reusing skill: 8K tokens (10x reduction)

2. **Consistency**
   - Same skill = same output structure
   - No random variations between runs

3. **Security**
   - Agents can't corrupt trusted workflows
   - All modifications require human review

4. **Compound Learning**
   - Each solved workflow becomes reusable
   - Agents get better over time, not reset each run

## Skill Discovery Pattern

When starting ANY complex task:
1. Call `discover_skills()` to see what exists
2. Search for relevant keywords in skill descriptions
3. If skill found → read and execute it
4. If no skill → write code, then save to staging for review

## Audit Logging

All skill-related operations are logged:
```python
{
  "category": "skills",
  "subcategory": "discovery|execution|creation|violation",
  "insight": {
    "skill_name": "...",
    "operation": "...",
    "result": "..."
  }
}
```

## Emergency Override

There is NO emergency override. If agents genuinely need to modify a skill:
1. Create improved version in staging
2. Log rationale to insights
3. Human reviews and approves
4. Human manually replaces old skill

This ensures NO automated corruption of trusted skills.

---

**Remember:** Skills are the foundation of compound learning. Protect them.
