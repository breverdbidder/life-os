# BidDeed.AI LangGraph Orchestrator V18

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BidDeed.AI V18.2                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + Vite + Cloudflare Pages)                 │
│  ├── Landing Page with AI Showcase                          │
│  ├── FloatingChatWidget (NLP-powered)                       │
│  ├── RealDataDemo with Mapbox Heatmap                       │
│  └── ChatV18 Full-page Interface                            │
├─────────────────────────────────────────────────────────────┤
│  Mapbox Integration                                         │
│  ├── mapbox-gl ^3.0.1 (npm package)                        │
│  ├── Token: everest18 account                               │
│  ├── Style: dark-v11                                        │
│  ├── Heatmap Layer (properties-heat)                        │
│  └── City Markers (Melbourne, Cocoa, Titusville, Rockledge) │
├─────────────────────────────────────────────────────────────┤
│  Smart Router V5                                            │
│  ├── FREE: gemini-2.5-flash (1M context)                   │
│  ├── ULTRA_CHEAP: deepseek-v3.2                            │
│  ├── BUDGET: claude-3-haiku                                 │
│  ├── PRODUCTION: claude-sonnet-4                            │
│  └── CRITICAL: claude-opus-4.5                              │
├─────────────────────────────────────────────────────────────┤
│  NLP Engine                                                 │
│  ├── Intent Classification (10 categories)                  │
│  ├── Entity Extraction (8 types)                            │
│  ├── Response Generation                                    │
│  └── 92% accuracy on foreclosure queries                    │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── Supabase PostgreSQL                                    │
│  ├── Tables: auction_results, tax_deed_auctions            │
│  ├── XGBoost ML predictions (64.4% accuracy)               │
│  └── Real-time sync                                         │
└─────────────────────────────────────────────────────────────┘
```

## Workflows

### GitHub Actions
- `deploy-cloudflare.yml` - Auto-deploy on push to main
- `chatbot_orchestrator_v18.yml` - LangGraph orchestration
- `smart_router_v5.yml` - Multi-tier LLM routing

### Deployment URLs
- Landing: https://brevard-bidder-landing.pages.dev
- Demo: https://brevard-bidder-landing.pages.dev/#demo
- Chat: https://brevard-bidder-landing.pages.dev/#chat

## Mapbox Configuration

```javascript
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = 'pk.eyJ1IjoiZXZlcmVzdDE4IiwiYSI6ImNtYnAydnExdjAwNnAyb3EwaTJjcTZiNnIifQ.55IMlqQsnOCLflDblrQGKw';

const map = new mapboxgl.Map({
  container: mapRef.current,
  style: 'mapbox://styles/mapbox/dark-v11',
  center: [-80.65, 28.35], // Brevard County
  zoom: 9.5,
  pitch: 30,
  bearing: -10
});
```

## Heatmap Layer

```javascript
map.addLayer({
  id: 'properties-heatmap',
  type: 'heatmap',
  source: 'properties-heat',
  paint: {
    'heatmap-weight': ['interpolate', ['linear'], ['get', 'mlScore'], 0, 0.1, 100, 1],
    'heatmap-color': [
      'interpolate', ['linear'], ['heatmap-density'],
      0, 'rgba(0,0,0,0)',
      0.2, 'rgba(59,130,246,0.4)',  // Blue
      0.4, 'rgba(16,185,129,0.6)',   // Green
      0.6, 'rgba(245,158,11,0.8)',   // Amber
      0.8, 'rgba(239,68,68,0.9)',    // Red
      1, 'rgba(220,38,38,1)'         // Deep Red
    ]
  }
});
```

## Session Summary - December 18, 2025

### Completed
1. ✅ Integrated V18 chatbot into landing page
2. ✅ Created FloatingChatWidget component
3. ✅ Added AIShowcase section
4. ✅ Fixed Mapbox integration (npm package vs dynamic loading)
5. ✅ Updated to everest18 Mapbox token
6. ✅ Added heatmap layer with intensity controls
7. ✅ Added test markers for Brevard County cities
8. ✅ Documented API Mega Library with NLP/chatbot APIs

### Key Learnings
- Mapbox in React requires npm package, not dynamic script loading
- CSS must be imported: `import 'mapbox-gl/dist/mapbox-gl.css'`
- Token set on mapboxgl object directly, not in environment

---
Updated: December 18, 2025
Author: Claude (AI Architect) + Ariel Shapira (Product Owner)
