---
description: Quick status overview of all Life OS domains
allowed-tools: Bash, Read
---

# Life OS Status Dashboard

## Time
🕐 FL: !`TZ=America/New_York date +"%I:%M %p %Z"`
🕐 IL: !`TZ=Asia/Jerusalem date +"%I:%M %p %Z"`

## Today
📅 !`date +"%A, %B %d, %Y"`

## Shabbat Check
!`python3 -c "
from datetime import datetime
import calendar
now = datetime.now()
day = calendar.day_name[now.weekday()]
if day == 'Friday':
    print('🕯️ Shabbat begins at sunset')
elif day == 'Saturday':
    print('🕯️ Shabbat - No work tasks')
else:
    print('📅 Regular day')
"`

## Domain Status

### 🏢 BUSINESS
- BidDeed.AI: Check brevard-bidder-scraper repo
- Next auction: Check calendar

### 🏊 MICHAEL D1
- SwimCloud ID: 3250085
- Next meet: Harry Meisel Dec 13-14

### 👨‍👩‍👦 FAMILY
- Orthodox observance active
- Check family calendar

### 🧠 PERSONAL
- ADHD tracking: Active
- Learning sessions: Check insights

## GitHub Actions
!`gh run list --limit=3 2>/dev/null || echo "gh CLI not configured"`

## Energy Pattern
| Time | Level | Best For |
|------|-------|----------|
| 9-11 AM | Peak | Complex tasks |
| 2-4 PM | Dip | Learning/admin |
| Evening | Family | No work |

## Quick Actions
- `/log` - Log insight to Supabase
- `/michael` - Michael swim data
- `/check-tasks` - ADHD accountability
