# Hotels Reference - Shapira Family

## Quick Lookup

Query Supabase: `GET /rest/v1/insights?insight_type=eq.HOTEL&source=eq.life_os_knowledge`

## Florida Swim Meet Hotels

### Ocala Area

**Staybridge Suites Ocala** ⭐⭐⭐⭐⭐
- Address: 4627 NW Blitchton Rd, Ocala, FL 34482
- Context: Michael swim meets at Ocala Aquatic Center (fast pool)
- Room Type: Studio with queen beds
- Amenities: Full kitchen, free breakfast, spacious
- Value: Excellent - great price for what you get
- Last Stay: December 2025
- ✅ **RECOMMENDED** for future Ocala meets

---

## Rating Guide

| Stars | Meaning |
|-------|---------|
| ⭐⭐⭐⭐⭐ | Excellent - book again immediately |
| ⭐⭐⭐⭐ | Good - would stay again |
| ⭐⭐⭐ | Acceptable - if nothing else available |
| ⭐⭐ | Below average - avoid if possible |
| ⭐ | Poor - do not book again |

## Data Fields for Hotels

When adding a new hotel, capture:
```json
{
  "address": "Full street address",
  "city": "City name",
  "state": "FL",
  "context": "Why we stayed (swim meet, business, etc.)",
  "room_type": "king/queen/suite/studio",
  "amenities": ["kitchen", "pool", "breakfast"],
  "value": "budget/good/excellent",
  "tips": "Any notes for next time"
}
```
