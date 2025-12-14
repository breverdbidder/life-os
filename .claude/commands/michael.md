---
description: Quick access to Michael's swimming data and recruiting status
allowed-tools: Bash, Read, Glob
argument-hint: [times|rivals|recruiting|nutrition]
---

# Michael D1 Quick Access

## Arguments
- `times` - View recent times and PBs
- `rivals` - Compare against verified rivals
- `recruiting` - Check recruiting status
- `nutrition` - Today's nutrition plan

## Michael Profile
- **SwimCloud ID**: 3250085
- **Age**: 16 (Class 2027)
- **Events**: 50/100/200 Free, 100 Fly, 100 Back

## Commands

### View Times
```bash
cat src/michael_d1_agents_v3/data/personal_bests.json 2>/dev/null || echo "Data not loaded"
```

### Rival Comparison
```
Verified Rivals:
- Soto (2928537) - PI: 47
- Gordon (1733035) - PI: 90
- Domboru (1518102)
```

### Recruiting Status
```bash
cat src/michael_d1_agents_v3/data/recruiting_tracker.json 2>/dev/null || echo "No recruiting data"
```

### Today's Nutrition
```
Day: !`date +%A`

Mon-Thu: Strict Keto (<20g carbs)
Fri-Sun: Moderate Carbs (Shabbat)
```

## Quick Stats
!`cat src/michael_d1_agents_v3/data/summary.json 2>/dev/null | head -20 || echo "Load data with michael-d1 agent"`

## Next Meet
Check data directory for upcoming meets.
