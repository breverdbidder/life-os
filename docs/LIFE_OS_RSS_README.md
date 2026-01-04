# Life OS RSS Automation System

**Zero Human-in-the-Loop ADHD Intervention System**

Automatically monitors Life OS tasks and triggers interventions when tasks are ABANDONED or BLOCKED.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      LIFE OS RSS AUTOMATION                      │
└─────────────────────────────────────────────────────────────────┘

Supabase (task_states table)
    ↓
GitHub Actions (every 30min)
    ↓
RSS Exporter (life_os_rss_exporter.py)
    ↓
RSS Feed (public/rss.xml)
    ↓
Cloudflare Pages (life-os-aiy.pages.dev/rss.xml)
    ↓
Make.com (RSS watcher)
    ↓
    ├── Discord Webhook (alerts)
    └── Supabase (life_os_interventions table)
```

## Components

### 1. RSS Exporter (`life_os_rss_exporter.py`)
- **Function**: Fetches ABANDONED/BLOCKED tasks from Supabase
- **Output**: RSS 2.0 XML feed + JSON summary
- **Filter**: Last 24 hours only
- **Location**: Root directory

### 2. GitHub Actions Workflow (`.github/workflows/rss_generator.yml`)
- **Schedule**: Every 30 minutes (`*/30 * * * *`)
- **Actions**:
  - Fetch latest tasks from Supabase
  - Generate RSS feed
  - Commit to repository
  - Auto-deploy to Cloudflare Pages
- **Cost**: $0 (GitHub Actions free tier)

### 3. Make.com Workflow (`make_com_workflow_template.json`)
- **Trigger**: RSS feed watch (30min intervals)
- **Filter**: Business domain tasks only
- **Actions**:
  1. Send Discord alert to #accountability
  2. Log intervention to Supabase
  3. Detect high abandonment patterns (>3/day)
  4. Send escalation alert if pattern detected
- **Cost**: $0 (Make.com free tier: 1,000 ops/month, uses ~720/month)

### 4. Supabase Schema (`supabase_migration_interventions.sql`)
- **Table**: `life_os_interventions`
- **Views**: 
  - `daily_intervention_summary` - Daily stats
  - `intervention_patterns` - ADHD pattern insights
- **Features**: RLS enabled, auto-timestamps, analytics

## Setup Instructions

### Step 1: Deploy Supabase Schema

```bash
# Run migration in Supabase SQL Editor
psql -h db.mocerqjnksmhcjzxrewo.supabase.co \
     -U postgres \
     -f supabase_migration_interventions.sql
```

Or copy/paste `supabase_migration_interventions.sql` into Supabase SQL Editor.

### Step 2: Configure GitHub Actions

1. Add GitHub secret:
   - Name: `SUPABASE_KEY`
   - Value: Your Supabase service role key

2. Push files to repository:
```bash
git add life_os_rss_exporter.py
git add .github/workflows/rss_generator.yml
git commit -m "Add Life OS RSS automation"
git push
```

3. Verify workflow runs:
   - Go to Actions tab
   - Check "Life OS RSS Feed Generator" workflow
   - Manually trigger first run

### Step 3: Create Discord Webhook

1. In Discord:
   - Go to #accountability channel settings
   - Integrations → Webhooks → New Webhook
   - Name: "Life OS Alerts"
   - Copy webhook URL

### Step 4: Import Make.com Workflow

1. Open Make.com → Scenarios → Import
2. Upload `make_com_workflow_template.json`
3. Replace placeholders:
   - `YOUR_DISCORD_WEBHOOK_URL_HERE` → Your Discord webhook (2 places)
   - `YOUR_SUPABASE_KEY_HERE` → Your Supabase service role key (2 places)
4. Activate scenario
5. Test with "Run once" button

### Step 5: Verify End-to-End

1. Create test ABANDONED task in Supabase:
```sql
INSERT INTO task_states (
    session_id, task_id, description, domain, 
    complexity, clarity, estimated_minutes, 
    status, initiated_at, updated_at
) VALUES (
    'test_session', 'test_abandoned', 
    'Test abandoned task for RSS automation', 
    'BUSINESS', 5, 5, 30, 
    'ABANDONED', NOW(), NOW()
);
```

2. Wait 30 minutes OR manually trigger GitHub Action

3. Check RSS feed:
   - URL: https://life-os-aiy.pages.dev/rss.xml
   - Should contain test task

4. Check Discord:
   - Should receive alert in #accountability

5. Check Supabase:
```sql
SELECT * FROM life_os_interventions 
WHERE task_id = 'test_abandoned';
```

## RSS Feed URL

**Public URL**: https://life-os-aiy.pages.dev/rss.xml

**Query Parameters**:
- None (feed auto-filters ABANDONED/BLOCKED from last 24 hours)

**Feed Format**: RSS 2.0 with Atom namespace

**Update Frequency**: Every 30 minutes

## Make.com Workflow Details

### Free Tier Limits
- **Operations/month**: 1,000
- **Estimated usage**: 720 (48 checks/day × 30 days)
- **Buffer**: 280 operations remaining

### Workflow Branches

**Branch 1: Individual Task Alerts**
```
RSS Feed → Filter (BUSINESS) → Discord Alert → Supabase Log
```

**Branch 2: Pattern Detection**
```
RSS Feed → Count Interventions → Filter (>3) → High Abandonment Alert
```

### Alert Examples

**Individual Alert**:
```
🚨 ADHD Intervention Required

Task: ⚠️ ABANDONED: Build BidDeed.AI zoning analyzer

Details:
Task: Build BidDeed.AI zoning analyzer
Status: ABANDONED
Domain: BUSINESS
Complexity: 8/10
Started: 2026-01-04T10:30:00
Duration Since Start: 2 hours

Action Required: @ariel Please address this abandoned task

Direct Link: https://life-os-aiy.pages.dev?task=task_20260104_103000
```

**Pattern Alert** (>3 abandonments):
```
⚠️ HIGH ABANDONMENT ALERT

@ariel You've abandoned 5 tasks today.

Pattern Detection: This indicates potential ADHD overwhelm or task clarity issues.

Recommended Actions:
1. Review task complexity ratings
2. Break down large tasks into micro-commits
3. Consider body doubling for next task
4. Check focus score and energy levels
```

## Analytics Queries

### Daily Summary
```sql
SELECT * FROM daily_intervention_summary 
WHERE intervention_date = CURRENT_DATE;
```

### Open Interventions
```sql
SELECT task_description, triggered_at, 
       AGE(NOW(), triggered_at) as time_open
FROM life_os_interventions 
WHERE resolution_status = 'OPEN'
ORDER BY triggered_at DESC;
```

### ADHD Patterns (Last 30 Days)
```sql
SELECT * FROM intervention_patterns;
```

### High Abandonment Days
```sql
SELECT intervention_date, 
       SUM(intervention_count) as total_interventions
FROM daily_intervention_summary
GROUP BY intervention_date
HAVING SUM(intervention_count) > 3
ORDER BY intervention_date DESC;
```

### Resolve Intervention
```sql
UPDATE life_os_interventions
SET resolution_status = 'RESOLVED',
    resolved_at = NOW(),
    resolution_notes = 'Task completed after intervention'
WHERE task_id = 'task_20260104_103000';
```

## Costs

| Component | Cost |
|-----------|------|
| GitHub Actions | $0 (free tier) |
| Cloudflare Pages | $0 (free tier) |
| Supabase Pro | Already paying |
| Make.com | $0 (free tier: 1,000 ops/month) |
| **TOTAL** | **$0/month** |

## Monitoring

### GitHub Actions Status
- Check: https://github.com/breverdbidder/life-os/actions
- Workflow: "Life OS RSS Feed Generator"
- Frequency: Every 30 minutes

### Make.com Execution History
- Dashboard: https://www.make.com/en/executions
- Scenario: "Life OS ADHD Intervention Monitor"
- Check: Operations used vs limit

### Supabase Logs
```sql
-- Today's interventions
SELECT COUNT(*) FROM life_os_interventions 
WHERE DATE(triggered_at) = CURRENT_DATE;

-- Last 24 hours activity
SELECT * FROM life_os_interventions 
WHERE triggered_at >= NOW() - INTERVAL '24 hours'
ORDER BY triggered_at DESC;
```

## Troubleshooting

### RSS Feed Not Updating
1. Check GitHub Actions logs
2. Verify SUPABASE_KEY secret exists
3. Manually trigger workflow
4. Check Supabase task_states table has ABANDONED tasks

### Discord Alerts Not Sending
1. Verify Discord webhook URL in Make.com
2. Check webhook permissions in Discord
3. Test webhook with curl:
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"content": "Test alert"}'
```

### Make.com Not Triggering
1. Check scenario is activated
2. Verify RSS feed URL is correct
3. Check free tier operation limits
4. Review execution history for errors

### Supabase Log Failures
1. Verify SUPABASE_KEY in Make.com
2. Check life_os_interventions table exists
3. Test with manual INSERT
4. Review Supabase logs

## Future Enhancements

- [ ] SMS alerts via Twilio for critical abandonments
- [ ] Slack integration for team visibility
- [ ] ML-based abandonment prediction
- [ ] Auto-suggest task breakdowns for complex tasks
- [ ] Integration with calendar for time-blocking suggestions
- [ ] Gamification: Achievement badges for completion streaks

## License

MIT - Part of Life OS ecosystem

## Author

Ariel Shapira - Solo Founder, BidDeed.AI / Everest Capital USA

**Last Updated**: 2026-01-04
