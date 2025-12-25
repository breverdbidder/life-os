---
name: dual-timezone-skill
description: Handle FL/IL timezone conversions with Shabbat awareness and prayer time consciousness
---

# Dual Timezone Skill

Manages dual timezone (Florida/Israel) conversions with religious observance awareness.

## When to Use This Skill

- Displaying times in responses
- Scheduling tasks or events
- Planning meetings across timezones
- Tracking Shabbat/holiday times
- Setting reminders for Michael's swimming

## Primary Timezones

### Florida (Primary)
- **Timezone:** America/New_York (EST/EDT)
- **Current:** Eastern Standard Time (EST)
- **Offset:** UTC-5 (winter), UTC-4 (summer DST)
- **Icon:** 🕐 FL

### Israel (Family/Community)
- **Timezone:** Asia/Jerusalem (IST/IDT)  
- **Current:** Israel Standard Time (IST)
- **Offset:** UTC+2 (winter), UTC+3 (summer DST)
- **Icon:** 🕐 IL

## Display Format

**Always show both when time-relevant:**
```
🕐 FL: 10:00 PM EST (Dec 24) | IL: 5:00 AM IST (Dec 25)
```

**For task scheduling:**
```
Reminder set for:
🕐 FL: 8:00 AM EST Monday | IL: 3:00 PM IST Monday
```

## Shabbat Observance

### Core Rules

**Shabbat Duration:**
- **Starts:** Friday at sundown (18 minutes before sunset)
- **Ends:** Saturday at havdalah (42 minutes after sunset)
- **No Work:** Including no swimming practice/meets

**Michael's Constraint:**
- NO swimming Friday night through Saturday evening
- Must finish practice before Shabbat candles
- Cannot compete in Saturday meets until after havdalah

### Shabbat Time Calculation

```python
# For Brevard County, FL (Satellite Beach)
friday_sunset = get_sunset('Satellite Beach, FL', this_friday)
shabbat_starts = friday_sunset - timedelta(minutes=18)

saturday_sunset = get_sunset('Satellite Beach, FL', this_saturday)  
shabbat_ends = saturday_sunset + timedelta(minutes=42)

# Display format
print(f"Shabbat this week:")
print(f"  Starts: Friday {shabbat_starts.strftime('%I:%M %p EST')}")
print(f"  Ends: Saturday {shabbat_ends.strftime('%I:%M %p EST')}")
```

**Example Output:**
```
Shabbat this week:
  Starts: Friday 5:32 PM EST
  Ends: Saturday 6:28 PM EST
  
⚠️ NO swimming practice Friday 5:32 PM - Saturday 6:28 PM
```

### Holiday Awareness

**Major Holidays (No Work):**
- Rosh Hashanah (2 days)
- Yom Kippur (1 day)
- Sukkot (first 2 days + last 2 days)
- Passover (first 2 days + last 2 days)
- Shavuot (2 days)

**Same Rules as Shabbat:**
- No swimming/practice/meets
- Starts 18 min before sunset
- Ends 42 min after sunset next day

## Prayer Time Consciousness

### Daily Prayer Times (Brevard County)

**Shacharit (Morning):**
- Earliest: Sunrise
- Latest: 4 hours after sunrise
- Typical: 7:00-9:00 AM EST

**Mincha (Afternoon):**
- Earliest: 30 min after solar noon
- Latest: Sunset
- Typical: 5:00-6:00 PM EST

**Maariv (Evening):**
- After nightfall (3 stars visible)
- Typical: 7:00-9:00 PM EST

### Schedule Consideration

```python
# When scheduling tasks
if time_conflicts_with_prayer(scheduled_time):
    suggest_alternative = after_prayer_time(scheduled_time)
    notify_user(f"Note: {scheduled_time} conflicts with prayer. 
                 Suggest {suggest_alternative} instead?")
```

## DST Transitions

**Florida DST:**
- Starts: 2nd Sunday in March (2:00 AM → 3:00 AM)
- Ends: 1st Sunday in November (2:00 AM → 1:00 AM)

**Israel DST:**
- Different schedule than US
- Typically late March - late October
- Exact dates vary by Hebrew calendar

**Time Difference Changes:**
```
Winter (Nov-Mar): FL is UTC-5, IL is UTC+2 → 7 hours difference
Summer (Mar-Nov): FL is UTC-4, IL is UTC+3 → 7 hours difference
Transition periods: May be 6 or 8 hours briefly
```

## Michael's Swim Schedule Integration

### Weekly Schedule Template
```
Monday:
  🕐 FL: 3:30 PM EST - Practice
  🕐 IL: 10:30 PM IST

Tuesday:
  🕐 FL: 3:30 PM EST - Practice
  🕐 IL: 10:30 PM IST

Wednesday:
  🕐 FL: 3:30 PM EST - Practice
  🕐 IL: 10:30 PM IST

Thursday:
  🕐 FL: 3:30 PM EST - Practice
  🕐 IL: 10:30 PM IST

Friday:
  🕐 FL: 3:30 PM EST - Practice (MUST END BEFORE SHABBAT)
  ⚠️ Check Shabbat candle time

Saturday:
  ⛔ NO SWIMMING until after Havdalah
  🕐 Earliest possible: 6:30 PM EST (example)

Sunday:
  🕐 FL: 10:00 AM EST - Practice or Meet
  🕐 IL: 5:00 PM IST
```

### Meet Scheduling Rules

**Cannot Accept:**
- Friday evening meets (after candles)
- Saturday meets (until after havdalah)
- Holiday meets (same rules as Shabbat)

**Template Response:**
```
"Michael observes Shabbat and cannot swim from Friday sundown 
through Saturday evening (havdalah). This week that's Friday 
5:32 PM - Saturday 6:28 PM EST. Can the meet schedule accommodate?"
```

## Timezone Conversion Examples

### Current Time Display
```python
from datetime import datetime
import pytz

fl_tz = pytz.timezone('America/New_York')
il_tz = pytz.timezone('Asia/Jerusalem')

now_utc = datetime.now(pytz.utc)
fl_time = now_utc.astimezone(fl_tz)
il_time = now_utc.astimezone(il_tz)

print(f"🕐 FL: {fl_time.strftime('%I:%M %p %Z (%b %d)')}")
print(f"🕐 IL: {il_time.strftime('%I:%M %p %Z (%b %d)')}")
```

### Event Scheduling
```python
# User says: "Set reminder for 8 AM tomorrow"
fl_tomorrow_8am = datetime.combine(tomorrow, time(8, 0))
fl_aware = fl_tz.localize(fl_tomorrow_8am)
il_time = fl_aware.astimezone(il_tz)

print(f"Reminder set for:")
print(f"  🕐 FL: {fl_aware.strftime('%I:%M %p %Z %A')}")
print(f"  🕐 IL: {il_time.strftime('%I:%M %p %Z %A')}")
```

## Output Templates

### Standard Time Display
```
🕐 FL: [time] [timezone] ([date]) | IL: [time] [timezone] ([date])
```

### Shabbat Notice
```
⚠️ SHABBAT TIMES THIS WEEK:
Candle Lighting: Friday 5:32 PM EST
Havdalah: Saturday 6:28 PM EST

Michael cannot swim during this time.
```

### Meeting Scheduling
```
Proposed meeting:
🕐 FL: Tuesday 2:00 PM EST
🕐 IL: Tuesday 9:00 PM IST

✓ No conflict with Shabbat
✓ No conflict with prayer times
✓ Michael available (after school)
```

## Integration with Life OS

### Task Scheduling
```python
# When creating task with deadline
task_time_fl = parse_user_time(user_input)
task_time_il = convert_to_israel(task_time_fl)

# Check conflicts
if conflicts_with_shabbat(task_time_fl):
    warn_user("Task scheduled during Shabbat")
elif conflicts_with_michael_swim(task_time_fl):
    warn_user("Conflicts with Michael's practice")
```

### Calendar Integration
```python
# Store all times in UTC
# Display in dual format
event = {
    'time_utc': utc_timestamp,
    'time_fl': fl_display,
    'time_il': il_display,
    'shabbat_safe': not conflicts_with_shabbat(utc_timestamp)
}
```

## Example Usage

```
"What time is it now?"
→ 🕐 FL: 10:00 PM EST (Dec 24) | IL: 5:00 AM IST (Dec 25)

"When is Shabbat this week?"
→ Candle lighting: Friday 5:32 PM EST
   Havdalah: Saturday 6:28 PM EST

"Schedule task for tomorrow 8 AM"
→ Task scheduled:
   🕐 FL: 8:00 AM EST Friday
   🕐 IL: 3:00 PM IST Friday

"Can Michael swim Saturday morning?"
→ ⛔ NO - Shabbat until 6:28 PM EST Saturday
```

## Critical Rules

1. **Always Show Both:** FL and IL times when relevant
2. **Shabbat Priority:** Never schedule swimming during Shabbat
3. **Conservative Times:** Use 18 min before / 42 min after sunset
4. **Check Conflicts:** Prayer times, Shabbat, holidays
5. **Clear Icons:** Use 🕐 for time, ⚠️ for warnings, ⛔ for restrictions
