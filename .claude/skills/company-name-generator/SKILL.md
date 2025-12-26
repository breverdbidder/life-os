---
name: company-name-generator
description: Generate business names across 10 categories with USPTO trademark screening, domain availability checking, and automated scoring (0-100). Use when users need naming options for companies, products, methodologies, or frameworks. Outputs ranked names with trademark risk assessment and strategic recommendations.
---

# Company Name Generator

Generates business names across 10 naming categories with built-in trademark screening and domain availability validation.

## When to Use This Skill

- User requests business name ideas, company names, or product names
- User mentions trademark concerns or domain availability
- User wants professional naming analysis with scoring
- User needs multiple naming options ranked by criteria
- User asks for methodology/framework names (like "Six Sigma" or "Moneyball")

## Workflow

### Step 1: Context Gathering

Extract from user's request:
- **Industry/Domain**: What business (e.g., foreclosure real estate, AI/ML, SaaS)
- **Signals to Communicate**: Capabilities (e.g., AI, automation, prediction, real estate)
- **Existing Brand**: Any brand equity to preserve (e.g., "Everest Capital USA")
- **Name Type**: Company, product, methodology, metric, framework
- **Trademark Classes**: Default Classes 9+42 (software + SaaS)

### Step 2: Generate Names (10 Categories)

Generate 10-15 names per category (100+ total):

1. **Descriptive**: Function-based (AuctionIntel, ForecastLogic AI)
2. **Metaphoric**: Imagery (Summit Intelligence, Compass Real AI)
3. **Invented**: Coinages (Auctioniq, Bidlytics, Lienova)
4. **Founder-based**: Personal (The Shapira Formula, Shapira Intelligence)
5. **Acronym**: Initialisms (APEX, SAFE, EAGLE, RADAR)
6. **Compound**: Two-words (BidDeed.AI, LienLogic, TitleTrack)
7. **Foreign Language**: Sophistication (Veritas Auction, Apex Lux)
8. **Playful**: Approachable (BidWise, DeedDive, AuctionHawk)
9. **Geographic**: Place-based (Brevard BidTech, Space Coast Intelligence)
10. **Legacy**: Institutional (Shapira & Associates, The Everest Group)

### Step 3: Score Each Name (0-100)

**Scoring Formula:**
```
Score = (Trademark×0.30) + (DomainSignal×0.25) + (TechSignal×0.25) + (Metaphor×0.10) + (Pronunciation×0.10)
```

**Criteria:**

| Criterion | 90-100 | 75-89 | 60-74 | <60 |
|-----------|--------|-------|-------|-----|
| **Trademark** | Unique, 0-2 conflicts | Distinctive, 3-4 conflicts | Common combo, 5+ conflicts | Generic/exact match |
| **Domain Signal** | Explicit (Auction, Lien, Title) | Clear (Forecast, Bid, Property) | Implied (Intelligence, Capital) | Weak/none |
| **Tech Signal** | Explicit AI/ML/Algorithm | Strong (.ai, Analytics, Smart) | Implied (Auto, Predict) | Weak/none |
| **Metaphor** | Evocative storytelling | Clear imagery | Subtle | None |
| **Pronunciation** | 1-2 syllables, phonetic | 3 syllables, clear | 4+ syllables | Difficult |

### Step 4: USPTO Trademark Check (Simulated)

**Risk Assessment:**
- **LOW**: 0-2 similar marks, distinctive
- **MEDIUM**: 3-5 similar marks, one exact in different class  
- **HIGH**: 5+ similar, exact match in same class

*Note: Full USPTO TESS API integration in `scripts/uspto_check.py` (not yet implemented - manual review recommended)*

### Step 5: Domain Availability Check (Simulated)

Check availability for:
- **.com** (priority)
- **.ai** (tech signal)
- **.io** (startup signal)

*Note: Full domain API integration in `scripts/domain_check.py` (not yet implemented - manual verification recommended)*

### Step 6: Output Ranked Report

Generate markdown with:

1. **Executive Summary**: Top 3 recommendations with scores
2. **Category Winners**: Best name per category
3. **Overall Top 25**: Ranked table (name, category, score, trademark risk, domain)
4. **Strategic Analysis**: Brand architecture, dual-brand strategies
5. **USPTO Templates**: Ready-to-file TEAS applications
6. **Next Steps**: Timeline, budget, recommendations

## Scoring Rubric (Detailed)

### Trademark Strength (30%)
- **100**: Invented word, zero conflicts (e.g., Auctioniq)
- **90**: Unique combo, 1-2 conflicts
- **80**: Distinctive, 3-4 conflicts
- **70**: Common words, unique combo
- **60**: Descriptive, 5+ conflicts
- **<60**: Generic or exact match exists

### Domain Signal (25%)
- **100**: Industry explicit (Auction, Foreclosure, Lien, Title, Deed)
- **90**: Very clear (Forecast, Bid, Property, Market)
- **80**: Clear with context (Intelligence, Capital, Analytics)
- **70**: Implied (Insights, Edge, Prime)
- **60**: Broad (Systems, Platform, Group)
- **<60**: Weak or no connection

### Tech Signal (25%)
- **100**: Explicit AI/ML (AI, Intelligence, Logic, Algorithm)
- **90**: Strong tech (.ai TLD, Analytics, Systems)
- **80**: Tech-forward (Smart, Auto, Cognitive)
- **70**: Implied (Predict, Optimize, Intelligent)
- **60**: Subtle (Pro, Plus, Advanced)
- **<60**: No tech signal

### Metaphor Power (10%)
- **100**: Evocative storytelling (Summit, Oracle, Compass, Beacon)
- **90**: Strong imagery (Radar, Atlas, Eagle, Keystone)
- **80**: Clear metaphor (Edge, Prime, Path, Apex)
- **70**: Subtle (North, Rise, Flow)
- **60**: Mild (Plus, Pro, Max)
- **<60**: Literal only

### Pronunciation (10%)
- **100**: 1-2 syllables, phonetic, memorable
- **90**: 3 syllables, clear
- **80**: 4 syllables, pronounceable
- **70**: Complex but clear
- **60**: Ambiguous
- **<60**: Difficult/unpronounceable

## Dual-Brand Strategy

When user has existing brand equity but needs better domain/tech signal:

```
Parent Brand (Existing) → Everest Capital USA
    │
    ├── Methodology (New) → The Shapira Formula™ (Ariel owns IP)
    │       └── Framework → The Everest Ascent™ (12 stages)
    │
    └── Product (New) → BidDeed.AI
            └── Tagline → "Powered by The Shapira Formula™"
```

**Benefits:**
- Preserves existing brand equity ✅
- Adds clear domain + tech signals ✅
- Separates IP ownership (methodology vs. product) ✅
- Supports exit strategy (license methodology separately) ✅

## USPTO Filing Template

```
TEAS PLUS APPLICATION ($350/class)

Mark: [NAME]
Applicant: [OWNER] (Individual/Corporation)
Address: [ADDRESS]

CLASS 9 - Computer Software
Downloadable computer software using artificial intelligence 
for [USE CASE]; Downloadable [DOMAIN] software featuring [FEATURES].

First Use: [DATE]
Specimen: Screenshot showing "[NAME]" in software interface

CLASS 42 - SaaS  
Software as a service (SAAS) featuring [DESCRIPTION].

First Use: [DATE]
Specimen: Website screenshot (login/subscription page)

Total Fee: $350 × [CLASSES] = $[TOTAL]
```

## Best Practices

**DO:**
- ✅ Generate 100+ names across all categories
- ✅ Score all names using formula
- ✅ Provide top 3 with strategic rationale
- ✅ Include trademark templates for winners
- ✅ Consider existing brand equity

**DON'T:**
- ❌ Skip scoring (unbalanced recommendations)
- ❌ Recommend HIGH trademark risk without disclaimer
- ❌ Generate <50 total names
- ❌ Ignore existing brand relationships
- ❌ Claim legal advice (USPTO screening is preliminary)

## Limitations

- USPTO screening simulated (recommend attorney review)
- Domain checks simulated (verify manually)
- Scoring algorithmic (human judgment needed)
- USPTO only (no international trademarks)
- No cultural sensitivity automation (manual review needed)

For legal review: Recommend USPTO-registered trademark attorney  
For premium domains: Recommend GoDaddy Auctions or Sedo
