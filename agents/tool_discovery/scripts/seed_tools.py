#!/usr/bin/env python3
"""
Seed Tool Index with BidDeed.AI's existing tools
Converts static API_MEGA_LIBRARY.md into vector-searchable index
"""

import os
import asyncio
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tool_index.vector_store import index_tool

# BidDeed.AI Tool Definitions (from API_MEGA_LIBRARY.md and existing integrations)
BIDDEED_TOOLS = [
    # Data Sources
    {
        "tool_name": "realforeclose_scraper",
        "tool_description": "Scrape foreclosure auction listings from RealForeclose.com. Returns case numbers, addresses, plaintiff info, sale dates, and opening bids for Brevard County foreclosure auctions.",
        "mcp_server_name": "biddeed-scrapers",
        "category": "data_source"
    },
    {
        "tool_name": "bcpao_property_search",
        "tool_description": "Search Brevard County Property Appraiser (BCPAO) for property details including assessed value, legal description, owner info, and property photos.",
        "mcp_server_name": "biddeed-scrapers",
        "category": "data_source"
    },
    {
        "tool_name": "acclaimweb_lien_search",
        "tool_description": "Search AcclaimWeb for recorded documents including mortgages, liens, judgments, and satisfactions. Critical for lien priority analysis in foreclosure due diligence.",
        "mcp_server_name": "biddeed-scrapers",
        "category": "data_source"
    },
    {
        "tool_name": "realtdm_tax_search",
        "tool_description": "Search RealTDM for tax certificates on Brevard County properties. Returns certificate numbers, face amounts, interest rates, and redemption status.",
        "mcp_server_name": "biddeed-scrapers",
        "category": "data_source"
    },
    {
        "tool_name": "beca_scraper",
        "tool_description": "BECA V22 Scraper - Extract final judgments, opening bids, and property addresses from Brevard County clerk case documents with anti-bot detection bypass.",
        "mcp_server_name": "biddeed-scrapers",
        "category": "data_source"
    },
    {
        "tool_name": "census_demographics",
        "tool_description": "Fetch Census API demographic data for property zip codes. Returns median income, population, vacancy rates, and housing statistics for neighborhood analysis.",
        "mcp_server_name": "biddeed-analytics",
        "category": "data_source"
    },
    
    # Analytics & ML
    {
        "tool_name": "xgboost_third_party_predictor",
        "tool_description": "BidDeed.AI ML model predicting probability of third-party purchase at foreclosure auction. Uses 28 plaintiff patterns and historical auction data. 64.4% accuracy.",
        "mcp_server_name": "biddeed-ml",
        "category": "analytics"
    },
    {
        "tool_name": "max_bid_calculator",
        "tool_description": "Calculate maximum bid for foreclosure property using formula: (ARV×70%)-Repairs-$10K-MIN($25K,15%ARV). Returns BID/REVIEW/SKIP recommendation based on bid/judgment ratio.",
        "mcp_server_name": "biddeed-analytics",
        "category": "analytics"
    },
    {
        "tool_name": "lien_priority_analyzer",
        "tool_description": "Analyze lien priority to determine which liens survive foreclosure. Detects HOA foreclosures where senior mortgages survive. Critical for avoiding DO_NOT_BID scenarios.",
        "mcp_server_name": "biddeed-analytics",
        "category": "analytics"
    },
    {
        "tool_name": "repair_estimator",
        "tool_description": "Estimate property repair costs based on condition indicators, property age, size, and comparable rehab data. Returns low/medium/high estimates.",
        "mcp_server_name": "biddeed-analytics",
        "category": "analytics"
    },
    
    # Reports & Output
    {
        "tool_name": "generate_auction_report",
        "tool_description": "Generate one-page DOCX report for foreclosure property with BCPAO photo, ML predictions, lien analysis, max bid calculation, and BID/REVIEW/SKIP recommendation.",
        "mcp_server_name": "biddeed-reports",
        "category": "output"
    },
    {
        "tool_name": "decision_logger",
        "tool_description": "Log auction bid decision to Supabase with full audit trail including case number, decision, reasoning, ML score, and timestamp for compliance tracking.",
        "mcp_server_name": "biddeed-logging",
        "category": "output"
    },
    
    # Smart Router
    {
        "tool_name": "smart_router_v5",
        "tool_description": "Route LLM requests to optimal model based on task complexity. FREE: gemini-2.5-flash (1M context), ULTRA_CHEAP: deepseek-v3.2, PAID: claude-sonnet-4-5. Target 90% FREE tier.",
        "mcp_server_name": "biddeed-router",
        "category": "infrastructure"
    },
    
    # External APIs (from API_MEGA_LIBRARY.md)
    {
        "tool_name": "google_maps_geocoding",
        "tool_description": "Geocode property addresses to lat/long coordinates. Used for neighborhood analysis and distance calculations.",
        "mcp_server_name": "google-maps",
        "category": "external_api"
    },
    {
        "tool_name": "zillow_zestimate",
        "tool_description": "Fetch Zillow Zestimate for property valuation reference. Note: Use as sanity check only, not primary ARV source.",
        "mcp_server_name": "zillow-api",
        "category": "external_api"
    },
    
    # Life OS Tools
    {
        "tool_name": "swimcloud_times",
        "tool_description": "Fetch competitive swim times from SwimCloud for Michael Shapira (ID: 3250085) and rivals. Returns event times, power index, improvement trends.",
        "mcp_server_name": "life-os-michael",
        "category": "life_os"
    },
    {
        "tool_name": "nutrition_logger",
        "tool_description": "Log Michael's ketogenic diet compliance. Tracks macros, meal timing, and Shabbat carb modifications (Mon-Thu strict keto, Fri-Sun moderate).",
        "mcp_server_name": "life-os-michael",
        "category": "life_os"
    },
    {
        "tool_name": "task_tracker",
        "tool_description": "ADHD-optimized task tracking for Ariel. States: INITIATED→SOLUTION_PROVIDED→IN_PROGRESS→COMPLETED/ABANDONED. Detects context switches and triggers interventions.",
        "mcp_server_name": "life-os-ariel",
        "category": "life_os"
    }
]


async def seed_tools():
    """Seed all BidDeed.AI tools into vector index"""
    
    print(f"🔧 Seeding {len(BIDDEED_TOOLS)} tools into vector index...")
    
    success_count = 0
    for tool in BIDDEED_TOOLS:
        result = await index_tool(
            tool_name=tool["tool_name"],
            tool_description=tool["tool_description"],
            mcp_server_name=tool.get("mcp_server_name"),
            category=tool.get("category"),
            metadata={"source": "API_MEGA_LIBRARY", "version": "v1"}
        )
        
        if result.get("success"):
            print(f"  ✅ {tool['tool_name']}")
            success_count += 1
        else:
            print(f"  ❌ {tool['tool_name']}: {result}")
    
    print(f"\n📊 Seeded {success_count}/{len(BIDDEED_TOOLS)} tools")
    
    # Test discovery
    print("\n🔍 Testing tool discovery...")
    from tool_index.vector_store import discover_tools
    
    test_queries = [
        "find foreclosure auction listings",
        "analyze property liens",
        "calculate maximum bid price",
        "track swimming times"
    ]
    
    for query in test_queries:
        results = await discover_tools(query, limit=3)
        print(f"\n  Query: '{query}'")
        for r in results:
            print(f"    → {r.get('tool_name')} ({r.get('similarity', 0):.2f})")


if __name__ == "__main__":
    asyncio.run(seed_tools())
