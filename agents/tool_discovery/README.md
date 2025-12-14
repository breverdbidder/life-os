# Agentic Tool Discovery System

Dynamic MCP server discovery, token economics tracking, and skill extraction for BidDeed.AI.

## Architecture

Based on cutting-edge agentic patterns:
1. **Dynamic Tool Discovery** - Vector-indexed tool search replacing static API_MEGA_LIBRARY.md
2. **Token Economics Tracking** - Measure exploration (76K tokens) vs production (8K tokens) for ROI proof
3. **Skill Extraction** - Convert successful Claude.ai sessions into frozen GitHub Actions workflows

## The Pattern

```
Exploration Phase (expensive, flexible)
    ↓ Claude.ai chat discovers & combines tools
    ↓ ~76,000 tokens per run
    ↓ 
Skill Extraction (one-time)
    ↓ Analyze successful patterns
    ↓ Generate frozen workflow
    ↓
Production Phase (cheap, reliable)
    ↓ GitHub Actions workflow
    ↓ ~8,000 tokens per run
    ↓ 10x cost reduction
```

## Components

### 1. Tool Index (`src/tool_index/`)
- Supabase pgvector for semantic search
- ~2,000 MCP server descriptions indexed
- Query: "find foreclosure auction data" → Returns top 3 relevant tools

### 2. Token Tracker (`src/token_tracker/`)
- Log token usage per workflow
- Compare exploration vs production phases
- Track Smart Router V5 tier distribution (target: 40-55% FREE)

### 3. Skill Extractor (`src/skill_extractor/`)
- Analyze chat conversations for repeated patterns
- Generate GitHub Actions YAML from successful workflows
- Deploy frozen skills directly to repo

## Usage

### Discover Tools
```python
from src import discover_tools

# Semantic search for relevant tools
tools = await discover_tools("analyze property liens and mortgages")
# Returns: [acclaimweb_lien_search, lien_priority_analyzer, ...]
```

### Track Token Economics
```python
from src import TokenUsage, log_token_usage, compare_exploration_vs_production

# Log exploration run
usage = TokenUsage(
    workflow_id="beca-2024-12-14",
    workflow_name="BECA Daily Scrape",
    phase="exploration",
    model="claude-sonnet-4-5",
    input_tokens=45000,
    output_tokens=31000,
    tool_calls=12
)
await log_token_usage(usage)

# Compare phases
comparison = await compare_exploration_vs_production("BECA Daily Scrape")
# Returns: {token_reduction: "89%", skill_extraction_roi: "ACHIEVED"}
```

### Extract & Deploy Skill
```python
from src import extract_and_deploy_skill

# Convert successful pattern to frozen workflow
result = await extract_and_deploy_skill(
    skill_name="beca-daily-scrape",
    description="Scrape BECA for foreclosure data daily at 6 AM EST",
    tool_sequence=[
        {"name": "beca_scraper", "params": {"date": "today"}},
        {"name": "lien_priority_analyzer", "params": {}},
        {"name": "decision_logger", "params": {}}
    ],
    input_schema={"auction_date": {"type": "string", "required": True}},
    trigger_patterns=["run BECA", "scrape foreclosures"]
)
# Creates: .github/workflows/skill-beca-daily-scrape.yml
```

## Setup

### 1. Initialize Supabase Tables
```bash
python scripts/init_tables.py
# Copy output SQL to Supabase SQL Editor
```

### 2. Seed Tool Index
```bash
export SUPABASE_KEY="your-key"
python scripts/seed_tools.py
```

### 3. Deploy via GitHub Actions
```bash
# Push to trigger deployment
git push origin main

# Or manual trigger with table init
gh workflow run deploy_tool_discovery.yml -f init_tables=true -f seed_tools=true
```

## ROI Measurement

This system proves the "Agentic AI ecosystem" valuation model:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Token reduction | 90% (10x) | `compare_exploration_vs_production()` |
| FREE tier usage | 40-55% | `get_smart_router_metrics()` |
| Cost per workflow | <$0.01 production | Token economics log |

## Integration with BidDeed.AI

- **BECA V22**: Exploration → Frozen workflow achieving 10x reduction
- **Smart Router V5**: Tracks FREE tier distribution
- **12-Stage Pipeline**: Each stage = potential frozen skill

## Files

```
agentic-tool-discovery/
├── src/
│   ├── tool_index/
│   │   └── vector_store.py      # pgvector MCP discovery
│   ├── token_tracker/
│   │   └── economics.py         # Token usage & ROI
│   └── skill_extractor/
│       └── extractor.py         # Chat → workflow pipeline
├── scripts/
│   ├── init_tables.py           # Supabase setup
│   └── seed_tools.py            # Index BidDeed tools
├── .github/workflows/
│   └── deploy_tool_discovery.yml
└── requirements.txt
```

## Source

Based on agentic architecture patterns from MCP + Agency Swarm research (Dec 2025).
Implements: Dynamic tool discovery, programmatic orchestration, development→production pipeline.
