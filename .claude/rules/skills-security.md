# Skills Directory Security Policy

## Read-Only Directories
The following directories are **PERMANENTLY READ-ONLY** for all agents:
- `/mnt/skills/public/` - Official Anthropic skills
- `/mnt/skills/examples/` - Example skills  
- `/mnt/skills/private/` - Private skills (if exists)
- `/mnt/skills/user/` - User-created skills

## Agent Permissions
✅ **ALLOWED:**
- Read skill files (SKILL.md, scripts, resources)
- Execute skill scripts in sandbox
- Call discover_skills tool to list available skills
- Create NEW skills in `/home/claude/proposed_skills/` for human review

❌ **FORBIDDEN:**
- Modify existing skills
- Delete skill files
- Override skill logic
- Write to `/mnt/skills/` directory tree

## Skill Modification Process
If an agent needs to update a skill:
1. Generate improved skill in `/home/claude/proposed_skills/[skill_name]_v2/`
2. Create comparison document showing changes
3. Surface to Ariel for review and approval
4. Human manually moves approved skill to `/mnt/skills/user/`

## Security Enforcement
- File system: `/mnt/skills/` mounted as read-only in container
- Claude rules: Pre-action verification prevents writes
- Audit: All skill reads logged to Supabase `skill_usage` table

## Violation Response
If agent attempts to modify skills:
1. Block the operation immediately
2. Log violation to `insights` table
3. Alert: "SECURITY: Agent attempted to modify read-only skills directory"
4. Terminate current task

---
**Last Updated:** 2024-12-24
**Owner:** Ariel Shapira
**Enforcement:** Automated via filesystem + Claude rules
