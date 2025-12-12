#!/usr/bin/env python3
"""
SwimCloud Scraper for Michael Shapira and Satellite Beach HS
Uses Firecrawl for JavaScript rendering
"""

import os
import json
import re
import requests
from datetime import datetime

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Target swimmers
SWIMMERS = {
    "Michael Shapira": {
        "swimcloud_id": "3250085",
        "team": "Satellite Sr High School",
        "grad_year": 2027
    },
    "Sawyer Davis": {
        "swimcloud_id": None,  # Need to find
        "team": "Satellite Sr High School",
        "grad_year": None
    },
    "Bastian Soto": {
        "swimcloud_id": None,
        "team": "Satellite Sr High School",
        "grad_year": None
    }
}

# Satellite Beach HS team ID
SATELLITE_HS_TEAM_ID = "2276"

def scrape_with_firecrawl(url: str) -> dict:
    """Scrape a page using Firecrawl API"""
    if not FIRECRAWL_API_KEY:
        raise ValueError("FIRECRAWL_API_KEY not set")
    
    response = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "url": url,
            "formats": ["markdown", "html"],
            "waitFor": 3000,  # Wait for JS to load
            "timeout": 30000
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error scraping {url}: {response.status_code} - {response.text}")
        return None

def parse_swimmer_times(markdown: str) -> list:
    """Parse swim times from SwimCloud markdown"""
    times = []
    
    # Pattern for SCY times: Event name followed by time
    # Example: "50 Y Free 21.86" or "100 Y Free 48.80"
    event_patterns = [
        r"(\d+)\s*Y\s*(Free|Fly|Back|Breast|IM)\s+(\d+[:.]\d+\.?\d*)",
        r"(50|100|200|500|1000|1650)\s*(Freestyle|Butterfly|Backstroke|Breaststroke|Individual Medley)\s+(\d+[:.]\d+\.?\d*)"
    ]
    
    for pattern in event_patterns:
        matches = re.findall(pattern, markdown, re.IGNORECASE)
        for match in matches:
            distance, stroke, time = match
            times.append({
                "event": f"{distance} {stroke}",
                "time": time,
                "course": "SCY"
            })
    
    return times

def scrape_team_roster(team_id: str) -> list:
    """Scrape team roster from SwimCloud"""
    url = f"https://www.swimcloud.com/team/{team_id}/roster/"
    print(f"Scraping team roster: {url}")
    
    result = scrape_with_firecrawl(url)
    if not result or not result.get("data"):
        return []
    
    markdown = result["data"].get("markdown", "")
    
    # Parse swimmer names and IDs from roster
    swimmers = []
    # Pattern: /swimmer/ID/ and name
    swimmer_pattern = r'/swimmer/(\d+)/["\s>]+([A-Za-z]+,\s*[A-Za-z]+)'
    matches = re.findall(swimmer_pattern, result["data"].get("html", ""))
    
    for swimmer_id, name in matches:
        swimmers.append({
            "id": swimmer_id,
            "name": name
        })
    
    return swimmers

def scrape_swimmer_profile(swimmer_id: str, swimmer_name: str) -> dict:
    """Scrape individual swimmer profile and times"""
    url = f"https://www.swimcloud.com/swimmer/{swimmer_id}/times/"
    print(f"Scraping swimmer: {swimmer_name} ({url})")
    
    result = scrape_with_firecrawl(url)
    if not result or not result.get("data"):
        return None
    
    markdown = result["data"].get("markdown", "")
    html = result["data"].get("html", "")
    
    times = parse_swimmer_times(markdown)
    
    return {
        "swimmer_id": swimmer_id,
        "name": swimmer_name,
        "times": times,
        "raw_markdown": markdown[:5000],  # First 5k chars for debugging
        "scraped_at": datetime.utcnow().isoformat()
    }

def save_to_supabase(data: dict, table: str = "michael_swim") -> bool:
    """Save data to Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase credentials not set, saving locally")
        return False
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json=data
    )
    
    return response.status_code in [200, 201]

def main():
    print("=" * 60)
    print("SwimCloud Scraper - Michael Shapira & Satellite Beach HS")
    print("=" * 60)
    
    results = []
    
    # 1. Scrape Michael's profile
    michael_data = scrape_swimmer_profile(
        SWIMMERS["Michael Shapira"]["swimcloud_id"],
        "Michael Shapira"
    )
    if michael_data:
        results.append(michael_data)
        print(f"\n✅ Michael Shapira - Found {len(michael_data.get('times', []))} times")
        for t in michael_data.get("times", []):
            print(f"   {t['event']}: {t['time']}")
    
    # 2. Scrape team roster to find other swimmers
    print("\n📋 Fetching Satellite Beach HS roster...")
    roster = scrape_team_roster(SATELLITE_HS_TEAM_ID)
    print(f"   Found {len(roster)} swimmers on roster")
    
    # 3. Look for specific competitors
    for name in ["Sawyer Davis", "Bastian Soto", "Sawyer Hackett"]:
        for swimmer in roster:
            if name.lower() in swimmer.get("name", "").lower():
                swimmer_data = scrape_swimmer_profile(swimmer["id"], name)
                if swimmer_data:
                    results.append(swimmer_data)
                    print(f"\n✅ {name} - Found {len(swimmer_data.get('times', []))} times")
                break
    
    # Save results
    output_file = "swimcloud_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "scraped_at": datetime.utcnow().isoformat(),
            "team": "Satellite Sr High School",
            "team_id": SATELLITE_HS_TEAM_ID,
            "swimmers": results
        }, f, indent=2)
    
    print(f"\n📁 Results saved to {output_file}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
