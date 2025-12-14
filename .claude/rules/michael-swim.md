# Michael D1 Swimming Rules

## Data Sources

- **SwimCloud ID**: 3250085
- **Verified Rivals**: 
  - Soto: 2928537 (PI 47)
  - Gordon: 1733035 (PI 90)
  - Domboru: 1518102

## Target Events

| Event | Current | Target | Notes |
|-------|---------|--------|-------|
| 50 Free | Track | D1 standards | Sprint focus |
| 100 Free | Track | D1 standards | Primary event |
| 200 Free | Track | D1 standards | Endurance |
| 100 Fly | Track | D1 standards | Secondary |
| 100 Back | Track | D1 standards | Secondary |

## Diet Protocol

### Monday - Thursday (Strict Keto)
- Follow Michael Andrew protocol
- High fat, moderate protein, minimal carbs
- Track macros in `michael_nutrition` table

### Friday - Sunday (Shabbat Observance)
- Moderate carbs allowed
- Kosher requirements maintained
- No tracking on Shabbat

## Data Storage

All swim data goes to:
- `michael_swim_times` - Performance tracking
- `michael_nutrition` - Diet logging
- `michael_recruiting` - D1 outreach

## Meet Schedule

- Check SwimCloud for upcoming meets
- Log results to Supabase after each meet
- Compare against rivals after each event
