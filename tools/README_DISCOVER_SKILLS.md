# Discover Skills Tool

## Purpose
Allows agents to discover and select appropriate skills **before** executing complex workflows. This prevents token waste and improves task accuracy.

## Architecture
```
/mnt/skills/
├── public/          # Official Anthropic skills (READ-ONLY)
├── examples/        # Example skills (READ-ONLY)
├── user/           # User-created skills (READ-ONLY)
└── private/        # Private skills if exists (READ-ONLY)
```

## Usage

### Command Line
```bash
# List all skills
python3 tools/discover_skills.py

# Search for specific skills
python3 tools/discover_skills.py "docx"
python3 tools/discover_skills.py "presentation"

# Get JSON output
python3 tools/discover_skills.py "" "json"
```

### Python API
```python
from tools.discover_skills import SkillDiscovery, discover_skills

# Method 1: High-level function
result = discover_skills()  # All skills
result = discover_skills("spreadsheet")  # Search
result = discover_skills(format="json")  # JSON output

# Method 2: Class-based API
discovery = SkillDiscovery()
all_skills = discovery.list_all()
results = discovery.search("foreclosure")
skill = discovery.get_by_id("docx")
```

### GitHub Actions Workflow
```yaml
name: Discover Skills
on:
  workflow_dispatch:
    inputs:
      query:
        description: 'Search query (optional)'
        required: false
        type: string

jobs:
  discover:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: List Skills
        run: python3 tools/discover_skills.py "${{ github.event.inputs.query }}"
```

## Agent Integration Pattern

### Before Task Execution
```python
# 1. Agent receives task
task = "Create a foreclosure auction report"

# 2. Search for relevant skills
discovery = SkillDiscovery()
skills = discovery.search("report")

# 3. Agent selects best skill
# Output: "Found skill: 'pdf' - PDF Processing Guide"

# 4. Read the skill
with open(skills[0]['skill_file']) as f:
    skill_instructions = f.read()

# 5. Execute workflow using skill
# ... agent follows skill instructions ...
```

## Skill Metadata Structure
```json
{
  "name": "DOCX creation, editing, and analysis",
  "skill_id": "docx",
  "category": "public",
  "description": "Comprehensive document creation...",
  "path": "/mnt/skills/public/docx",
  "skill_file": "/mnt/skills/public/docx/SKILL.md"
}
```

## When to Use

✅ **USE discover_skills when:**
- Starting a complex workflow (docs, spreadsheets, presentations)
- Task mentions specific output types (PDF, DOCX, PPTX, XLSX)
- User requests automation of multi-step processes
- Unsure which skill to use

❌ **DON'T use discover_skills for:**
- Simple one-shot tool calls
- Tasks with no relevant skills available
- When you already know the exact skill needed

## Performance Benefits

### Token Savings
- **Before:** Load all 16 skills in context (~50K tokens)
- **After:** List skills (2K tokens) → Read 1 skill (3-5K tokens)
- **Savings:** ~90% reduction in context usage

### Accuracy Improvement
- Agent sees all options before choosing
- Prevents wrong skill selection
- Reduces trial-and-error iterations

## Security

The tool has **READ-ONLY** access to `/mnt/skills/`. Agents cannot:
- Modify existing skills
- Delete skills
- Override skill logic
- Write to skills directories

See `.claude/rules/skills-security.md` for full security policy.

## Examples

### Example 1: Document Creation
```python
# Agent task: "Create a professional report"
skills = discover_skills("document")
# Returns: docx skill
# Agent reads /mnt/skills/public/docx/SKILL.md
# Executes workflow using python-docx
```

### Example 2: Presentation Building
```python
# Agent task: "Build a deck about Q4 results"
skills = discover_skills("presentation")
# Returns: pptx skill
# Agent reads /mnt/skills/public/pptx/SKILL.md
# Executes workflow using pptxgenjs
```

### Example 3: Data Analysis
```python
# Agent task: "Analyze foreclosure auction data"
skills = discover_skills("spreadsheet")
# Returns: xlsx skill
# Agent reads /mnt/skills/public/xlsx/SKILL.md
# Creates Excel with formulas and charts
```

## Future Enhancements

1. **Skill Usage Analytics**
   - Log which skills are called most often
   - Track success/failure rates
   - Store in Supabase `skill_usage` table

2. **Smart Recommendations**
   - ML model suggests skills based on task text
   - "Users who ran X also used Y"

3. **Version Control**
   - Track skill versions
   - Allow agents to request specific versions
   - Rollback if new version fails

4. **Skill Composition**
   - Combine multiple skills for complex workflows
   - Example: pptx + xlsx = presentation with embedded data

---

**Last Updated:** 2024-12-24  
**Deployed:** life-os, brevard-bidder-scraper  
**Dependencies:** Python 3.11+, pathlib, re, json
