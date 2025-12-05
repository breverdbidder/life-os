---
name: life-os-knowledge
description: Personal knowledge base for Shapira family daily life. Use when querying or storing information about hotels, swim meet venues, travel logistics, restaurants, service providers, or any location-based preferences. Triggers on phrases like "remember this hotel", "where did we stay", "next time in [city]", "log this location", or references to past stays/visits.
---

# Life OS Knowledge Base

Personal knowledge system for the Shapira family. Stores hotels, venues, travel logistics, and location-based preferences.

## Data Storage

**Primary:** Supabase table `life_os_locations`
**Database:** mocerqjnksmhcjzxrewo.supabase.co

## Schema: life_os_locations

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| category | text | HOTEL, SWIM_VENUE, RESTAURANT, SERVICE_PROVIDER, TRAVEL_ROUTE |
| name | text | Location name |
| address | text | Full address |
| city | text | City |
| state | text | State |
| context | text | Why we use this (e.g., "Michael swim meets") |
| rating | int | 1-5 stars |
| notes | jsonb | Flexible notes (room type, amenities, tips) |
| last_visited | date | Most recent visit |
| created_at | timestamp | Record creation |

## Usage Patterns

### Storing New Location
```sql
INSERT INTO life_os_locations (category, name, address, city, state, context, rating, notes, last_visited)
VALUES ('HOTEL', 'Staybridge Suites Ocala', '4627 NW Blitchton Rd', 'Ocala', 'FL', 
        'Michael swim meets at Ocala Aquatic Center', 5,
        '{"room_type": "studio with queen beds", "amenities": ["kitchen", "breakfast"], "value": "excellent"}',
        '2025-12-04');
```

### Querying by Context
```sql
SELECT * FROM life_os_locations 
WHERE context ILIKE '%swim%' AND city = 'Ocala';
```

### Querying by Category
```sql
SELECT * FROM life_os_locations 
WHERE category = 'HOTEL' AND state = 'FL'
ORDER BY rating DESC;
```

## Categories

- **HOTEL** - Overnight stays, include room type, value rating
- **SWIM_VENUE** - Competition pools, include pool speed (fast/slow), parking, warmup info
- **RESTAURANT** - Kosher-friendly, keto-friendly options noted
- **SERVICE_PROVIDER** - Contractors, professionals, include contact info
- **TRAVEL_ROUTE** - Common drives, include duration, stops, tips

## Integration with Memory

Memory stores pointers to frequently-accessed locations. Full details live in Supabase.
Example memory: "Michael swim meets @ Ocala: Staybridge Suites (see life_os_locations)"

## Reference Files

- `references/hotels.md` - Hotel reviews and preferences
- `references/swim-venues.md` - Swim meet venue details
- `references/travel.md` - Travel routes and logistics
