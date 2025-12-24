# Skills Directory Security Rules

## Core Principle
**Agents can USE skills but CANNOT modify the skills directory.**

## Protected Directories (READ-ONLY)
The following directories are **READ-ONLY** for all agents:

```
/mnt/skills/public/     - Core Anthropic skills
/mnt/skills/private/    - Private skills (if exists)
/mnt/skills/examples/   - Example skills
```

## Enforcement Rules

### ✅ ALLOWED Operations
- Read any skill file via `view` tool
- Execute code from skills
- Call `discover_skills` tool to list available skills
- Reference skill instructions in prompts
- Copy skill code to working directory (/home/claude) for modification

### ❌ FORBIDDEN Operations
- Create files in /mnt/skills/*
- Modify existing files in /mnt/skills/*
- Delete files from /mnt/skills/*
- Move/rename files in /mnt/skills/*
- Change permissions on /mnt/skills/*

## Violation Response
If agent attempts to modify /mnt/skills/:
1. Operation will fail (filesystem protection)
2. Agent must acknowledge: "Skills directory is read-only"
3. Agent must copy skill to /home/claude/ if modification needed
4. Modified skill goes to /home/claude/ or /mnt/user-data/outputs/

## New Skill Creation
When agent develops a new skill:
1. Create in /home/claude/new-skills/
2. Test thoroughly
3. If successful, notify user: "New skill ready for review at [path]"
4. User manually reviews and moves to /mnt/skills/user/ (if that directory exists)

## Skill Discovery
Before executing complex workflows, agent MUST:
1. Call `discover_skills` tool
2. Check if relevant skill exists
3. Read skill with `view` tool if found
4. Follow skill instructions

## Rationale
- **Security:** Prevents agents from overwriting trusted workflows
- **Reproducibility:** Skills remain stable across runs
- **Version Control:** All skill changes go through review
- **Debugging:** Clear separation between agent exploration and production skills

## Integration with Pre-Action Verification
This rule is part of the pre-action verification system. Before any file operation in /mnt/skills/, agent must verify it's a read operation only.
