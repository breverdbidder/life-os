# 🚀 GTD System Deployment Guide

## Overview
This deploys the complete Getting Things Done (GTD) system into your Life OS, integrating with existing Supabase infrastructure.

## Files Created
1. `gtd_schema.sql` - Complete database schema with tables, views, functions
2. `gtd.html` - Main GTD interface (conversational AI-powered)
3. `DEPLOYMENT.md` - This file

## Deployment Steps

### 1. Deploy Database Schema

**Option A: Via Supabase SQL Editor** (Recommended)
```bash
# 1. Go to: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql
# 2. Click "New Query"
# 3. Paste contents of gtd_schema.sql
# 4. Click "Run"
```

**Option B: Via Supabase CLI**
```bash
# Install Supabase CLI if not installed
npm install -g supabase

# Link to project
supabase link --project-ref mocerqjnksmhcjzxrewo

# Run migration
supabase db push --file gtd_schema.sql
```

### 2. Get API Keys

You need two keys:

**A. Supabase Anon Key**
```bash
# Get from: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/settings/api
# Copy "anon public" key
```

**B. Anthropic API Key**
```bash
# Already in your environment: ANTHROPIC_API_KEY
# Or from: https://console.anthropic.com/settings/keys
```

### 3. Update gtd.html with Keys

Edit gtd.html and replace:
```javascript
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY'; // Line ~155
// Replace with your actual Supabase anon key

'x-api-key': 'YOUR_ANTHROPIC_API_KEY', // Line ~225
// Replace with your actual Anthropic API key
```

### 4. Deploy to GitHub

```bash
# Clone your life-os repo
cd ~/projects
git clone https://github.com/breverdbidder/life-os.git
cd life-os

# Copy files
cp /path/to/gtd.html ./gtd.html
cp /path/to/gtd_schema.sql ./schema/gtd_schema.sql
cp /path/to/DEPLOYMENT.md ./docs/GTD_DEPLOYMENT.md

# Commit
git add .
git commit -m "Deploy GTD agentic system to Life OS"
git push origin main
```

### 5. Deploy to Cloudflare Pages

Your existing Cloudflare Pages setup will auto-deploy:
- URL: https://life-os-aiy.pages.dev/gtd.html
- Trigger: Any push to main branch in GitHub

**Verify deployment:**
```bash
# Wait 2-3 minutes after git push, then:
curl -I https://life-os-aiy.pages.dev/gtd.html
# Should return 200 OK
```

### 6. Link from Main Life OS

Add GTD link to your main Life OS dashboard:

Edit `index.html` or `chat.html`:
```html
<a href="/gtd.html" class="nav-link">
  🎯 GTD System
</a>
```

## Database Schema Overview

### Core Tables
- `gtd_inbox` - Unprocessed captures
- `gtd_next_actions` - Single-step tasks with contexts
- `gtd_projects` - Multi-step outcomes
- `gtd_waiting_for` - Delegated items
- `gtd_someday` - Future possibilities
- `gtd_calendar` - Time/date specific
- `gtd_reference` - Information storage
- `gtd_contexts` - Work contexts (@computer, @phone, etc.)
- `gtd_reviews` - Review tracking
- `gtd_triggers` - Prompt questions for weekly review

### Key Views
- `v_gtd_health` - System health metrics

### Functions
- `complete_next_action(uuid)` - Mark action complete
- `process_inbox_item(uuid, text, jsonb)` - Route inbox item to appropriate list

## Initial Data

The schema automatically seeds:
- **8 default contexts**: @computer, @phone, @home, @office, @errands, @anywhere, @pool, @low_energy
- **10 trigger questions**: Customized for your 4 domains (BUSINESS, MICHAEL, FAMILY, PERSONAL)

## Testing

### 1. Verify Schema Deployed
```sql
-- Run in Supabase SQL Editor
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'gtd_%';
-- Should return 10 tables
```

### 2. Check Default Data
```sql
SELECT * FROM gtd_contexts;
-- Should show 8 contexts

SELECT * FROM gtd_triggers;
-- Should show 10 trigger questions
```

### 3. Test Health View
```sql
SELECT * FROM v_gtd_health;
-- Should return all zeros (empty system)
```

### 4. Test Capture
```sql
INSERT INTO gtd_inbox (content, source) 
VALUES ('Test capture from deployment', 'manual');

SELECT * FROM v_gtd_health;
-- inbox_count should now be 1
```

### 5. Test Web Interface
```bash
# Open in browser
open https://life-os-aiy.pages.dev/gtd.html

# Try commands:
# - "brain dump"
# - "show my lists"
# - "what should I do now"
```

## Integration with Existing Life OS

### ADHD Tracking
GTD system integrates with your existing ADHD tracking:
- `energy_level` field on actions (HIGH/MEDIUM/LOW)
- `estimated_minutes` for time management
- Context-based filtering reduces decision fatigue

### Dual Timezone Support
- All timestamps are in UTC (Supabase default)
- Display layer can convert to FL (EST) or IL (IST)
- Shabbat-aware: `@low_energy` context for Friday prep

### Domain Integration
All GTD items tagged with domain:
- `BUSINESS` - BidDeed.AI, foreclosures
- `MICHAEL` - Swimming, recruiting
- `FAMILY` - Shabbat, holidays
- `PERSONAL` - Health, learning

### Existing Tables
GTD system is **additive** - doesn't modify existing tables:
- `activities` table remains unchanged
- Can optionally link GTD actions to activities for unified tracking

## Maintenance

### Daily (5 minutes)
```sql
-- Check inbox
SELECT COUNT(*) FROM gtd_inbox WHERE processed = FALSE;

-- Review health
SELECT * FROM v_gtd_health;
```

### Weekly (60-90 minutes)
Use the "weekly review" command in the interface. It will guide you through:
1. Process all inbox items
2. Review all projects
3. Check waiting fors
4. Review someday/maybe
5. Plan next week

### Monthly
```sql
-- Archive completed projects
UPDATE gtd_projects 
SET status = 'ARCHIVED' 
WHERE status = 'COMPLETED' 
AND completed_at < NOW() - INTERVAL '30 days';

-- Review someday items
SELECT * FROM gtd_someday 
WHERE last_reviewed IS NULL 
OR last_reviewed < CURRENT_DATE - INTERVAL '30 days';
```

## Troubleshooting

### Issue: Can't see GTD tables
```bash
# Verify deployment
psql postgresql://[connection-string] -c "\dt gtd_*"
# Or use Supabase Table Editor in dashboard
```

### Issue: API calls failing
- Check API keys are correct in gtd.html
- Check browser console for errors (F12)
- Verify CORS is enabled on Supabase (should be by default)

### Issue: Cloudflare Pages not updating
```bash
# Check deployment status
# Go to: https://dash.cloudflare.com/[account]/pages/life-os-aiy
# Look for latest deployment

# Force redeploy if needed
git commit --allow-empty -m "Force redeploy GTD"
git push origin main
```

### Issue: Supabase rate limits
- Free tier: 500 requests/second
- If hitting limits, consider upgrading to Pro ($25/mo)
- Or add caching layer with localStorage

## Next Steps

After deployment:

1. **Initial Setup** (30 min)
   - Run "brain dump" command
   - Capture everything on your mind
   - Process inbox items

2. **First Week** (daily 5 min)
   - Daily review each morning
   - Capture items as they come up
   - Complete actions from lists

3. **First Weekly Review** (Sunday night, 60-90 min)
   - Full system review
   - Establish review habit
   - Adjust contexts/workflows as needed

4. **Iterate** (ongoing)
   - Add custom contexts if needed
   - Refine trigger questions
   - Integrate with other Life OS modules

## Architecture Notes

### Why This Design?

**Agentic vs Traditional App:**
- No rigid UI - conversational interface
- AI interprets natural language
- Dynamic workflow adaptation
- Context-aware recommendations

**Database-Backed:**
- All state persists in Supabase
- Can query/analyze via SQL
- Integrates with other Life OS data
- Backup/restore via Supabase

**Claude API Integration:**
- Real-time GTD coaching
- Understands your personal context
- Enforces GTD methodology
- Adapts to your ADHD needs

### Cost Estimate

**Supabase:**
- Database: Free tier OK for single user
- API calls: ~500/day = well within limits

**Anthropic API:**
- ~10 messages/day = 40K tokens/day
- Sonnet 4: $3/1M tokens input, $15/1M output
- Est cost: ~$0.50/day = $15/month
- Included in your Claude Max subscription

**Total:** $0/month extra (covered by existing subscriptions)

## Support

- GTD Methodology: https://gettingthingsdone.com/
- Supabase Docs: https://supabase.com/docs
- Claude API: https://docs.anthropic.com/
- Life OS Issues: breverdbidder/life-os GitHub issues

---

**Deployment Status:** ⏳ Ready to deploy
**Estimated Time:** 20 minutes
**Difficulty:** Low (mostly copy/paste)
**Dependencies:** Supabase, Cloudflare Pages, Anthropic API

Let's get things done! 🎯
