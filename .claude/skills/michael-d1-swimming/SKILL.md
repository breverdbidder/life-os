---
name: michael-d1-swimming
description: >
  D1 swimming analytics and recruiting tracker for Michael Shapira.
  Use when: (1) analyzing swim times, (2) meet results, (3) time drops,
  (4) rival comparisons, (5) recruiting outreach, (6) nutrition tracking,
  (7) training load, (8) SwimCloud lookups. Events: 50/100/200 Free,
  100 Fly, 100 Back. Diet: Keto Mon-Thu, moderate Fri-Sun (Shabbat).
---

# Michael D1 Swimming

## Overview

Comprehensive tracking system for Michael Shapira's D1 swimming pathway. Combines time analytics, rival monitoring, recruiting pipeline, and kosher-adapted keto nutrition management.

## Athlete Profile

| Attribute | Value |
|-----------|-------|
| Name | Michael Shapira |
| DOB | July 22, 2009 (16 years old) |
| School | Satellite Beach High School |
| Grad Year | 2027 |
| SwimCloud ID | 3250085 |
| Primary Events | 50 Free, 100 Free, 200 Free |
| Secondary Events | 100 Fly, 100 Back |
| Build Target | 6'5-6'6" / 190-205 lbs (Michael Andrew model) |

## Events & Time Standards

### Target Times (D1 Recruitment Interest)

| Event | Current PR | D1 Interest | Power 5 | SEC/Big10 |
|-------|-----------|-------------|---------|-----------|
| 50 Free | TBD | 20.5 | 19.8 | 19.2 |
| 100 Free | TBD | 45.0 | 44.0 | 43.0 |
| 200 Free | TBD | 1:40.0 | 1:38.0 | 1:36.0 |
| 100 Fly | TBD | 50.0 | 48.5 | 47.5 |
| 100 Back | TBD | 51.0 | 49.5 | 48.5 |

### Time Drop Tracking

```python
def calculate_time_drop(old_time: str, new_time: str) -> dict:
    """Calculate improvement between times."""
    old_seconds = parse_time(old_time)
    new_seconds = parse_time(new_time)
    drop = old_seconds - new_seconds
    pct = (drop / old_seconds) * 100
    return {
        "drop_seconds": drop,
        "drop_percentage": pct,
        "significance": "PR" if drop > 0 else "slower"
    }
```

## Verified Rivals

Tracked competitors from SwimCloud:

| Name | SwimCloud ID | PI Score | Primary Event | Notes |
|------|--------------|----------|---------------|-------|
| Soto | 2928537 | 47 | Sprint Free | Key local rival |
| Gordon | 1733035 | 90 | Distance | Strong 200 |
| Domboru | 1518102 | 90 | IM/Back | Versatile |

### Rival Comparison Workflow

1. Pull times from SwimCloud for each rival
2. Compare event-by-event
3. Calculate gap to close
4. Set specific targets

## Recruiting Pipeline

### Target Schools (Tiered)

**Tier 1 (Reach):**
- Florida, Texas, Cal, Stanford
- Requirements: Power 5 times, 3.5+ GPA

**Tier 2 (Match):**
- Florida State, Auburn, Tennessee
- Requirements: D1 Interest times, 3.0+ GPA

**Tier 3 (Safety):**
- UCF, USF, FAU
- Requirements: Current level + improvement trajectory

### Recruiting Timeline

| Date | Action | Status |
|------|--------|--------|
| Sophomore (Current) | Build base, attend camps | IN_PROGRESS |
| Junior Fall | Email coaches, questionnaires | PENDING |
| Junior Winter | Official visits begin | PENDING |
| Junior Spring | Verbal commitments possible | PENDING |
| Senior Fall | National Letter of Intent | PENDING |

### Outreach Tracking

```python
outreach = {
    "school": "University of Florida",
    "coach": "Anthony Nesty",
    "email": "coach@ufl.edu",
    "initial_contact": "2025-09-01",
    "response": None,
    "camp_attended": False,
    "visit_scheduled": None,
    "status": "INITIAL_CONTACT"
}
```

## Nutrition Protocol

### Kosher-Adapted Keto Diet

Based on Michael Andrew's protocol (Olympic swimmer, similar sprint focus):

**Monday - Thursday: Strict Keto**
- Carbs: <30g/day
- Protein: 1.2g/lb body weight
- Fat: Remainder of calories
- Focus: Kosher meats, fish, eggs, nuts, vegetables

**Friday - Sunday: Moderate Carbs (Shabbat)**
- Carbs: 100-150g/day
- Timing: Pre-workout, post-workout, Shabbat meals
- Sources: Challah, potatoes, rice, fruits

### Daily Tracking

```python
nutrition_log = {
    "date": "2025-12-19",
    "day_type": "KETO",  # KETO | SHABBAT
    "meals": [
        {"meal": "breakfast", "items": ["eggs", "avocado"], "carbs": 8},
        {"meal": "lunch", "items": ["grilled chicken", "salad"], "carbs": 5},
        {"meal": "dinner", "items": ["salmon", "broccoli"], "carbs": 10}
    ],
    "total_carbs": 23,
    "keto_compliant": True,
    "training_notes": "AM practice - felt good energy"
}
```

### Macros Target

| Day Type | Carbs | Protein | Fat |
|----------|-------|---------|-----|
| Keto | <30g | 180g | 150g |
| Shabbat | 100-150g | 180g | 100g |

## Training Load Monitoring

### Weekly Structure

| Day | AM Practice | PM Practice | Notes |
|-----|------------|-------------|-------|
| Mon | Technique | Sprint sets | Keto day |
| Tue | Distance | Dryland | Keto day |
| Wed | Race pace | Recovery | Keto day |
| Thu | Starts/turns | Sprint | Keto day |
| Fri | Light | Rest | Shabbat prep |
| Sat | Rest | Rest | Shabbat |
| Sun | Meet or long | Dryland | Carb timing |

### Taper Protocol (Meet Week)

1. Reduce volume 40-50%
2. Maintain intensity
3. Extra sleep (9+ hours)
4. Carb load last 2 days

## Meet Schedule

### Key Meets 2025-2026

| Date | Meet | Location | Events |
|------|------|----------|--------|
| Dec 13-14 | Harry Meisel | TBD | All |
| Jan TBD | District Qualifier | TBD | All |
| Feb TBD | Regionals | TBD | Qualified events |
| Mar TBD | States | TBD | Qualified events |

## SwimCloud Integration

### Data Retrieval

```python
SWIMCLOUD_BASE = "https://www.swimcloud.com"

def get_swimmer_times(swimmer_id: int) -> dict:
    """Fetch times from SwimCloud."""
    url = f"{SWIMCLOUD_BASE}/swimmer/{swimmer_id}"
    # Scrape or API call
    return times_by_event

def compare_to_rival(michael_id: int, rival_id: int) -> dict:
    """Compare times between swimmers."""
    michael_times = get_swimmer_times(michael_id)
    rival_times = get_swimmer_times(rival_id)
    
    comparison = {}
    for event in michael_times:
        if event in rival_times:
            gap = michael_times[event] - rival_times[event]
            comparison[event] = {
                "michael": michael_times[event],
                "rival": rival_times[event],
                "gap": gap,
                "status": "AHEAD" if gap < 0 else "BEHIND"
            }
    return comparison
```

## LangGraph Integration

### State Schema
```python
class SwimState(TypedDict):
    swimmer_id: int
    event: str
    current_pr: float
    target_time: float
    rival_times: dict
    nutrition_today: dict
    training_load: str
    next_meet: dict
```

### Nodes
- `fetch_times` - SwimCloud data retrieval
- `analyze_progress` - Time drop calculation
- `compare_rivals` - Head-to-head analysis
- `log_nutrition` - Daily meal tracking
- `recruiting_status` - Pipeline update

## Scripts

- `scripts/swimcloud_scraper.py` - Time data extraction
- `scripts/rival_comparison.py` - Head-to-head analysis
- `scripts/nutrition_tracker.py` - Keto compliance checker
- `scripts/recruiting_pipeline.py` - Outreach management

## References

- `references/d1_time_standards.md` - Full D1/D2/D3 cut times
- `references/michael_andrew_protocol.md` - Training/nutrition details
- `references/recruiting_calendar.md` - NCAA recruiting rules
