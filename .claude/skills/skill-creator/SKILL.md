---
name: skill-creator
description: Guide for creating effective skills that extend Claude's capabilities with specialized knowledge
---

# Skill Creator

Interactive guide for building custom Claude skills.

## When to Use
- Creating skills for repetitive workflows
- Codifying domain-specific knowledge
- Building team skill libraries
- Documenting best practices as skills

## Development Process

### 1. Identify Use Cases (3-5 examples)
```
Examples:
- "Calculate max bid for foreclosure property"
- "Search AcclaimWeb for lien records"
- "Parse BCPAO GIS data"
```

### 2. Analyze Patterns
What's reusable?
- Common data sources
- Repeated calculations
- Standard workflows
- Reference docs needed

### 3. Determine Contents

**SKILL.md** (required): Instructions Claude follows

**scripts/** (optional): Python/bash executables
- Clear names: `calculate_max_bid.py`
- Include docstrings
- Handle errors

**references/** (optional): Documentation
- API schemas
- Business rules
- Regulations

**assets/** (optional): Templates, logos
- HTML boilerplate
- Brand assets
- Example files

### 4. Write SKILL.md Structure

```yaml
---
name: skill-name
description: Clear 1-2 sentence description
---

# Skill Name

Detailed purpose and capabilities.

## When to Use This Skill
- Use case 1
- Use case 2

## Instructions
1. First step
2. Second step
3. Final step

## Examples
Show inputs/outputs

## Best Practices
- Guideline 1
- Guideline 2
```

### 5. Keep Minimal

**DO NOT CREATE:**
- README files
- Setup docs
- Testing procedures
- Auxiliary context

**Only include what Claude needs.**

## Design Principles
1. Single responsibility
2. Self-contained
3. Discoverable (good name/description)
4. Tested scripts
5. Minimal files

## Testing
1. Place in `.claude/skills/`
2. Start new conversation
3. Reference: "Use [skill] to..."
4. Verify discovery
5. Check outputs

## Example Usage
```
"Use skill creator to build a Supabase integration skill"
"Help me create foreclosure lien analysis skill"
```
