# API Mega Library - BidDeed.AI & Life OS Resources

**Source Repository:** [cporter202/API-mega-list](https://github.com/cporter202/API-mega-list)  
**Total APIs:** 10,498 across 18 categories  
**Last Updated:** December 10, 2025  
**Curated by:** Ariel Shapira, Everest Capital of Brevard LLC

---

## Quick Reference - Category Counts

| Category | API Count | Primary Use Case |
|----------|-----------|------------------|
| Automation | 4,825 | Workflow automation, scheduling |
| Lead Generation | 3,452 | Contact enrichment, B2B outreach |
| Social Media | 3,268 | Social listening, content scraping |
| Developer Tools | 2,652 | Code tools, testing, deployment |
| E-commerce | 2,440 | Product data, pricing intelligence |
| Other | 1,297 | Miscellaneous utilities |
| AI | 1,208 | LLM integrations, AI agents |
| Videos | 979 | Video scraping, transcription |
| Integrations | 890 | Platform connectors |
| **Real Estate** | **851** | **Property data, listings, market intel** |
| Jobs | 848 | Job board scraping |
| Open Source | 768 | Free/OSS tools |
| SEO Tools | 710 | Rankings, backlinks, keywords |
| Agents | 697 | AI agents, autonomous systems |
| News | 590 | News aggregation, RSS |
| Travel | 397 | Hotels, flights, bookings |
| MCP Servers | 131 | Model Context Protocol servers |
| Business | 2 | Business utilities |

---

## 🏠 REAL ESTATE APIs - BidDeed.AI Priority

### Property Data Aggregators
| API | Description | Use Case |
|-----|-------------|----------|
| [Global Real Estate Aggregator](https://apify.com/charlestechy/global-real-estate-aggregator) | Unified API for Zillow, Realtor, Zumper, Apartments.com, Rightmove | Multi-source property comparison |
| [MLS API](https://apify.com/api/mls-api) | Real estate aggregator with standardized format | Market analysis |
| [Real Estate API](https://apify.com/api/real-estate-api) | Property prices, GPS, beds/baths, living area | Valuation data |
| [RealEstateAPI.com](https://www.realestateapi.com) | Prop-tech APIs for disruptive applications | Investment analysis |

### Platform-Specific Scrapers
| API | Platform | Key Data |
|-----|----------|----------|
| [Realtor.com Scraper](https://apify.com/epctex/realtor-scraper) | Realtor.com | Listings, agents, pricing |
| [Zillow Group APIs](https://www.zillowgroup.com/developers/) | Zillow | Zestimates, MLS, transactions |
| [StreetEasy Scraper](https://apify.com/scrapestorm/streeteasy-real-estate-scraper---cheap) | StreetEasy | NYC real estate data |
| [Compass Urls Spider](https://apify.com/hello.datawizards/compass-urls-spider) | Compass | Property details, agent info |
| [Idealista Scraper](https://apify.com/igolaizola/idealista-scraper) | Idealista | Spain/Italy/Portugal properties |

### BidDeed.AI Integration Opportunities
1. **Supplement BCPAO data** with Zillow/Realtor valuations
2. **Agent contact enrichment** via Realtor.com agent scraper
3. **Comparable sales analysis** via MLS API
4. **Market trend monitoring** via StreetEasy/Zillow

---

## 🤖 AI & AGENTS APIs - Agentic AI Infrastructure

### AI Agents
| API | Description | Integration |
|-----|-------------|-------------|
| [AI Web Agent](https://apify.com/apify/ai-web-agent) | Natural language web browsing, form filling | BidDeed.AI automation |
| [AI Company Researcher Agent](https://apify.com/louisdeconinck/ai-company-researcher-agent) | AI-powered company research | Plaintiff research |
| [AI Real Estate Agent](https://apify.com/harvestlabs/ai-real-estate-agent) | Property search by criteria | Automated property analysis |
| [Deep Job Search Agent](https://apify.com/fantastic-jobs/deep-job-search-agent) | Multi-source job aggregation | Life OS job tracking |
| [Competitive Intelligence Agent](https://apify.com/apify/competitive-intelligence-agent) | Google Maps + social data analysis | Market gap analysis |

### AI Content Processing
| API | Description | Use Case |
|-----|-------------|----------|
| [AI Content Processor](https://apify.com/valid_headlamp/ai-content-processor) | GPT-4o summarization, NER, sentiment | Document analysis |
| [AI Markdown Maker](https://apify.com/onescales/bulk-ai-markdown-maker) | Web to markdown conversion | RAG pipeline prep |
| [AI Web Scraper - Crawl4AI](https://apify.com/raizen/ai-web-scraper) | LLM-optimized scraping | Training data collection |
| [AI Training Data Enricher](https://apify.com/fiery_dream/ai-training-data-enricher) | Data validation, deduplication | ML model training |

### MCP Servers (Model Context Protocol)
| MCP Server | Function | Priority |
|------------|----------|----------|
| [Context7 MCP Server](https://apify.com/agentify/context7-mcp-server) | Up-to-date code documentation | HIGH - Claude Code |
| [Calculator MCP Server](https://apify.com/matymar/calculator-mcp-server) | Math operations | LOW |
| [Figma MCP Server](https://apify.com/woundless_vehicle/figma-mcp-server) | Figma design access | Life OS design |
| [Gemini AI MCP Server](https://apify.com/bhansalisoft/gemini-ai-mcp-server) | Gemini integration | Smart Router fallback |

---

## 📊 GOVERNMENT & PUBLIC DATA APIs

### US Census Bureau (FREE)
| Endpoint | Data | URL |
|----------|------|-----|
| American Community Survey (ACS) | Demographics, income, housing | `api.census.gov/data/{year}/acs/acs5` |
| Population Estimates | Population by state/county | `api.census.gov/data/{year}/pep/population` |
| Economic Census | Business data by industry | `api.census.gov/data/{year}/ecnbasic` |
| TIGERweb GeoServices | Census boundaries by FIPS | `tigerweb.geo.census.gov/arcgis/rest/services` |
| Geocoding API | Address to lat/long | `geocoding.geo.census.gov/geocoder/locations/onelineaddress` |

**Census API Key Request:** https://api.census.gov/data/key_signup.html

### BidDeed.AI Census Integration
Already using Census API for demographics - expand to:
- Housing characteristics (vacancy rates)
- Income estimates by tract
- Business establishment counts

---

## 🔍 LEAD GENERATION & CONTACT APIs

### B2B Lead Generation
| API | Description | Cost |
|-----|-------------|------|
| [Leads Finder](https://apify.com/code_crafter/leads-finder) | Apollo alternative - emails, phones, LinkedIn | $1.5/1k leads |
| [Company Contact Scraper](https://apify.com/fatihtahta/waterfall-contact-enricher) | Domain to contact list | $4.5/1k |
| [Global Lead Scraper](https://apify.com/charlestechy/global-lead-scraper) | Business websites + email extraction | Per crawl |
| [Crunchbase Scraper](https://apify.com/ingenious_mastiff/crunchbase-scrapper) | Company profiles, funding, executives | Per profile |

### Email Scrapers
| API | Platform | Use Case |
|-----|----------|----------|
| [Instagram Email Scraper](https://apify.com/scraper-mind/best-instagram-email-scraper) | Instagram | B2C outreach |
| [Events Email Scraper](https://apify.com/scrapestorm/events-lead-conferences-email-scraper---cheap-advanced) | Events/Conferences | Sponsor outreach |
| [Expedia Email Scraper](https://apify.com/contactminerlabs/expedia-email-scraper---advanced-cheapest-reliable) | Expedia | Travel contacts |

---

## 📱 SOCIAL MEDIA & NEWS APIs

### Social Platforms
| API | Platform | Key Features |
|-----|----------|--------------|
| [Facebook Ads Library Scraper](https://apify.com/api-empire/facebook-ads-library-scraper) | Facebook | Ad creatives, spend, targeting |
| [Twitter/X Scraper](https://apify.com/mikolabs/x-scraper) | X/Twitter | Tweets, profiles, media |
| [Comments Analyzer Agent](https://apify.com/apify/comments-analyzer-agent) | TikTok/YouTube/Instagram | Sentiment analysis, crisis detection |

### News Intelligence
| API | Description | Use Case |
|-----|-------------|----------|
| [AI Newsletter Agent](https://apify.com/louisdeconinck/ai-newsletter-agent) | Curated newsletters on any topic | Industry monitoring |
| [Global Markets Intelligence](https://apify.com/visita/global-markets-intelligence) | Financial news + AI sentiment | Investment signals |
| [GDELT News Pipeline](https://apify.com/visita/gdelt-news) | Multi-source news aggregation | Market monitoring |

---

## 🛠️ AUTOMATION & DEVELOPER TOOLS

### Web Scraping Infrastructure
| API | Description | Priority |
|-----|-------------|----------|
| [AI Web Fetcher](https://apify.com/abotapi/ai-fetch-python) | LLM-friendly markdown conversion | HIGH - RAG |
| [AI Search Tool](https://apify.com/abotapi/ai-web-search-tool) | Multi-backend DuckDuckGo search | HIGH - Agent search |
| [Complete SEO Audit Tool](https://apify.com/smart-digital/complete-seo-audit-tool) | 0-100 SEO scores | Marketing |

### Code & Development
| API | Description | Use Case |
|-----|-------------|----------|
| [CodeScout AI](https://apify.com/aigeek/codescout-ai) | AI-optimized codemaps from repos | Architecture docs |
| [GitHub Push Event Scraper](https://apify.com/krab/github-push-event-scraper) | Commit metadata extraction | Dev monitoring |
| [AI Code Review Agent](https://apify.com/fiery_dream/ai-code-review-agent) | GPT-4 code reviews | QA automation |

---

## 💼 LIFE OS - MICHAEL D1 SWIMMING

### Fitness & Performance
| API | Description | Use Case |
|-----|-------------|----------|
| Sports stats APIs | Performance tracking | Swim time analysis |
| Nutrition APIs | Meal planning | Keto meal tracking |

### Family & Calendar
| API | Description | Use Case |
|-----|-------------|----------|
| Google Calendar MCP | Event management | Shabbat scheduling |
| [AI Travel Agent](https://apify.com/harvestlabs/ai-travel-agent) | Travel planning | College visit planning |

---

## 📁 Repository Integration Plan

### GitHub Deployment
```bash
# BidDeed.AI
breverdbidder/brevard-bidder-scraper/docs/API_MEGA_LIBRARY.md

# Life OS
breverdbidder/life-os/docs/API_MEGA_LIBRARY.md
```

### Supabase Storage
```sql
INSERT INTO insights (category, content, metadata)
VALUES (
  'api_library',
  'API Mega Library - 10,498 APIs across 18 categories',
  {
    "source": "github.com/cporter202/API-mega-list",
    "total_apis": 10498,
    "categories": 18,
    "real_estate_apis": 851,
    "ai_apis": 1208,
    "priority_integrations": ["Real Estate Aggregator", "Census API", "MCP Servers"]
  }
);
```

---

## Priority Integration Roadmap

### Phase 1 - Immediate (BidDeed.AI V14)
1. ✅ Census API (already integrated)
2. 🔄 Real Estate Aggregator API - supplement BCPAO valuations
3. 🔄 AI Web Agent - automate BECA document retrieval

### Phase 2 - Q1 2026
1. Lead Generation APIs - owner contact enrichment
2. MCP Servers - Claude Code integration
3. News Intelligence - market trend monitoring

### Phase 3 - Scale
1. Social Media APIs - community sentiment analysis
2. Automation APIs - full pipeline automation
3. Multi-source property aggregation

---

**Credit:** Ariel Shapira, Solo Founder - Real Estate Developer & Founder, Everest Capital USA
