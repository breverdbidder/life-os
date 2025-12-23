# API Mega Library - BidDeed.AI & Life OS Resources

**Source Repository:** [cporter202/API-mega-list](https://github.com/cporter202/API-mega-list)  
**Total APIs:** 10,498 across 18 categories  
**Last Updated:** December 13, 2025 (V14.5.1 - Claude Security Review + LangGraph)  
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
1. ✅ **Supplement BCPAO data** with Zillow/Redfin valuations (V14.5.0 LIVE)
2. ✅ **Comparable sales** from Zillow + Redfin (V14.5.0 LIVE)
3. ✅ **Multi-source ARV** with confidence scoring (V14.5.0 LIVE)
4. 🔄 Agent contact enrichment via Realtor.com agent scraper
5. 🔄 Market trend monitoring via StreetEasy/Zillow

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

### 🔄 LangGraph Orchestration (BidDeed.AI V14.5.1)

| Tool | Description | Status | URL |
|------|-------------|--------|-----|
| **LangGraph** | Stateful multi-actor agent orchestration | ✅ DEPLOYED | https://github.com/langchain-ai/langgraph |
| **LangGraph Studio** | Visual graph editor & debugger | 🔄 Evaluating | https://github.com/langchain-ai/langgraph-studio |
| **LangGraph CLI** | Local development server | ✅ Integrated | `pip install langgraph-cli` |
| **langgraph-checkpoint-sqlite** | SQLite-based state persistence | ✅ DEPLOYED | PyPI |
| **LangSmith** | Observability & tracing | 🔄 Evaluating | https://smith.langchain.com |

#### BidDeed.AI LangGraph Pipeline (12 Stages)
```
Discovery → Scraping → Title Search → Lien Priority → Tax Certs →
Demographics → ML Score → Max Bid → Decision Log → Report → 
Disposition → Archive
```

**Key Integrations:**
- `src/langgraph/orchestrator_v2.py` - Main orchestrator
- `src/langgraph/nodes/` - Individual stage implementations
- `.github/workflows/langgraph_orchestrator.yml` - GitHub Actions workflow
- SQLite checkpoints for state persistence

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

### 🔒 Security & Code Quality (BidDeed.AI DEPLOYED)

| Tool | Description | Status | Priority |
|------|-------------|--------|----------|
| **[anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review)** | Official Anthropic AI-powered security scanning for PRs | ✅ DEPLOYED | CRITICAL |
| [Snyk Security](https://snyk.io) | Dependency vulnerability scanning | ✅ DEPLOYED | HIGH |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | Secrets detection in code | ✅ DEPLOYED | HIGH |
| [Bandit](https://github.com/PyCQA/bandit) | Python SAST security linter | ✅ DEPLOYED | HIGH |
| [Safety](https://github.com/pyupio/safety) | Python dependency vulnerability check | ✅ DEPLOYED | MEDIUM |

#### Claude Code Security Review Configuration (V14.5.1)
```yaml
# .github/workflows/claude-security-review.yml
uses: anthropics/claude-code-security-review@main
with:
  claude-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
  claude-model: claude-sonnet-4-20250514
  custom-security-scan-instructions: .github/security/biddeed-security-instructions.md
  false-positive-filtering-instructions: .github/security/biddeed-fp-filter.md
```

**BidDeed.AI Security Focus Areas:**
- Financial calculation integrity (max bid formula)
- Agentic AI safety (LangGraph orchestrator)
- Credential management (API keys in secrets)
- Prompt injection prevention
- PDF/legal document handling

### Code & Development
| API | Description | Use Case |
|-----|-------------|----------|
| [CodeScout AI](https://apify.com/aigeek/codescout-ai) | AI-optimized codemaps from repos | Architecture docs |
| [GitHub Push Event Scraper](https://apify.com/krab/github-push-event-scraper) | Commit metadata extraction | Dev monitoring |
| [AI Code Review Agent](https://apify.com/fiery_dream/ai-code-review-agent) | GPT-4 code reviews | QA automation |
| [claude-code-excellence-audit](https://github.com/romiluz13/claude-code-excellence-audit) | Claude Code config scoring (0-100) | Config optimization |

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

### Phase 1 - Immediate (BidDeed.AI V14.5) ✅ COMPLETE
1. ✅ Census API (integrated)
2. ✅ **Zillow API via Apify** - Zestimates, comps, price history (V14.5.0)
3. ✅ **Redfin API via Apify** - Estimates, sold data, agent info (V14.5.0)
4. ✅ CMA Enrichment Agent - Multi-source ARV with confidence scoring
5. ✅ **Claude Code Security Review** - Anthropic official PR security scanning (V14.5.1)
6. 🔄 AI Web Agent - automate BECA document retrieval

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


---

## 🎨 UI/UX COMPONENT LIBRARIES - BidDeed.AI Priority

### Core Component Libraries (MANDATORY)

| Library | Stars | URL | Use Case | License |
|---------|-------|-----|----------|---------|
| shadcn/ui | 78k+ | ui.shadcn.com | Base components, Radix primitives | MIT |
| assistant-ui | 7.6k | github.com/assistant-ui/assistant-ui | Chat UI, LangGraph integration | MIT |
| LobeChat | 69k+ | github.com/lobehub/lobe-chat | MCP plugin system, Artifacts | Apache 2.0 |
| Recharts | 24k+ | recharts.org | Data visualization | MIT |
| Framer Motion | 24k+ | framer.com/motion | Animations | MIT |
| react-resizable-panels | 4k+ | github.com/bvaughn/react-resizable-panels | Split-screen layout | MIT |
| Mapbox GL JS | 11k+ | docs.mapbox.com/mapbox-gl-js | Interactive maps | BSD |
| TanStack Table | 26k+ | tanstack.com/table | Virtualized tables | MIT |

### Extended UI Ecosystem

| Library | Stars | URL | Use Case | License |
|---------|-------|-----|----------|---------|
| Material UI | 94k+ | mui.com | Enterprise components | MIT |
| Ant Design | 93k+ | ant.design | Data-dense interfaces | MIT |
| Chakra UI | 38k+ | chakra-ui.com | Accessible components | MIT |
| Radix UI | 16k+ | radix-ui.com | Unstyled primitives | MIT |
| NextUI | 22k+ | nextui.org | Modern components | MIT |
| Tremor | 16k+ | tremor.so | Dashboard components | Apache 2.0 |
| HeadlessUI | 26k+ | headlessui.com | Unstyled accessible | MIT |
| React Aria | 13k+ | react-spectrum.adobe.com/react-aria | Accessibility hooks | Apache 2.0 |

### Agent/AI-Specific UI

| Library | Stars | URL | Use Case | License |
|---------|-------|-----|----------|---------|
| OpenManus | 50.8k | github.com/FoundationAgents/OpenManus | Agent orchestration patterns | MIT |
| LangChain Agent Chat UI | 2k+ | github.com/langchain-ai/agent-chat-ui | Split-screen artifacts | MIT |
| OpenHands | 65k+ | github.com/All-Hands-AI/OpenHands | Agent GUI patterns | MIT |
| Vercel AI SDK | 10k+ | sdk.vercel.ai | Streaming responses | MIT |
| CopilotKit | 13k+ | copilotkit.ai | AI-native components | MIT |

### Specialized Libraries

| Library | URL | Use Case |
|---------|-----|----------|
| React Query | tanstack.com/query | Server state management |
| Zustand | zustand-demo.pmnd.rs | Client state management |
| React Hook Form | react-hook-form.com | Form handling |
| Zod | zod.dev | Schema validation |
| Nivo | nivo.rocks | D3-based charts |
| Visx | airbnb.io/visx | Low-level D3 |
| Lucide | lucide.dev | Icon system |
| date-fns | date-fns.org | Date formatting |
| numeral.js | numeraljs.com | Currency formatting |

### BidDeed.AI Component Stack (DEPLOYED)

```
brevard-bidder-scraper/frontend/
├── components/
│   ├── layout/SplitScreenLayout.tsx  ← Core split-screen
│   ├── map/MapView.tsx               ← Mapbox property map
│   └── property/
│       ├── PropertyCard.tsx          ← Property display
│       ├── PropertyFilters.tsx       ← Filter controls
│       ├── PropertyList.tsx          ← Property list
│       └── QuickStats.tsx            ← Dashboard stats
├── types/property.ts                 ← TypeScript interfaces
└── tailwind.config.ts               ← Design tokens
```

### Design Tokens

```css
/* BidDeed.AI Brand Colors */
--bb-primary: #667eea;    /* Trust Blue */
--bb-secondary: #764ba2;   /* Accent Purple */
--bb-bid: #22c55e;         /* Green - BID */
--bb-review: #fbbf24;      /* Yellow - REVIEW */
--bb-skip: #ef4444;        /* Red - SKIP */
```

### Documentation

- **Full Guide:** `docs/BIDDEED_AI_UI_UX_ECOSYSTEM.md`
- **awesome-ui-component-library:** github.com/anubhavsrivastava/awesome-ui-component-library (1.6k stars)

---



---

## 🎨 ULTIMATE UI/UX SOURCES

*Added December 2025 - Comprehensive component library reference for BidDeed.AI*

### Tier 1: Core Foundation (MANDATORY)

| Library | Stars | Purpose | License | URL |
|---------|-------|---------|---------|-----|
| **assistant-ui** | 7.6k+ | AI Chat Primitives (YC-backed, 400k+ monthly downloads) | MIT | https://github.com/assistant-ui/assistant-ui |
| **LobeChat** | 69k+ | Full Agent Workspace, MCP Marketplace, Artifacts | Apache 2.0 | https://github.com/lobehub/lobe-chat |
| **shadcn/ui** | 78k+ | Radix-based component primitives | MIT | https://ui.shadcn.com |
| **Recharts** | 24k+ | React charting for financial data | MIT | https://recharts.org |
| **Framer Motion** | 24k+ | Production animations | MIT | https://www.framer.com/motion |
| **react-resizable-panels** | 4k+ | Split-screen layout (40/60) | MIT | https://github.com/bvaughn/react-resizable-panels |

### Tier 2: Extended Ecosystem

| Library | Stars | Use Case | URL |
|---------|-------|----------|-----|
| **Material UI** | 94k+ | Enterprise component system | https://mui.com |
| **Ant Design** | 93k+ | Data-dense tables & forms | https://ant.design |
| **Chakra UI** | 38k+ | Accessible component system | https://chakra-ui.com |
| **Radix UI** | 16k+ | Unstyled accessible primitives | https://radix-ui.com |
| **Tremor** | 16k+ | Dashboard analytics | https://tremor.so |
| **NextUI** | 22k+ | Modern component library | https://nextui.org |
| **HeadlessUI** | 26k+ | Tailwind Labs primitives | https://headlessui.com |
| **React Aria** | 13k+ | Adobe accessibility library | https://react-spectrum.adobe.com |

### Tier 3: Data & State Management

| Library | Stars | Purpose |
|---------|-------|---------|
| **TanStack Table** | 26k+ | Headless table logic |
| **TanStack Query** | 43k+ | Server state management |
| **Zustand** | 48k+ | Lightweight client state |
| **Jotai** | 18k+ | Atomic state management |
| **React Hook Form** | 42k+ | Form validation |
| **Zod** | 35k+ | Runtime type validation |

### Tier 4: Agent/AI-Specific

| Library | Stars | BidDeed.AI Integration |
|---------|-------|------------------------|
| **OpenManus** | 50.8k | Multi-agent coordination reference |
| **OpenHands** | 65k+ | Code execution agent patterns |
| **Vercel AI SDK** | 10k+ | Streaming, tool calling |
| **CopilotKit** | 13k+ | Inline AI assistance |
| **LangChain Agent Chat UI** | 2k+ | LangGraph visualization |
| **claude-flow** | 5k+ | Claude orchestration patterns |

### Tier 5: Visualization & Maps

| Library | Stars | Purpose |
|---------|-------|---------|
| **Mapbox GL JS** | 11k+ | Property location mapping |
| **react-map-gl** | 8k+ | React wrapper for Mapbox |
| **Nivo** | 13k+ | Advanced data visualization |
| **Visx** | 19k+ | Low-level chart components |
| **Chart.js** | 64k+ | Simple charting |
| **D3.js** | 108k+ | Custom visualizations |

### MCP (Model Context Protocol) Resources

| Resource | Description | URL |
|----------|-------------|-----|
| **LobeChat MCP Marketplace** | 100+ MCP plugins | https://lobehub.com/mcp |
| **awesome-mcp-servers** | Community MCP server list | https://github.com/punkpeye/awesome-mcp-servers |
| **MCP SDK** | Official TypeScript SDK | https://github.com/modelcontextprotocol/sdk |

### BidDeed.AI Implementation Stack

```
Frontend:
├── Framework: Next.js 15 / Vite 5
├── UI: assistant-ui + shadcn/ui
├── State: Zustand + React Query
├── Styling: Tailwind CSS 4.0 + CVA
├── Animations: Framer Motion
└── Maps: Mapbox GL + react-map-gl

AI Integration:
├── Primary: Claude Sonnet 4 (Anthropic API)
├── Fallback: Gemini 2.5 Flash (Smart Router)
├── Protocol: MCP for tool orchestration
└── Chat: assistant-ui primitives

Backend:
├── Database: Supabase PostgreSQL
├── Auth: Clerk / Supabase Auth
├── Queue: BullMQ (pipeline orchestration)
└── Deploy: Cloudflare Pages + GitHub Actions
```

### Design Token Reference

```css
/* BidDeed.AI Color System */
--bb-primary: #667eea;    /* Trust Blue */
--bb-secondary: #764ba2;  /* Accent Purple */
--bb-dark: #1a1a2e;       /* Background */
--bb-darker: #16213e;     /* Panel */
--bb-accent: #0f3460;     /* Border */
--bb-bid: #22c55e;        /* Green - BID */
--bb-review: #fbbf24;     /* Yellow - REVIEW */
--bb-skip: #ef4444;       /* Red - SKIP */
```

---

*Total Combined Stars: 620k+*
*Last Updated: December 2025*



---

## 📱 MOBILE DEPLOYMENT - PWA, React Native, Push Notifications

*Added December 2025 - Mobile-first deployment patterns for BidDeed.AI*

### PWA (Progressive Web App) - RECOMMENDED PATH

| Resource | Description | URL |
|----------|-------------|-----|
| **Workbox** | Google's PWA toolkit | https://developers.google.com/web/tools/workbox |
| **PWA Builder** | Microsoft PWA generator | https://www.pwabuilder.com |
| **Vite PWA Plugin** | Zero-config PWA for Vite | https://vite-pwa-org.netlify.app |
| **Next.js PWA** | next-pwa package | https://github.com/shadowwalker/next-pwa |

#### BidDeed.AI PWA Implementation

```javascript
// vite.config.ts - Vite PWA Plugin
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'BidDeed.AI - Foreclosure Intelligence',
        short_name: 'BidDeed.AI',
        description: 'AI-powered foreclosure auction analysis',
        theme_color: '#667eea',
        background_color: '#1a1a2e',
        display: 'standalone',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.anthropic\.com/,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-cache' }
          }
        ]
      }
    })
  ]
})
```

#### Service Worker Template (Workbox)

```javascript
// sw.js - Service Worker
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { NetworkFirst, CacheFirst } from 'workbox-strategies';

// Precache static assets
precacheAndRoute(self.__WB_MANIFEST);

// Cache API responses (network-first)
registerRoute(
  ({ url }) => url.origin === 'https://api.anthropic.com',
  new NetworkFirst({ cacheName: 'api-responses' })
);

// Cache static assets (cache-first)
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({ cacheName: 'images' })
);
```

---

### React Native / Expo - NATIVE APP PATH

| Resource | Description | URL |
|----------|-------------|-----|
| **Expo** | React Native framework | https://expo.dev |
| **Expo Go** | Development testing app | https://expo.dev/go |
| **EAS Build** | Cloud builds for iOS/Android | https://expo.dev/eas |
| **React Native** | Core framework | https://reactnative.dev |

#### Expo Quick Start

```bash
# Initialize Expo project
npx create-expo-app@latest biddeed-mobile --template tabs

# Install dependencies
cd biddeed-mobile
npx expo install expo-notifications expo-secure-store
npx expo install @react-native-async-storage/async-storage

# Start development
npx expo start
```

#### Expo GitHub Actions Build

```yaml
# .github/workflows/expo-build.yml
name: Expo Build
on:
  push:
    branches: [main]
    paths: ['mobile/**']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: cd mobile && npm ci
      - run: cd mobile && eas build --platform all --non-interactive
```

---

### Push Notifications

| Service | Description | Pricing | URL |
|---------|-------------|---------|-----|
| **OneSignal** | Cross-platform push | Free tier: 10k MAU | https://onesignal.com |
| **Firebase Cloud Messaging (FCM)** | Google's push service | Free (unlimited) | https://firebase.google.com/docs/cloud-messaging |
| **Expo Notifications** | Built-in Expo push | Free with Expo | https://docs.expo.dev/push-notifications |
| **Novu** | Notification infrastructure | Free tier available | https://novu.co |
| **Knock** | Notification system | Free tier: 10k/mo | https://knock.app |

#### OneSignal Web Push (PWA)

```javascript
// Initialize OneSignal for PWA
import OneSignal from 'react-onesignal';

await OneSignal.init({
  appId: process.env.ONESIGNAL_APP_ID,
  safari_web_id: process.env.ONESIGNAL_SAFARI_ID,
  notifyButton: { enable: true },
  allowLocalhostAsSecureOrigin: true
});

// Request permission
await OneSignal.Notifications.requestPermission();

// Send notification from backend
const response = await fetch('https://onesignal.com/api/v1/notifications', {
  method: 'POST',
  headers: {
    'Authorization': `Basic ${ONESIGNAL_REST_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    app_id: ONESIGNAL_APP_ID,
    include_subscription_ids: [userId],
    contents: { en: 'New auction property matches your criteria!' },
    data: { propertyId: 'ABC123', type: 'auction_match' }
  })
});
```

#### Firebase Cloud Messaging (FCM)

```javascript
// firebase-messaging-sw.js (Service Worker)
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: 'YOUR_API_KEY',
  projectId: 'biddeed-ai',
  messagingSenderId: 'YOUR_SENDER_ID',
  appId: 'YOUR_APP_ID'
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body,
    icon: '/icon-192.png',
    data: payload.data
  });
});
```

#### Expo Push Notifications (React Native)

```javascript
// notifications.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

export async function registerForPushNotifications() {
  if (!Device.isDevice) return null;
  
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') return null;
  
  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id'
  });
  
  return token.data;
}

// Send via Expo Push API
const message = {
  to: expoPushToken,
  sound: 'default',
  title: 'Auction Alert',
  body: 'Property 123 Main St matches your criteria',
  data: { propertyId: 'ABC123' }
};

await fetch('https://exp.host/--/api/v2/push/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(message)
});
```

---

### Capacitor - Web-to-Native Bridge

| Resource | Description | URL |
|----------|-------------|-----|
| **Capacitor** | Ionic's web-to-native | https://capacitorjs.com |
| **Capacitor Push** | Native push support | https://capacitorjs.com/docs/apis/push-notifications |

```bash
# Add Capacitor to existing web app
npm install @capacitor/core @capacitor/cli
npx cap init BidDeedAI com.everestcapital.biddeed

# Add platforms
npm install @capacitor/android @capacitor/ios
npx cap add android
npx cap add ios

# Sync web build
npm run build
npx cap sync
```

---

### BidDeed.AI Mobile Deployment Priority

| Path | Effort | Cost | Recommendation |
|------|--------|------|----------------|
| **PWA** | 2-3 hours | $0 | ✅ DO FIRST - brevard-bidder-landing |
| **Expo Go** | 1-2 days | $0 | 🔄 Phase 2 if PWA insufficient |
| **App Store** | 3-5 days | $99/yr Apple + $25 Google | 🔄 Phase 3 for enterprise |

---

*Last Updated: December 2025*
*Maintainer: Ariel Shapira, Everest Capital USA*


---

## 🌐 BROWSER AUTOMATION APIs - BidDeed.AI Scraping

### Production Services (Tested Dec 2025)

| Service | Plan | Monthly | Use Case | Status |
|---------|------|---------|----------|--------|
| **Firecrawl** | Hobby | $16 | BECA scraping (anti-bot bypass) | 🔄 RECOMMENDED |
| **Browserless** | Prototyping | $35 | Already integrated, BrowserQL | ✅ INTEGRATED |
| Scrapfly | Startup | $30 | Alternative if others fail | 🔄 Evaluating |

### Test Results (Dec 16, 2025)

| Site | Free Playwright | Paid Required |
|------|-----------------|---------------|
| BCPAO | ✅ Works | No |
| RealForeclose | ✅ Works | No |
| BECA | ❌ IP Blocked | **Yes** |

### Firecrawl Details

- **GitHub:** https://github.com/mendableai/firecrawl
- **Pricing:** $16/mo = 3,000 credits (1 credit/page, 5 for stealth)
- **Self-host:** Available but NO Fire-engine (anti-bot is cloud-only)
- **Integration:** LangChain native, LLM-ready markdown output

### Browserless Details

- **GitHub:** https://github.com/browserless/browserless
- **Pricing:** $35/mo = 20,000 units (1 unit = 30s browser time)
- **Self-host:** Available but NO BrowserQL (stealth is paid-only)
- **Integration:** Native Puppeteer/Playwright, already in BidDeed.AI

### BidDeed.AI Strategy

```
HYBRID APPROACH (Optimized Cost):
├── FREE Playwright (GitHub Actions)
│   ├── BCPAO property lookups
│   ├── RealForeclose calendar
│   └── Tax deed results
└── PAID Firecrawl ($16/mo)
    └── BECA scraping only
    
Total: $16/mo instead of $35/mo = $228/year saved
```



---

## 🛒 GROCERY & SHOPPING APIs - Life OS Integration

*Added December 23, 2025 - Shopping automation for Life OS*

### MCP Servers (Model Context Protocol)

| MCP Server | Description | Auth | Cost | URL |
|------------|-------------|------|------|-----|
| **Instacart MCP** | Create shopping lists, recipe pages for 85k+ retailers | API Key | FREE | https://mcp.instacart.com/mcp |
| **Kroger MCP** | Full grocery automation: search, cart, checkout | OAuth2 | FREE | https://github.com/CupOfOwls/kroger-mcp |
| **Amazon Shopping MCP** | Product search, cart management, checkout | AWS API | FREE | https://github.com/Fewsats/amazon-mcp |
| **Shufersal MCP** | Israel grocery automation | OAuth2 | FREE | https://github.com/matipojo/shufersal-mcp |
| **CartQL MCP** | Universal cart API for AI agents | API Key | Freemium | https://cartql.com |

### Instacart Developer Platform

| Endpoint | Function | Auth |
|----------|----------|------|
| `POST /idp/v1/products/products_link` | Create shopping list page | Bearer Token |
| `POST /idp/v1/products/recipe` | Create recipe page | Bearer Token |
| MCP: `create-shopping-list` | MCP tool for shopping lists | Bearer Token |
| MCP: `create-recipe` | MCP tool for recipes | Bearer Token |

**Servers:**
- Development: `https://connect.dev.instacart.tools`
- Production: `https://connect.instacart.com`
- MCP Dev: `https://mcp.dev.instacart.tools/mcp`
- MCP Prod: `https://mcp.instacart.com/mcp`

**Apply:** https://www.instacart.com/company/business/developers

### Kroger MCP Server (Full Automation)

```bash
# Install
pip install kroger-mcp
# Or with uvx
uvx kroger-mcp
```

**Tools Available:**
| Tool | Function |
|------|----------|
| `search_locations` | Find stores by ZIP |
| `search_products` | Search with pricing/availability |
| `add_items_to_cart` | Add to Kroger cart (OAuth2) |
| `view_current_cart` | Local cart tracking |
| `get_product_details` | Full product info |

**Kroger Banners Covered:**
- Kroger, Ralphs, Fred Meyer, Harris Teeter
- King Soopers, Smith's, QFC, Fry's, Dillons
- Food 4 Less, Foods Co, Pay Less

**Get API Keys:** https://developer.kroger.com

### Costco Scrapers (Apify - Product Data Only)

| Actor | Cost | Function |
|-------|------|----------|
| `tri_angle/costco-fast-product-scraper` | $5/mo free tier | Quick product search |
| `ecomscrape/costco-product-details-scraper` | Pay per run | Full product details |
| `tri_angle/costco-reviews-scraper` | Pay per run | Customer reviews |
| `ecomscrape/costco-other-site-product-search-scraper` | Pay per run | International Costco |

**Limitation:** Costco has NO public checkout API. Scrapers are read-only (price/inventory check).

### Amazon Shopping MCP

```json
{
  "mcpServers": {
    "Amazon": {
      "command": "uvx",
      "args": ["amazon-mcp"]
    },
    "Fewsats": {
      "command": "env",
      "args": ["FEWSATS_API_KEY=YOUR_KEY", "uvx", "fewsats-mcp"]
    }
  }
}
```

**Requirements:** AWS Product Advertising API credentials

### Life OS Shopping Architecture

```
┌─────────────────────────────────────────────────┐
│  Life OS Chat                                   │
│  "Buy these items at Costco/Kroger"             │
└─────────────────────┬───────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────────┐     ┌───────────────────┐
│ Costco → Instacart│     │ Kroger → MCP      │
│ (via IDP API)     │     │ (Full checkout)   │
│ Returns URL       │     │ OAuth2 cart mgmt  │
└───────────────────┘     └───────────────────┘
```

### Deployment Status (Life OS)

| Integration | Status | Location |
|-------------|--------|----------|
| Instacart API Client | ✅ Deployed | `life-os/shopping/src/instacart_client.ts` |
| Cloudflare Worker | ✅ Deployed | `life-os/shopping/src/worker.ts` |
| Shopping List React Component | ✅ Deployed | `life-os/shopping/src/components/ShoppingList.tsx` |
| Supabase Table | ✅ Migration ready | `shopping_lists` table |
| Kroger MCP | 🔄 Planned | Phase 2 |

---

