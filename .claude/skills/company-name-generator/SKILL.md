---
name: company-name-generator
description: Generate, score, and validate company names across 10 categories with USPTO trademark screening and domain availability checking
---

# Company Name Generator Skill

## Overview
Generates business names across 10 strategic categories, scores them 0-100 based on memorability, pronounceability, uniqueness, and emotional impact, screens for USPTO trademark conflicts, and checks domain availability.

## Categories

1. **Descriptive** - Directly communicate function (e.g., "ForecastLogic AI")
2. **Metaphoric** - Evoke imagery beyond literal meaning (e.g., "Summit Intelligence")
3. **Invented** - Unique coinages with no prior meaning (e.g., "Auctioniq")
4. **Founder-Based** - Leverage personal brand (e.g., "The Shapira Formula")
5. **Acronym** - Memorable initialisms (e.g., "APEX")
6. **Compound** - Two-word combinations (e.g., "BidDeed.AI")
7. **Foreign Language** - Evoke sophistication (e.g., "Veritas Auction")
8. **Playful** - Approachable, memorable (e.g., "BidWise")
9. **Geographic** - Place-based authority (e.g., "Brevard BidTech")
10. **Legacy** - Timeless institutional authority (e.g., "Shapira & Associates")

## Scoring Criteria (0-100)

Each name scored across 5 weighted dimensions:

| Criterion | Weight | Scale |
|-----------|--------|-------|
| **Trademark Strength** | 30% | Distinctiveness, USPTO clearance probability |
| **Domain Signal** | 25% | Communicates industry/expertise |
| **Memorability** | 25% | Easy to recall, spell, pronounce |
| **Emotional Impact** | 10% | Positive associations, storytelling power |
| **Pronunciation** | 10% | Syllables, phonetics, clarity |

**Formula:** `Total = (TS×0.30) + (DS×0.25) + (M×0.25) + (EI×0.10) + (P×0.10)`

## Tools & APIs

### USPTO TESS (Trademark Electronic Search System)
- **Endpoint:** `https://tmsearch.uspto.gov/bin/gate.exe?f=tess&state=4801:xiq6gp.1.1`
- **Method:** Web scraping (no official API)
- **Search Pattern:** `LD:{search_term}` (Live/Dead search)
- **Classes:** 9 (Software), 41 (Education), 42 (SaaS/Consulting)

### Domain Availability
- **API:** `https://api.domainsdb.info/v1/domains/search`
- **Parameters:** `?domain={name}&zone=com`
- **Free Tier:** 50 requests/day
- **Alternatives:** `whoisxmlapi.com` (1000 free/month)

### Backup: Manual WHOIS
```bash
whois example.com | grep -i "No match\|NOT FOUND\|available"
```

## Usage

### Input Schema
```json
{
  "business_context": "Foreclosure auction intelligence platform",
  "current_name": "The Everest Ascent",
  "industry_keywords": ["real estate", "AI", "foreclosure", "auction"],
  "founder_name": "Ariel Shapira",
  "company_entity": "Everest Capital USA",
  "target_classes": [9, 42],
  "preserve_brand": "Everest",
  "signal_required": ["real_estate", "AI_ML"],
  "positioning": "metric/framework"
}
```

### Output Schema
```json
{
  "total_generated": 50,
  "top_25": [
    {
      "rank": 1,
      "name": "Everest ForecastAI",
      "category": "Compound",
      "total_score": 96,
      "breakdown": {
        "trademark_strength": 95,
        "domain_signal": 95,
        "memorability": 100,
        "emotional_impact": 90,
        "pronunciation": 90
      },
      "trademark": {
        "class_9_conflicts": 0,
        "class_42_conflicts": 0,
        "risk_level": "LOW"
      },
      "domains": {
        "com": false,
        "ai": true,
        "io": true,
        "best_option": "everestforecast.ai"
      },
      "strategic_fit": "⭐⭐⭐⭐⭐"
    }
  ]
}
```

## Implementation

See `/scripts/generate_names.py` for full implementation.

### Core Functions

**1. Generate Names by Category**
```python
def generate_descriptive_names(context):
    """Combine function words + tech suffixes"""
    functions = ["Forecast", "Auction", "Bid", "Lien", "Title"]
    tech = ["AI", "Logic", "Intelligence", "Analytics", "IQ"]
    return [f"{f}{t}" for f in functions for t in tech]
```

**2. Score Names**
```python
def score_name(name, context):
    scores = {
        "trademark": score_trademark_strength(name),
        "domain": score_domain_signal(name, context),
        "memorability": score_memorability(name),
        "emotional": score_emotional_impact(name),
        "pronunciation": score_pronunciation(name)
    }
    return weighted_total(scores)
```

**3. Check USPTO**
```python
def check_uspto(name, classes=[9, 42]):
    """Search USPTO TESS for conflicts"""
    results = {}
    for cls in classes:
        query = f"LD:{name}[COMB] AND IC:{cls:03d}"
        results[cls] = tess_search(query)
    return analyze_conflicts(results)
```

**4. Check Domains**
```python
def check_domains(name, tlds=[".com", ".ai", ".io"]):
    """Check availability across TLDs"""
    availability = {}
    for tld in tlds:
        domain = f"{name.lower().replace(' ', '')}{tld}"
        availability[tld] = is_available(domain)
    return availability
```

## Examples

### Example 1: Foreclosure Platform
**Input:** "Need name for foreclosure AI platform, preserve 'Everest' brand"

**Output:**
1. Everest ForecastAI (96/100) - LOW risk, .ai available
2. Everest BidIntelligence (95/100) - LOW risk, .com available
3. The Shapira Formula (95/100) - LOW risk, .ai available

### Example 2: SaaS Rebrand
**Input:** "Current: 'PropTech Solutions', need AI signal"

**Output:**
1. PropIntelligence AI (93/100)
2. SmartProperty Systems (91/100)
3. PropertyPredict Pro (89/100)

## Best Practices

1. **Always preserve brand equity** if existing entity has market recognition
2. **Signal domain expertise** - users should immediately understand industry
3. **Make AI explicit** if technology is core differentiator
4. **Check all 3 trademark classes** (9, 41, 42) for comprehensive protection
5. **Prefer .ai domains** for AI-focused businesses (signals innovation)
6. **Founder names = IP clarity** - personal ownership unambiguous
7. **Avoid generic terms** - "Smart", "Pro", "Best" have weak trademarks
8. **Test pronunciation** - say it 10x fast, if tongue-twisting = fail
9. **Cultural sensitivity** - check translations in target markets
10. **Future-proof** - name should work for product line extensions

## Trademark Filing Strategy

### Recommended Classes
- **Class 9:** Software products (downloadable, mobile apps)
- **Class 41:** Educational services, training, certification
- **Class 42:** SaaS, consulting, technical services

### Filing Costs (USPTO TEAS Plus)
- $350 per class
- 2 classes typical = $700
- 3 classes comprehensive = $1,050

### Timeline
- Application filed: Day 1
- Examining attorney review: 3-6 months
- Office action response: 6 months to respond
- Publication for opposition: 30 days
- Registration: 12-18 months total

## API Rate Limits

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| USPTO TESS | Unlimited (web scraping) | N/A |
| DomainsDB | 50/day | $49/mo (1000/day) |
| WhoisXML | 1000/month | $50/mo (10K) |

## Error Handling

```python
def safe_name_generation(context):
    try:
        names = generate_all_categories(context)
        scored = score_all_names(names)
        validated = check_trademarks_and_domains(scored)
        return top_25(validated)
    except USPTOTimeout:
        return fallback_to_cached_results()
    except DomainAPILimit:
        return results_with_manual_domain_check_note()
    except Exception as e:
        log_error(e)
        return partial_results_with_warning()
```

## References

- [USPTO TESS](https://tmsearch.uspto.gov/)
- [USPTO Trademark Basics](https://www.uspto.gov/trademarks/basics)
- [DomainsDB API Docs](https://domainsdb.info/api-documentation)
- [Naming Best Practices](https://www.namingforce.com/blog)

## Version History

- **v1.0** (Dec 25, 2025) - Initial skill with 10 categories, USPTO/domain checking
