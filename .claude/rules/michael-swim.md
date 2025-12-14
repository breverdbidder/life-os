---
paths: src/michael_d1_agents_v3/**/*.py
---

# Michael D1 Swimming Rules - Life OS

## Athlete Profile

| Field | Value |
|-------|-------|
| Name | Michael Shapira |
| DOB | July 22, 2009 |
| Age | 16 |
| School | Satellite Beach HS |
| Class | 2027 |
| SwimCloud ID | 3250085 |

## Primary Events

| Event | Priority | Target |
|-------|----------|--------|
| 50 Free | High | D1 qualifying |
| 100 Free | High | D1 qualifying |
| 200 Free | Medium | Versatility |
| 100 Fly | Medium | Secondary |
| 100 Back | Medium | Secondary |

## Verified Rivals (Track These)

| Name | SwimCloud ID | Power Index | Notes |
|------|--------------|-------------|-------|
| Soto | 2928537 | 47 | Primary rival |
| Gordon | 1733035 | 90 | Strong competitor |
| Domboru | 1518102 | - | Watch for improvement |

## Data Sources

- **SwimCloud**: Primary timing data
- **Meet Results**: Manual entry when needed
- **Supabase**: `michael_swim_times` table

## Time Format Standards

```python
# Always store times in seconds
time_seconds = 23.45  # For 50 Free

# Display format: MM:SS.ss or SS.ss
def format_time(seconds: float) -> str:
    if seconds >= 60:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}:{secs:05.2f}"
    return f"{seconds:.2f}"
```

## Recruiting Tracking

### D1 Program Tiers
1. **Power 5**: Top programs (reach schools)
2. **Mid-Major D1**: Realistic targets
3. **D1 Low**: Safety schools

### Outreach Logging
```python
{
    "school": "University of Florida",
    "coach_name": "Anthony Nesty",
    "contact_date": "2025-12-13",
    "method": "email",
    "response": "pending",
    "notes": "Sent intro with times"
}
```

## Nutrition Protocol (Michael Andrew Model)

### Weekday (Mon-Thu): Strict Keto
- High fat, moderate protein, very low carb
- Target: <20g net carbs/day
- Focus: Mental clarity, sustained energy

### Weekend (Fri-Sun): Moderate Carbs
- Shabbat observance allows carbs
- Target: 100-150g carbs/day
- Focus: Glycogen replenishment

### Reference Athlete
- Michael Andrew: 6'5-6'6", 190-205 lbs
- Similar sprint focus (50/100 Free)
- Keto-adapted training

## Meet Calendar

Track upcoming meets:
```python
{
    "meet_name": "Harry Meisel Invitational",
    "dates": ["2025-12-13", "2025-12-14"],
    "location": "TBD",
    "events_entered": ["50 Free", "100 Free"]
}
```

## Performance Logging

Every time entry to Supabase:
```python
await supabase.table("michael_swim_times").insert({
    "event": "50 Free",
    "time_seconds": 23.45,
    "meet_name": "Harry Meisel",
    "date": "2025-12-13",
    "is_personal_best": True,
    "notes": "Negative split"
})
```
