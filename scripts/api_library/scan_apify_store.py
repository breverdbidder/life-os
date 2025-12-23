#!/usr/bin/env python3
"""
Scan Apify Store for new actors relevant to BidDeed.AI and Life OS
"""

import argparse
import json
import os
import requests
from datetime import datetime, timedelta

APIFY_STORE_API = "https://api.apify.com/v2/store"

# Categories we care about
RELEVANT_CATEGORIES = {
    "real-estate": ["real estate", "property", "zillow", "redfin", "mls", "foreclosure"],
    "e-commerce": ["costco", "walmart", "amazon", "kroger", "grocery", "shopping"],
    "automation": ["scraper", "crawler", "automation", "workflow"],
    "ai": ["ai", "llm", "gpt", "claude", "mcp", "agent"],
    "social": ["instagram", "tiktok", "youtube", "linkedin", "twitter"],
    "data": ["census", "government", "public records"]
}

def get_apify_actors(category_keywords: list, days_back: int = 30) -> list:
    """Fetch actors from Apify store matching keywords"""
    actors = []
    
    for keyword in category_keywords:
        try:
            response = requests.get(
                f"{APIFY_STORE_API}",
                params={
                    "search": keyword,
                    "limit": 50,
                    "sortBy": "popularity"
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                for actor in data.get("data", {}).get("items", []):
                    # Check if recently updated
                    modified = actor.get("modifiedAt", "")
                    if modified:
                        mod_date = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                        if mod_date > datetime.now(mod_date.tzinfo) - timedelta(days=days_back):
                            actors.append({
                                "name": actor.get("name"),
                                "title": actor.get("title"),
                                "description": actor.get("description", "")[:200],
                                "url": f"https://apify.com/{actor.get('username')}/{actor.get('name')}",
                                "username": actor.get("username"),
                                "stats": {
                                    "runs": actor.get("stats", {}).get("totalRuns", 0),
                                    "users": actor.get("stats", {}).get("totalUsers", 0)
                                },
                                "modified": modified,
                                "source": "apify",
                                "keyword": keyword
                            })
        except Exception as e:
            print(f"Error fetching {keyword}: {e}")
    
    # Deduplicate by URL
    seen = set()
    unique_actors = []
    for actor in actors:
        if actor["url"] not in seen:
            seen.add(actor["url"])
            unique_actors.append(actor)
    
    return unique_actors

def main():
    parser = argparse.ArgumentParser(description="Scan Apify Store for new actors")
    parser.add_argument("--categories", type=str, default="all", help="Comma-separated categories")
    parser.add_argument("--output", type=str, required=True, help="Output JSON file")
    parser.add_argument("--days", type=int, default=30, help="Days back to scan")
    args = parser.parse_args()
    
    # Determine which categories to scan
    if args.categories == "all":
        categories = RELEVANT_CATEGORIES
    else:
        categories = {k: v for k, v in RELEVANT_CATEGORIES.items() if k in args.categories.split(",")}
    
    all_actors = []
    for category, keywords in categories.items():
        print(f"Scanning category: {category}")
        actors = get_apify_actors(keywords, args.days)
        for actor in actors:
            actor["category"] = category
        all_actors.extend(actors)
        print(f"  Found {len(actors)} actors")
    
    # Sort by popularity
    all_actors.sort(key=lambda x: x["stats"]["runs"], reverse=True)
    
    # Save results
    with open(args.output, "w") as f:
        json.dump({
            "scan_date": datetime.now().isoformat(),
            "total_found": len(all_actors),
            "actors": all_actors
        }, f, indent=2)
    
    print(f"\nTotal: {len(all_actors)} actors saved to {args.output}")
    
    # Output for GitHub Actions
    print(f"::set-output name=count::{len(all_actors)}")

if __name__ == "__main__":
    main()
