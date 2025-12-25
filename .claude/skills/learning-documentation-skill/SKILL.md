---
name: learning-documentation-skill
description: Document learnings to Supabase insights table with proper categorization and markdown formatting
---

# Learning Documentation Skill

Systematically captures and stores learning insights to Supabase for future reference.

## When to Use This Skill

- After completing YouTube transcript analysis
- Documenting new technical knowledge
- Recording Michael's swim training insights
- Capturing MCP/architecture patterns
- Any "aha moment" worth preserving

## Supabase Integration

### Insert Pattern (GitHub Actions Workflow)

**Workflow:** `insert_insight.yml`

**Trigger via API:**
```python
requests.post(
    "https://github.com/breverdbidder/life-os/actions/workflows/insert_insight.yml/dispatches",
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    },
    json={
        "ref": "main",
        "inputs": {
            "category": category,
            "subcategory": subcategory,
            "title": title,
            "content": json.dumps(content_object)
        }
    }
)
```

**Direct Workflow Execution:**
```bash
# GitHub Actions workflow handles Supabase insert
# No local curl commands needed
```

## Category Structure

### Category: learning
**Subcategories:**
- `technical` - Programming, APIs, tools
- `business` - Strategy, operations, finance
- `health` - Michael's swimming, nutrition, training
- `personal` - Family, productivity, ADHD

**Example:**
```json
{
  "category": "learning",
  "subcategory": "technical",
  "title": "Claude Skills Progressive Disclosure Architecture",
  "content": {
    "concept": "Skills load in stages: ~100 tokens metadata scan, <5k full content when relevant",
    "source": "YouTube video analysis",
    "key_insight": "Massive token savings vs Claude rules (which load every prompt)",
    "application": "Use skills for BidDeed.AI foreclosure workflows"
  }
}
```

### Category: youtube_transcript
**Subcategories:**
- `education` - Tutorials, how-tos
- `business` - Entrepreneurship, strategy
- `technical` - Coding, AI, engineering
- `michael` - Swimming technique, training

**Example:**
```json
{
  "category": "youtube_transcript",
  "subcategory": "technical",
  "title": "6 Essential Claude Skills for Development",
  "content": {
    "video_id": "thxXGxYIwUI",
    "url": "https://youtu.be/thxXGxYIwUI",
    "key_points": [
      "Frontend design skill eliminates AI slop",
      "Skill creator for building custom skills",
      "Domain brainstormer saves hours searching",
      "Content writer matches your voice + citations",
      "Lead research finds customers + outreach",
      "Stripe integration done right first time"
    ],
    "homework": "Build Supabase skill using skill-creator",
    "date_watched": "2025-12-25"
  }
}
```

### Category: mcp_reference
**Subcategories:**
- `architecture` - MCP design patterns
- `integration` - Tool implementations
- `claude_skills` - Skills documentation
- `best_practices` - Standards, conventions

**Example:**
```json
{
  "category": "mcp_reference",
  "subcategory": "claude_skills",
  "title": "Skills vs MCP Servers - When to Use Each",
  "content": {
    "skills_use_when": "Task-specific workflows, repeatable processes, domain expertise",
    "mcp_use_when": "External API integration, real-time data, tool actions",
    "complementary": "Skills can use MCP servers as tools",
    "example": "Foreclosure-analysis-skill (workflow) uses Supabase MCP (data)"
  }
}
```

### Category: michael_swim
**Subcategories:**
- `training` - Workout plans, technique
- `nutrition` - Diet, supplements, timing
- `recruiting` - D1 contacts, programs
- `meets` - Race results, analysis

**Example:**
```json
{
  "category": "michael_swim",
  "subcategory": "training",
  "title": "Sprint Freestyle Technique Notes - Dec 2025",
  "content": {
    "focus_areas": ["high elbow catch", "explosive turns", "underwaters"],
    "model": "Michael Andrew technique videos",
    "progress": "100 free: 47.89 → targeting sub-47.0",
    "next_meet": "Harry Meisel Dec 13-14",
    "rivals": {
      "soto": "PI 47",
      "gordon": "PI 90"
    }
  }
}
```

## Markdown Formatting Standards

### Headers
Use proper markdown hierarchy:
```markdown
# Main Title (H1)
## Section (H2)
### Subsection (H3)
```

### Lists
```markdown
**Unordered:**
- Item 1
- Item 2
  - Sub-item

**Ordered:**
1. First
2. Second
3. Third
```

### Code Blocks
```markdown
**Inline:** `variable_name`

**Block:**
```python
def function():
    return "formatted"
```\`\`\`
```

### Links
```markdown
[Link Text](https://url.com)
```

### Emphasis
```markdown
**Bold text**
*Italic text*
`code inline`
```

## Content Structure Best Practices

### For Technical Learning
```json
{
  "concept": "What is it?",
  "why_important": "Why does it matter?",
  "how_works": "Technical explanation",
  "use_cases": ["When to use"],
  "example": "Concrete example",
  "gotchas": ["Common mistakes"],
  "source": "Where learned"
}
```

### For Business Insights
```json
{
  "insight": "Core takeaway",
  "context": "Situation/background",
  "application": "How to apply to BidDeed.AI",
  "roi_estimate": "Expected value",
  "next_steps": ["Action items"]
}
```

### For Michael's Swimming
```json
{
  "date": "2025-12-25",
  "event": "100 Free",
  "time": "47.89",
  "meet": "Meet name",
  "analysis": "What went well/poorly",
  "technique_focus": "Areas to improve",
  "next_goal": "Target time"
}
```

## Automation Triggers

Auto-document when:

### YouTube Transcript Complete
```python
# After youtube_transcript.yml completes
learning_documentation_skill.insert({
    'category': 'youtube_transcript',
    'subcategory': determine_type(video_content),
    'title': video_title,
    'content': extract_key_learnings(transcript)
})
```

### New Claude Skill Created
```python
# After deploying custom skill
learning_documentation_skill.insert({
    'category': 'mcp_reference',
    'subcategory': 'claude_skills',
    'title': f"{skill_name} Documentation",
    'content': skill_metadata
})
```

### Michael's Meet Results
```python
# After swim meet
learning_documentation_skill.insert({
    'category': 'michael_swim',
    'subcategory': 'meets',
    'title': f"{meet_name} - {date}",
    'content': race_results_analysis
})
```

## Example Workflow

```python
# Step 1: Identify learning moment
learning = {
    'category': 'learning',
    'subcategory': 'technical',
    'title': 'Supabase Row-Level Security Best Practices'
}

# Step 2: Structure content
learning['content'] = {
    'concept': 'RLS policies control data access per user',
    'key_insight': 'Enable RLS on ALL tables, even internal ones',
    'gotcha': 'Policies apply to service role too unless using security definer',
    'application': 'BidDeed.AI auction_results table needs RLS',
    'source': 'Supabase docs + trial/error',
    'date': '2025-12-25'
}

# Step 3: Trigger GitHub Actions workflow
# Workflow inserts to Supabase insights table

# Step 4: Verify insertion
# Check Supabase UI or query insights table
```

## Query Examples

Find past learnings:

```sql
-- Recent technical learnings
SELECT title, content
FROM insights
WHERE category = 'learning' 
  AND subcategory = 'technical'
ORDER BY created_at DESC
LIMIT 10;

-- Michael's swim progress
SELECT title, content->'time' as time
FROM insights  
WHERE category = 'michael_swim'
  AND subcategory = 'meets'
ORDER BY created_at DESC;

-- All YouTube transcripts
SELECT title, content->'url' as video_url
FROM insights
WHERE category = 'youtube_transcript'
ORDER BY created_at DESC;
```

## Example Usage

```
"Use learning-documentation-skill to log today's Claude skills learnings"

"Document Michael's 100 free improvement to Supabase"

"Record MCP architecture pattern we just discovered"
```

## Integration Points

- Triggers after YouTube transcript completion
- Logs after custom skill deployment
- Records Michael's meet results
- Captures technical discoveries
- Preserves business insights

## Critical Rules

1. **Always Use Workflow:** Never local curl to Supabase
2. **Structured Content:** Use JSON objects, not plain text
3. **Proper Categories:** Follow category/subcategory standards
4. **Markdown Format:** Use proper headers, lists, code blocks
5. **Searchable:** Make content easy to query later
