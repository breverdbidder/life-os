# Skills System - Security & Discovery

## Overview

This repository implements a **Skills-based AI Agent System** where agents can discover, read, and execute reusable workflows but CANNOT modify them. This ensures consistency, security, and compound learning.

## Architecture

### Skills Directory Structure
```
.claude/skills/
├── adhd-accountability/
│   ├── SKILL.md
│   └── track_task.py
├── supabase-ops/
│   ├── SKILL.md
│   └── insert_data.py
└── smart-router/
    ├── SKILL.md
    └── router_config.json
```

### Security Model

**Locked Directories (READ-ONLY for agents):**
- `.claude/skills/*` - User skills
- `/mnt/skills/public/*` - System skills
- `/mnt/skills/examples/*` - Example skills
- `/mnt/skills/user/*` - User-uploaded skills

**Staging Area (WRITE-ALLOWED):**
- `/tmp/new_skills/` - Temporary skill development
- `/mnt/user-data/outputs/new_skills/` - Skills pending review

**Enforcement:**
- GitHub Actions workflow blocks commits to skills directories
- `validate_skills_security.py` pre-flight checks
- File system permissions in sandbox
- Audit logging to Supabase

## Tools

### 1. Skill Discovery (`discover_skills.py`)

Find and list available skills:

```bash
# List all skills
python tools/discover_skills.py list

# Get JSON output
python tools/discover_skills.py json

# Detailed view
python tools/discover_skills.py detailed

# Get specific skill content
python tools/discover_skills.py get adhd-accountability
```

**Python API:**
```python
from tools.discover_skills import discover_skills, get_skill_content

# List all skills
skills = discover_skills(format="json")

# Get specific skill
content = get_skill_content("supabase-ops")
```

### 2. Security Validation (`validate_skills_security.py`)

Validate operations before execution:

```bash
# Check if path is locked
python tools/validate_skills_security.py --check-path .claude/skills/my-skill

# Validate operation
python tools/validate_skills_security.py --validate write .claude/skills/test.md

# Print security status
python tools/validate_skills_security.py --banner
```

## Usage for AI Agents

### Step 1: Discover Available Skills
```python
# Agent discovers what skills exist
skills_list = discover_skills(format="list")
# Returns formatted list with descriptions
```

### Step 2: Read Skill Content
```python
# Agent reads the skill it needs
skill_content = get_skill_content("max-bid-calculation")
# Returns full SKILL.md with instructions
```

### Step 3: Execute Skill
```python
# Agent follows instructions in SKILL.md
# Executes code/scripts defined in the skill
# CANNOT modify the skill itself
```

### Step 4: Create New Skills (Human Approval Required)
```python
# Agent creates NEW skill in staging area
new_skill_path = "/tmp/new_skills/property-analysis/"
# Writes SKILL.md and scripts
# Logs to insights table for human review
# Human manually moves to .claude/skills/ after approval
```

## Benefits

1. **Token Efficiency:** First run explores (expensive), subsequent runs reuse (cheap)
2. **Consistency:** Same workflows produce same output structure
3. **Security:** Agents can't corrupt trusted skills
4. **Compound Learning:** Each solved workflow becomes reusable building block
5. **Audit Trail:** All skill access logged to Supabase

## Examples

### BidDeed.AI Skills
- `max-bid-calculation` - Foreclosure auction bid calculation
- `lien-discovery` - Auto-search AcclaimWeb for liens
- `hoa-analysis` - Detect HOA foreclosures with senior mortgage survival
- `report-generation` - One-page DOCX auction reports

### Life OS Skills
- `adhd-accountability` - Task abandonment detection
- `michael-d1-swimming` - Competitive swim tracking
- `youtube-transcript` - 4-tier transcript extraction
- `supabase-ops` - Database operations

## Configuration

Edit `.skillsrc` to customize:
- Locked paths
- Allowed operations
- Staging areas
- Audit settings

## Workflows

### GitHub Actions
- `.github/workflows/skills_security.yml` - Enforces read-only on PR/push
- Blocks any commits that modify `.claude/skills/*`
- Logs violations to Supabase insights table

### Pre-flight Validation
Run before agent execution:
```bash
python tools/validate_skills_security.py --banner
```

## Troubleshooting

**Q: Agent says "permission denied" when trying to save skill**  
A: This is correct behavior. Agent must use staging area (`/tmp/new_skills/`)

**Q: How do I add a new skill?**  
A: 
1. Create in `/tmp/new_skills/your-skill/`
2. Add SKILL.md + scripts
3. Test thoroughly
4. Get human review
5. Human manually moves to `.claude/skills/`

**Q: Can I disable security temporarily?**  
A: No. This is a hard security boundary. Use staging area for experimentation.

## Roadmap

- [ ] Skill versioning system
- [ ] Automated testing framework for skills
- [ ] Skill marketplace/sharing between repos
- [ ] Performance metrics per skill (token usage, success rate)
- [ ] Skill dependency management

## References

- [Anthropic Skills Spec](https://github.com/anthropics/skills)
- [OpenAI Skills Discussion](https://platform.openai.com/docs/guides/skills)
- YouTube: "Skills for AI Agents" (tTZ4yDY4adg)

---

**Last Updated:** 2025-12-24  
**Maintainer:** Ariel Shapira / BidDeed.AI
