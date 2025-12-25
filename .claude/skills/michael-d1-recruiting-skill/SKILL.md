---
name: michael-d1-recruiting-skill
description: D1 swimming recruiting workflows including coach outreach, program research, and timeline tracking for Michael Shapira
---

# Michael D1 Recruiting Skill

Comprehensive D1 swimming recruiting support for Michael Shapira (Class of 2027).

## When to Use This Skill

- Researching D1 swim programs
- Drafting coach outreach emails
- Tracking recruiting timelines
- Analyzing program fit
- Comparing scholarship opportunities

## Michael's Profile

### Basic Info
- **Name:** Michael Shapira
- **DOB:** July 22, 2009 (16 years old)
- **High School:** Satellite Beach High School
- **Graduation:** Class of 2027
- **SwimCloud ID:** 3250085

### Events & Times (Best)
- **50 Free:** TBD
- **100 Free:** 47.89
- **200 Free:** TBD
- **100 Fly:** TBD
- **100 Back:** TBD

### Training Philosophy
- **Diet:** Keto Mon-Thu, moderate carbs Fri-Sun (Shabbat)
- **Model:** Michael Andrew (Olympic sprinter, similar build/events)
- **Focus:** Sprint freestyle, butterfly, backstroke
- **No Practice:** Friday night through Saturday (Shabbat observance)

### Key Rivals (SwimCloud)
- Soto (ID: 2928537, PI: 47)
- Gordon (ID: 1733035, PI: 90)
- Domboru (ID: 1518102)

## D1 Recruiting Timeline

### Sophomore Year (Current - 2024-25)
- Build relationships with coaches
- Attend college swim meets
- Focus on time improvements
- Unofficial visits

### Junior Year (2025-26)
**CRITICAL RECRUITING YEAR**
- July 1, 2025: Coaches can contact directly
- September-November: Unofficial visits
- December-February: Official visits begin
- Verbal commitments common

### Senior Year (2026-27)
- November: Early signing period
- February: Regular signing period
- Focus on maintaining times

## Coach Outreach Templates

### Template 1: Initial Introduction
```
Subject: Michael Shapira - Class of 2027 Sprinter - [High School]

Dear Coach [Name],

My name is Michael Shapira, and I'm a sophomore sprint freestyler 
at Satellite Beach High School in Florida (Class of 2027). I'm very 
interested in [University]'s swim program.

Current Times:
- 100 Free: 47.89
- [Other events]

I'm particularly drawn to [University] because [specific reasons: 
coaching staff, team culture, academic programs].

I'd welcome the opportunity to connect and learn more about your program.

SwimCloud Profile: [link]

Best regards,
Michael Shapira
[email]
[phone]
```

### Template 2: Follow-Up After Meet
```
Subject: Michael Shapira - Recent Time Drops

Coach [Name],

Following up from my previous email - I wanted to share some 
recent progress:

[Meet Name], [Date]:
- 100 Free: [new time] (dropped [X] seconds)
- [Other improvements]

I remain very interested in [University] and would love to 
discuss how I could contribute to your program.

Best,
Michael
```

### Template 3: Request for Unofficial Visit
```
Subject: Unofficial Visit Request - Michael Shapira

Coach [Name],

I'll be in the [region] area [dates] and would love to schedule 
an unofficial visit to [University].

I'm particularly interested in:
- Meeting with coaching staff
- Touring facilities
- Watching practice (if possible)
- Meeting current swimmers

Would [proposed dates] work for a visit?

Thank you,
Michael
```

## Program Research Checklist

For each target school, research:

### Athletic Factors
- [ ] Coach's recruiting philosophy
- [ ] Team culture (sprint-focused? distance?)
- [ ] Facility quality (pool, weight room, recovery)
- [ ] Recent recruiting classes (scholarship availability?)
- [ ] Current roster sprint times (where would Michael fit?)
- [ ] Conference competitiveness

### Academic Factors
- [ ] Major offerings (business? engineering?)
- [ ] Academic support for athletes
- [ ] Graduation rate for athletes
- [ ] Class schedule flexibility

### Lifestyle Factors
- [ ] Location (proximity to family FL/IL)
- [ ] Jewish community on campus
- [ ] Kosher dining options
- [ ] Shabbat observance accommodation
- [ ] Cost (scholarship potential vs. family budget)

### Compliance Factors
- [ ] No Friday night/Saturday competitions during Shabbat
- [ ] Havdalah time consideration for Saturday evening meets
- [ ] Kosher food availability
- [ ] Access to synagogue/Jewish community

## Target Program Tiers

### Tier 1: Reach Programs
Top-25 D1 programs, highly competitive
- Required times: Sub-47.0 in 100 Free
- Example: University of Florida, NC State, Texas

### Tier 2: Target Programs  
Top-50 D1 programs, good fit
- Required times: 47.0-48.5 in 100 Free
- Example: Louisville, Virginia Tech, South Carolina

### Tier 3: Safety Programs
D1 programs actively recruiting
- Current times competitive
- High scholarship potential

## Scholarship Negotiation

### Types of Aid
1. **Athletic Scholarship:** Percentage of full ride
2. **Academic Scholarship:** Merit-based aid
3. **Need-Based Aid:** FAFSA-determined
4. **Jewish Community Scholarships:** Hillel, local orgs

### Negotiation Leverage
- Multiple offers from similar-tier programs
- Academic strength (GPA, test scores)
- Improvement trajectory ("my times are dropping")
- Demonstrated leadership (team captain, etc.)

## Communication Tracking

Log ALL coach interactions to Supabase:

```python
supabase.table('recruiting_contacts').insert({
    'athlete': 'michael_shapira',
    'program': university_name,
    'coach_name': coach_name,
    'contact_type': 'email|call|visit|meet',
    'date': datetime,
    'notes': interaction_summary,
    'next_steps': action_items,
    'interest_level': 'high|medium|low'
})
```

## Official Visit Strategy

### Maximum: 5 Official Visits
Choose strategically:
1. Top choice (Tier 1)
2. Strong fit (Tier 2)
3. Safety with best scholarship (Tier 3)
4. Geographic preference (near family)
5. Wildcard (unique appeal)

### Visit Preparation
- Research: Team roster, recent meets, coach background
- Questions: Prepare 10+ thoughtful questions
- Overnight: Connect with host swimmer
- Academics: Meet with academic advisor
- Family: Include Ariel/Mariam if possible

## SwimCloud Integration

### Track Performance
```
Use SwimCloud ID 3250085 to:
- Monitor time improvements
- Compare against rivals
- Identify national ranking
- Find target programs where times competitive
```

### Competitor Analysis
```
Track rivals:
- Soto (2928537): What programs recruiting him?
- Gordon (1733035): Where is he considering?
- Benchmark: Am I improving faster than rivals?
```

## Shabbat Accommodation

**Non-Negotiable Requirements:**
- No Friday evening practices/meets after sundown
- No Saturday practices/meets until havdalah
- Kosher food available
- Jewish community accessible

**Template for Coach Discussion:**
```
"I observe Shabbat, which means I don't practice or compete from 
Friday sundown through Saturday evening (havdalah). I'm looking for 
a program that can accommodate this while still allowing me to 
contribute meaningfully to the team. Would this be possible at 
[University]?"
```

## Timeline Alerts

Track key dates in Supabase with reminders:

```python
alerts = {
    '2025-07-01': 'Coaches can contact directly - JUNIOR YEAR STARTS',
    '2025-09-01': 'Unofficial visit season begins',
    '2026-11-01': 'Early signing period',
    '2027-02-01': 'Regular signing period'
}
```

## Output Format

For each program researched:

```json
{
  "university": "University of Florida",
  "tier": 1,
  "coach": "Anthony Nesty",
  "interest_level": "high",
  "academic_fit": {
    "major_available": true,
    "support_strong": true
  },
  "athletic_fit": {
    "sprint_focused": true,
    "current_100_free_avg": 46.2,
    "michael_competitive": false,
    "needs_time_drop": 1.69
  },
  "lifestyle_fit": {
    "jewish_community": "strong",
    "kosher_dining": "available",
    "shabbat_accommodation": "unknown"
  },
  "next_steps": [
    "Email coach introduction",
    "Research Shabbat policy",
    "Plan unofficial visit"
  ]
}
```

## Example Usage

```
"Research D1 swim programs in Florida for Michael using michael-d1-recruiting-skill"

"Draft coach outreach email for University of Louisville"

"Compare Michael's 100 free time against Tier 2 programs"

"Track all recruiting contacts this month"
```

## Integration with Life OS

- Log contacts to Supabase recruiting_contacts table
- Track time improvements in michael_swim_times table
- Set reminders for follow-ups
- Monitor timeline milestones
