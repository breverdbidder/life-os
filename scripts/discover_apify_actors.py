#!/usr/bin/env python3
"""Discover new Apify actors relevant to Life OS / BidDeed.AI."""
import httpx
import json
import os
from datetime import datetime

APIFY_STORE_API = "https://api.apify.com/v2/store"
SEARCH_TERMS = ["real estate", "costco", "walmart", "grocery", "foreclosure", "zillow"]
KNOWN_ACTORS = {"tri_angle/costco-fast-product-scraper", "epctex/realtor-scraper", "apify/ai-web-agent"}

def search_apify_store(query):
    try:
        params = {"search": query, "limit": 10, "sortBy": "popularity"}
        resp = httpx.get(APIFY_STORE_API, params=params, timeout=30)
        if resp.status_code != 200:
            return []
        actors = []
        for item in resp.json().get("data", {}).get("items", []):
            actor_id = f"{item.get('username','')}/{item.get('name','')}"
            if actor_id not in KNOWN_ACTORS:
                actors.append({
                    "id": actor_id,
                    "name": item.get("title", item.get("name", "")),
                    "description": item.get("description", "")[:150],
                    "url": f"https://apify.com/{actor_id}",
                    "runs": item.get("stats", {}).get("totalRuns", 0),
                    "discovered": datetime.now().isoformat()
                })
        return actors
    except:
        return []

def discover_new_apify_actors():
    all_actors = []
    for term in SEARCH_TERMS:
        all_actors.extend(search_apify_store(term))
    seen = set()
    unique = [a for a in all_actors if a["id"] not in seen and not seen.add(a["id"])]
    return sorted(unique, key=lambda x: x["runs"], reverse=True)[:15]

if __name__ == "__main__":
    print(json.dumps(discover_new_apify_actors(), indent=2))
