# Supabase Integration Rules

## Connection Details

- **Host**: mocerqjnksmhcjzxrewo.supabase.co
- **Service Role Key**: Use GitHub Actions secrets

## Tables

| Table | Purpose |
|-------|---------|
| `tasks` | ADHD task tracking |
| `activities` | Activity logging |
| `insights` | AI insights (learning, michael_swim, health_log, claude_performance) |
| `daily_metrics` | Productivity metrics |
| `michael_swim_times` | Swim performance |
| `michael_nutrition` | Diet tracking |
| `michael_recruiting` | D1 outreach |
| `family_events` | Calendar events |
| `task_interventions` | ADHD intervention logs |
| `abandonment_patterns` | Pattern analysis |

## Insert Pattern

NEVER use local curl. Always use GitHub Actions workflow:

```bash
gh workflow run insert_insight.yml \
  -f category=learning \
  -f data='{"topic": "...", "takeaways": [...]}'
```

## Categories for insights table

- `learning` - Educational content captures
- `michael_swim` - Swimming updates
- `health_log` - Health tracking
- `claude_performance` - AI performance scoring

## Query Pattern

For read operations, use the Supabase REST API with appropriate headers.
