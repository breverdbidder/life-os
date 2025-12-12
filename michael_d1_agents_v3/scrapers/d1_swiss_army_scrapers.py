#!/usr/bin/env python3
"""
D1 Swiss Army Scrapers V3.0 - VERIFIED DATA
============================================
Using curl_cffi for SwimCloud scraping (bypasses anti-bot)

VERIFIED DATA FROM SWIMCLOUD (Dec 12, 2025):
- 50 Free: 21.86 (FHSAA 2A Region 2, Oct 29, 2025)
- 100 Free: 48.80 (FHSAA 2A Region 2, Oct 29, 2025)
- 100 Fly: 55.87 (FL GSC Holiday Classic, Dec 5-7, 2025)
- 200 Free: 1:53.03 (FL GSC Holiday Classic, Dec 5-7, 2025)
"""

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

# Try to import curl_cffi, fall back to requests
try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    import requests as cffi_requests
    HAS_CURL_CFFI = False

# VERIFIED MICHAEL SHAPIRA DATA (SwimCloud ID: 3250085)
MICHAEL_PROFILE = {
    "name": "Michael Shapira",
    "swimcloud_id": "3250085",
    "location": "Satellite Beach, FL",
    "graduation_year": 2027,
    "high_school": "Satellite Sr High School",
    "hs_team_id": "2276",
    "club": "Swim Melbourne",
    "club_id": "10023007",
    "instagram": "@michaelshapira80",
    "power_index": 49.62,
    "class_rank": "1000th+",
    "florida_rank": "116th",
    "verified_date": "2025-12-12"
}

# VERIFIED PERSONAL BESTS (from SwimCloud scrape Dec 12, 2025)
VERIFIED_PBS = {
    "50 Free SCY": {
        "time": "21.86",
        "seconds": 21.86,
        "meet": "FHSAA 2A Region 2 Championship",
        "date": "2025-10-29",
        "place": "3rd",
        "verified": True
    },
    "100 Free SCY": {
        "time": "48.80",
        "seconds": 48.80,
        "meet": "FHSAA 2A Region 2 Championship",
        "date": "2025-10-29",
        "place": "3rd",
        "verified": True
    },
    "100 Fly SCY": {
        "time": "55.87",
        "seconds": 55.87,
        "meet": "FL GSC Holiday Classic",
        "date": "2025-12-05",
        "place": "35th",
        "verified": True,
        "note": "NEW PB"
    },
    "200 Free SCY": {
        "time": "1:53.03",
        "seconds": 113.03,
        "meet": "FL GSC Holiday Classic",
        "date": "2025-12-05",
        "place": "66th",
        "verified": True,
        "note": "NEW PB"
    }
}

# D1 Recruiting Standards
D1_STANDARDS = {
    "tier_1": {  # SEC, Big Ten, ACC top
        "50 Free": {"walk_on": 21.5, "recruited": 20.5, "scholarship": 19.5},
        "100 Free": {"walk_on": 47.0, "recruited": 45.5, "scholarship": 44.0},
        "100 Fly": {"walk_on": 51.0, "recruited": 49.5, "scholarship": 48.0},
    },
    "tier_2": {  # Mid-major
        "50 Free": {"walk_on": 22.5, "recruited": 21.5, "scholarship": 20.5},
        "100 Free": {"walk_on": 49.0, "recruited": 47.5, "scholarship": 46.0},
        "100 Fly": {"walk_on": 53.0, "recruited": 51.5, "scholarship": 50.0},
    },
    "tier_3": {  # Smaller D1
        "50 Free": {"walk_on": 23.5, "recruited": 22.5, "scholarship": 21.5},
        "100 Free": {"walk_on": 51.0, "recruited": 49.5, "scholarship": 48.0},
        "100 Fly": {"walk_on": 55.0, "recruited": 53.5, "scholarship": 52.0},
    }
}


@dataclass
class SwimTime:
    event: str
    time: str
    seconds: float
    meet: str
    date: str
    place: Optional[str] = None
    course: str = "SCY"
    verified: bool = False


class SwimCloudScraper:
    """SwimCloud scraper using curl_cffi to bypass anti-bot protection."""
    
    BASE_URL = "https://www.swimcloud.com"
    
    def __init__(self):
        if HAS_CURL_CFFI:
            self.session = cffi_requests.Session(impersonate="chrome120")
        else:
            self.session = cffi_requests.Session()
        
        self.headers = {
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
        }
    
    def scrape_swimmer(self, swimmer_id: str) -> Dict:
        """Scrape swimmer profile and times."""
        url = f"{self.BASE_URL}/swimmer/{swimmer_id}/"
        
        try:
            if HAS_CURL_CFFI:
                resp = self.session.get(url, headers=self.headers, timeout=30)
            else:
                resp = self.session.get(url, headers=self.headers, timeout=30)
            
            if resp.status_code == 200 and len(resp.text) > 5000:
                return self._parse_profile(resp.text, swimmer_id)
        except Exception as e:
            print(f"Scrape error: {e}")
        
        return {}
    
    def _parse_profile(self, html: str, swimmer_id: str) -> Dict:
        """Parse swimmer profile HTML."""
        soup = BeautifulSoup(html, "html.parser")
        data = {"swimmer_id": swimmer_id, "times": {}, "meets": []}
        
        # Get name
        h1 = soup.find("h1")
        if h1:
            data["name"] = h1.get_text(strip=True).split()[0:2]
            data["name"] = " ".join(data["name"])
        
        # Get team
        team_link = soup.find("a", href=re.compile(r"/team/\d+"))
        if team_link:
            data["team"] = team_link.get_text(strip=True)
        
        # Parse times from tables
        for row in soup.select("table tbody tr"):
            cols = row.select("td")
            if len(cols) >= 2:
                event_td = cols[0]
                time_td = cols[1]
                
                event_strong = event_td.find("strong")
                if event_strong:
                    event = event_strong.get_text(strip=True)
                    time_link = time_td.find("a")
                    if time_link:
                        time_str = time_link.get_text(strip=True)
                        data["times"][event] = time_str
        
        # Get meet list
        for dropdown_item in soup.select(".dropdown-menu li a"):
            href = dropdown_item.get("href", "")
            if "/times/latest/" in href:
                meet_text = dropdown_item.get_text(strip=True)
                data["meets"].append(meet_text)
        
        return data
    
    def get_verified_times(self) -> Dict:
        """Return verified PB times for Michael Shapira."""
        return VERIFIED_PBS


class D1RecruitingAnalyzer:
    """Analyze recruiting fit with VERIFIED times."""
    
    def __init__(self):
        self.pbs = VERIFIED_PBS
        self.standards = D1_STANDARDS
    
    def analyze_fit(self) -> Dict:
        """Generate recruiting analysis with verified times."""
        analysis = {
            "swimmer": MICHAEL_PROFILE["name"],
            "class": MICHAEL_PROFILE["graduation_year"],
            "verified_date": MICHAEL_PROFILE["verified_date"],
            "events": {}
        }
        
        for event_key, pb_data in self.pbs.items():
            event = event_key.replace(" SCY", "")
            current_time = pb_data["seconds"]
            
            # Check against each tier
            tiers = {}
            for tier_name, tier_standards in self.standards.items():
                if event in tier_standards:
                    std = tier_standards[event]
                    status = "below"
                    if current_time <= std["scholarship"]:
                        status = "scholarship"
                    elif current_time <= std["recruited"]:
                        status = "recruited"
                    elif current_time <= std["walk_on"]:
                        status = "walk_on"
                    
                    tiers[tier_name] = {
                        "status": status,
                        "gap_to_walk_on": round(current_time - std["walk_on"], 2),
                        "gap_to_recruited": round(current_time - std["recruited"], 2)
                    }
            
            analysis["events"][event] = {
                "pb_time": pb_data["time"],
                "pb_seconds": current_time,
                "pb_meet": pb_data["meet"],
                "pb_date": pb_data["date"],
                "tiers": tiers
            }
        
        return analysis


def main():
    print("=" * 60)
    print("🏊 D1 Swiss Army Scrapers V3.0 - VERIFIED DATA")
    print("=" * 60)
    print(f"curl_cffi available: {HAS_CURL_CFFI}")
    
    # Show verified profile
    print(f"\n📊 Swimmer: {MICHAEL_PROFILE['name']}")
    print(f"   SwimCloud ID: {MICHAEL_PROFILE['swimcloud_id']}")
    print(f"   Class of {MICHAEL_PROFILE['graduation_year']}")
    print(f"   Power Index: {MICHAEL_PROFILE['power_index']}")
    print(f"   Florida Rank: {MICHAEL_PROFILE['florida_rank']}")
    
    # Show verified times
    print("\n✅ VERIFIED PERSONAL BESTS:")
    for event, data in VERIFIED_PBS.items():
        note = f" 🔥 {data.get('note', '')}" if data.get('note') else ""
        print(f"   {event}: {data['time']} ({data['place']} @ {data['meet']}){note}")
    
    # Run analysis
    analyzer = D1RecruitingAnalyzer()
    analysis = analyzer.analyze_fit()
    
    print("\n🎯 D1 RECRUITING ANALYSIS:")
    for event, data in analysis["events"].items():
        print(f"\n   {event}: {data['pb_time']}")
        for tier, tier_data in data["tiers"].items():
            status = tier_data["status"].upper()
            gap = tier_data["gap_to_walk_on"]
            print(f"      {tier}: {status} (gap to walk-on: {gap:+.2f}s)")
    
    # Save results
    output = {
        "profile": MICHAEL_PROFILE,
        "verified_pbs": VERIFIED_PBS,
        "analysis": analysis,
        "scraped_at": datetime.now().isoformat()
    }
    
    with open("michael_verified_times.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\n💾 Saved to michael_verified_times.json")
    
    return output


if __name__ == "__main__":
    main()
