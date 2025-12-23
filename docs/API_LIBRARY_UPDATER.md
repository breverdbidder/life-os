# API Library Auto-Updater

Automated system to keep `API_MEGA_LIBRARY.md` current with new APIs and MCP servers.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Weekly Cron (Sundays 6 AM EST)                             │
│  OR Manual Trigger                                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ Apify     │  │ MCP       │  │ GitHub    │
│ Store     │  │ Registries│  │ Trending  │
│ Scanner   │  │ Scanner   │  │ Scanner   │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Merge & Deduplicate   │
        │  (vs existing library) │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Claude AI Formatter   │
        │  (proper markdown)     │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Create Pull Request   │
        │  for human review      │
        └────────────────────────┘
```

## Sources Scanned

### 1. Apify Store
- **URL:** https://apify.com/store
- **Categories:** real-estate, e-commerce, automation, AI
- **Keywords:** costco, zillow, mls, grocery, scraper, etc.
- **Filter:** Updated in last 30 days

### 2. MCP Server Registries
- **Glama:** https://glama.ai/mcp/servers
- **PulseMCP:** https://www.pulsemcp.com/servers
- **MCP Market:** https://mcpmarket.com
- **GitHub:** awesome-mcp-servers repo

### 3. GitHub Trending
- **Topics:** api, mcp, scraper, automation, real-estate
- **Filter:** Stars > 10, updated in last 90 days

## Schedule

| Trigger | Frequency | Time |
|---------|-----------|------|
| Automatic | Weekly | Sundays 6 AM EST |
| Manual | On-demand | Workflow dispatch |

## Workflow Files

```
.github/workflows/update_api_library.yml
scripts/api_library/
├── scan_apify_store.py
├── scan_mcp_registry.py
├── scan_github_trending.py
├── merge_api_findings.py
└── generate_library_update.py
```

## Manual Trigger

1. Go to GitHub Actions
2. Select "Update API Mega Library"
3. Click "Run workflow"
4. Choose source: `all`, `apify`, `mcp`, or `github`

## Output

- **If new APIs found:** Creates PR with additions
- **If no new APIs:** Logs to Supabase, no PR
- **Always:** Updates `insights` table in Supabase

## PR Review Process

1. Workflow creates PR automatically
2. Human reviews new API additions
3. Check for:
   - Relevance to BidDeed.AI / Life OS
   - Proper categorization
   - No duplicates
4. Merge or close PR

## Secrets Required

| Secret | Purpose |
|--------|---------|
| `ANTHROPIC_API_KEY` | Claude AI for formatting |
| `APIFY_TOKEN` | Apify Store API access |
| `SUPABASE_URL` | Logging |
| `SUPABASE_KEY` | Logging |
| `GITHUB_TOKEN` | Auto-provided |

## Customization

### Add New Categories

Edit `scan_apify_store.py`:

```python
RELEVANT_CATEGORIES = {
    "real-estate": ["real estate", "zillow", ...],
    "your-new-category": ["keyword1", "keyword2"]
}
```

### Add New MCP Sources

Edit `scan_mcp_registry.py`:

```python
MCP_SOURCES = {
    "new_source": {
        "url": "https://...",
        "api": "https://..."
    }
}
```

### Adjust Scan Frequency

Edit workflow cron:

```yaml
schedule:
  # Daily at 6 AM EST
  - cron: '0 11 * * *'
  # Monthly on 1st
  - cron: '0 11 1 * *'
```

---

## Quick Commands

```bash
# Trigger manual scan
gh workflow run update_api_library.yml

# Check last run
gh run list --workflow=update_api_library.yml

# View logs
gh run view <run-id> --log
```

---

*Deployed: December 23, 2025*
*Repos: BidDeed.AI, Life OS*
