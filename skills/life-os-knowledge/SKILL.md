---
name: life-os-knowledge
description: Personal knowledge base for Shapira family daily life. Use when querying or storing information about hotels, swim meet venues, travel logistics, restaurants, service providers, or any location-based preferences. Triggers on phrases like "remember this hotel", "where did we stay", "next time in [city]", "log this location", or references to past stays/visits.
---

# Life OS Knowledge Base

Personal knowledge system for the Shapira family. Stores hotels, venues, travel logistics, and location-based preferences.

## Data Storage

**Database:** Supabase `mocerqjnksmhcjzxrewo`
**Table:** `insights` (using insight_type for categorization)

## Location Categories (insight_type values)

- `HOTEL` - Overnight stays
- `SWIM_VENUE` - Competition pools
- `RESTAURANT` - Dining options (kosher-friendly noted)
- `SERVICE_PROVIDER` - Contractors, professionals
- `TRAVEL_ROUTE` - Common drives

## Query Patterns

### Find hotels in a city
```python
GET /rest/v1/insights?insight_type=eq.HOTEL&description=cs.Ocala
```

### Find swim venues
```python
GET /rest/v1/insights?insight_type=eq.SWIM_VENUE&order=confidence.desc
```

### Search by context
```python
GET /rest/v1/insights?insight_type=in.(HOTEL,SWIM_VENUE)&description=cs.Michael
```

## Insert Pattern

```python
{
    "insight_type": "HOTEL",
    "title": "Hotel Name",
    "description": json.dumps({
        "address": "123 Main St",
        "city": "City",
        "state": "FL",
        "context": "Why we use this",
        "room_type": "suite/studio/etc",
        "amenities": ["list", "of", "amenities"],
        "value": "excellent/good/budget"
    }),
    "related_date": "2025-12-04",
    "priority": "medium",
    "status": "active",
    "source": "life_os_knowledge",
    "confidence": 5  # 1-5 star rating
}
```

## Reference Files

- `references/hotels.md` - Hotel reviews and preferences
- `references/swim-venues.md` - Swim meet venue details  
- `references/travel.md` - Travel routes and logistics
- `scripts/query_locations.py` - Helper for location queries
