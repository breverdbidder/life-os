# Life OS - Supabase Integration Workflow
## Version 1.0.0 | Updated: 2025-12-07
### Created by: Ariel Shapira, Solo Founder - Everest Capital of Brevard LLC

---

## 🔄 SUPABASE INTEGRATION PATTERN

**CRITICAL: Never use local curl for Supabase inserts.** Keys are stored securely in GitHub Actions secrets.

---

## 📤 INSERT WORKFLOW

### Workflow Location
`.github/workflows/insert_insight.yml` in `brevard-bidder-scraper` repo

### Trigger Command

```bash
GITHUB_TOKEN="$GITHUB_TOKEN"

curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/breverdbidder/brevard-bidder-scraper/actions/workflows/insert_insight.yml/dispatches" \
  -d '{
    "ref": "main",
    "inputs": {
      "title": "Your Title",
      "description": "Detailed description",
      "insight_type": "learning|task_completion|claude_performance",
      "source": "life_os"
    }
  }'
```

---

## 📊 INSIGHT TYPES FOR LIFE OS

| Type | Use Case | Example |
|------|----------|---------|
| `learning` | YouTube, articles, podcasts | "Keto adaptation for swimmers" |
| `task_completion` | ADHD task tracking | "Completed tax optimization review" |
| `claude_performance` | Achievement/mistake logs | "Successfully debugged pipeline" |
| `michael_swim` | Swimming progress | "New 100 Free PR: 52.3" |
| `health_log` | Personal health tracking | "Sleep: 7.5hrs, Energy: 8/10" |

---

## 🗄️ SUPABASE TABLES (Life OS)

**Project:** `mocerqjnksmhcjzxrewo`

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `activities` | Task tracking, checkpoints | activity_type, status, created_at |
| `tasks` | ADHD task management | description, complexity, clarity |
| `daily_metrics` | Productivity tracking | focus_score, energy, tasks_completed |
| `insights` | Claude logs, learnings | insight_type, title, description |
| `michael_swim_times` | Swimming progress | event, time, meet_date |
| `michael_nutrition` | Keto tracking | date, carbs, protein, fat |

---

## ✅ WORKFLOW BENEFITS

1. **Secure** - Keys never exposed in Claude sessions
2. **Auditable** - GitHub Actions provides run history
3. **Portable** - Works from any Claude instance
4. **Reliable** - GitHub handles retries and failures

---

## 🔗 CROSS-REPO INTEGRATION

Life OS shares the Supabase instance with BidDeed.AI:
- Same database: `mocerqjnksmhcjzxrewo`
- Same workflow trigger pattern
- Different insight_types for separation

---

*This document syncs with BidDeed.AI CLOUD_ECOSYSTEM_ARCHITECTURE.md*
