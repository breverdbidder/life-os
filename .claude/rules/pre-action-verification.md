# Pre-Action Verification Rule

## BEFORE ANY ACTION:

```
1. READ target file first (never assume content)
2. VERIFY endpoint/API exists (curl test)  
3. CHECK Supabase for prior attempts
THEN execute.
```

## Decision Routing Matrix

| Decision Type | Auto-Execute | Surface to Ariel |
|--------------|--------------|------------------|
| Code deploy (tests pass) | ✅ | ❌ |
| New API integration | ❌ | ✅ |
| Supabase schema change | ❌ | ✅ |
| Bug fix (<50 lines) | ✅ | ❌ |
| Workflow modification | ✅ | ❌ |
| Spend >$10 | ❌ | ✅ |
| File creation | ✅ | ❌ |
| Web search | ✅ | ❌ |

## Checkpoint Format (SHORT)

```
STATE: [task_id] [status] → [next_action]
```

Examples:
- `STATE: beca_scraper COMPLETED → deploy auction_data_legitimate.yml`
- `STATE: schema_update IN_PROGRESS → verify migration`
- `STATE: api_integration BLOCKED → awaiting Ariel approval`

## Verification Workflow

```python
# Before modifying any file:
result = verifier.run_verification(
    task_id="task_name",
    target_file="path/to/file",
    endpoint="https://api.example.com"  # if applicable
)

if not result["verified"]:
    # STOP - do not proceed
    print(f"BLOCKED: {result['block_reason']}")
```

## Never Auto-Execute

- New external API integrations
- Database schema changes
- Any spend over $10
- Actions that failed 3+ times previously
