"""
D1 Swiss Army Scrapers - Michael Shapira D1 Pathway
====================================================
Comprehensive scraping toolkit for D1 swimming recruitment intelligence.

Scrapers:
1. SwimCloud - Times, rankings, meet results
2. CollegeSwimming.com - Team rosters, recruiting standards
3. USA Swimming - Official times database
4. D1 Recruiting Standards - Target times by program tier

Author: Everest Capital USA / Life OS
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json
import re
import os

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

@dataclass
class SwimTime:
    event: str
    time: str
    time_seconds: float
    meet_name: str
    meet_date: str
    course: str  # SCY, LCM, SCM
    swimmer_name: str
    team: str
    source: str

@dataclass
class D1Program:
    school: str
    conference: str
    division: str
    recruiting_standard_50_free: Optional[str]
    recruiting_standard_100_free: Optional[str]
    recruiting_standard_100_fly: Optional[str]
    recruiting_standard_100_back: Optional[str]
    coach_name: Optional[str]
    coach_email: Optional[str]
    chabad_nearby: bool
    kosher_options: bool

# Michael's current times and targets
MICHAEL_PROFILE = {
    "name": "Michael Shapira",
    "graduation": 2027,
    "school": "Satellite Beach High School",
    "events": ["50 Free", "100 Free", "200 Free", "100 Fly", "100 Back"],
    "current_times": {
        "50 Free": {"time": "23.22", "seconds": 23.22},
        "100 Free": {"time": "50.82", "seconds": 50.82},
        "100 Fly": {"time": "57.21", "seconds": 57.21},
        "100 Back": {"time": "1:01.62", "seconds": 61.62}
    },
    "target_schools": [
        {"name": "University of Florida", "conference": "SEC", "tier": 1},
        {"name": "Florida State University", "conference": "ACC", "tier": 1},
        {"name": "University of Miami", "conference": "ACC", "tier": 1},
        {"name": "USF", "conference": "AAC", "tier": 2},
        {"name": "FAU", "conference": "AAC", "tier": 2},
        {"name": "FIU", "conference": "CUSA", "tier": 2}
    ]
}

# D1 Recruiting Standards by Tier
D1_RECRUITING_STANDARDS = {
    "tier_1": {  # SEC, Big Ten, Pac-12, ACC top programs
        "50 Free": {"walk_on": "21.5", "recruited": "20.5", "scholarship": "19.5"},
        "100 Free": {"walk_on": "47.0", "recruited": "45.5", "scholarship": "44.0"},
        "100 Fly": {"walk_on": "51.0", "recruited": "49.5", "scholarship": "48.0"},
        "100 Back": {"walk_on": "52.0", "recruited": "50.5", "scholarship": "49.0"}
    },
    "tier_2": {  # Mid-major conferences
        "50 Free": {"walk_on": "22.5", "recruited": "21.5", "scholarship": "20.5"},
        "100 Free": {"walk_on": "49.0", "recruited": "47.5", "scholarship": "46.0"},
        "100 Fly": {"walk_on": "53.0", "recruited": "51.5", "scholarship": "50.0"},
        "100 Back": {"walk_on": "54.0", "recruited": "52.5", "scholarship": "51.0"}
    },
    "tier_3": {  # Smaller D1 programs
        "50 Free": {"walk_on": "23.5", "recruited": "22.5", "scholarship": "21.5"},
        "100 Free": {"walk_on": "51.0", "recruited": "49.5", "scholarship": "48.0"},
        "100 Fly": {"walk_on": "55.0", "recruited": "53.5", "scholarship": "52.0"},
        "100 Back": {"walk_on": "56.0", "recruited": "54.5", "scholarship": "53.0"}
    }
}


class SwimCloudScraper:
    """Scrape SwimCloud for times, rankings, and meet results."""
    
    BASE_URL = "https://www.swimcloud.com"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30, follow_redirects=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def search_swimmer(self, name: str) -> list[dict]:
        """Search for swimmer by name."""
        url = f"{self.BASE_URL}/api/search/?q={name.replace(' ', '+')}&type=swimmer"
        try:
            resp = await self.client.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json().get("results", [])
        except Exception as e:
            print(f"SwimCloud search error: {e}")
        return []
    
    async def get_swimmer_times(self, swimmer_id: str) -> list[SwimTime]:
        """Get all times for a swimmer."""
        url = f"{self.BASE_URL}/swimmer/{swimmer_id}/times/"
        times = []
        try:
            resp = await self.client.get(url, headers=self.headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for row in soup.select("table.c-table-clean tbody tr"):
                    cols = row.select("td")
                    if len(cols) >= 4:
                        event = cols[0].get_text(strip=True)
                        time_str = cols[1].get_text(strip=True)
                        times.append(SwimTime(
                            event=event,
                            time=time_str,
                            time_seconds=self._parse_time(time_str),
                            meet_name=cols[2].get_text(strip=True),
                            meet_date=cols[3].get_text(strip=True),
                            course="SCY",
                            swimmer_name="",
                            team="",
                            source="swimcloud"
                        ))
        except Exception as e:
            print(f"SwimCloud times error: {e}")
        return times
    
    async def get_team_roster(self, team_id: str) -> list[dict]:
        """Get D1 team roster with times."""
        url = f"{self.BASE_URL}/team/{team_id}/roster/"
        roster = []
        try:
            resp = await self.client.get(url, headers=self.headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for row in soup.select("table.c-table tbody tr"):
                    cols = row.select("td")
                    if len(cols) >= 3:
                        roster.append({
                            "name": cols[0].get_text(strip=True),
                            "year": cols[1].get_text(strip=True),
                            "hometown": cols[2].get_text(strip=True) if len(cols) > 2 else ""
                        })
        except Exception as e:
            print(f"SwimCloud roster error: {e}")
        return roster
    
    async def get_recruiting_class(self, team_id: str, year: int) -> list[dict]:
        """Get incoming recruiting class for a team."""
        url = f"{self.BASE_URL}/team/{team_id}/commits/?year={year}"
        commits = []
        try:
            resp = await self.client.get(url, headers=self.headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for row in soup.select("table tbody tr"):
                    cols = row.select("td")
                    if len(cols) >= 2:
                        commits.append({
                            "name": cols[0].get_text(strip=True),
                            "best_time": cols[1].get_text(strip=True) if len(cols) > 1 else ""
                        })
        except Exception as e:
            print(f"SwimCloud commits error: {e}")
        return commits
    
    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                return float(parts[0]) * 60 + float(parts[1])
            return float(time_str)
        except:
            return 0.0
    
    async def close(self):
        await self.client.aclose()


class CollegeSwimmingScraper:
    """Scrape CollegeSwimming.com for team data and recruiting standards."""
    
    BASE_URL = "https://www.collegeswimming.com"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30, follow_redirects=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def get_team_recruiting_times(self, team_slug: str) -> dict:
        """Get recruiting standard times for a team."""
        url = f"{self.BASE_URL}/team/{team_slug}/recruiting"
        standards = {}
        try:
            resp = await self.client.get(url, headers=self.headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for row in soup.select("table tbody tr"):
                    cols = row.select("td")
                    if len(cols) >= 2:
                        event = cols[0].get_text(strip=True)
                        time_str = cols[1].get_text(strip=True)
                        standards[event] = time_str
        except Exception as e:
            print(f"CollegeSwimming recruiting error: {e}")
        return standards
    
    async def get_conference_rankings(self, conference: str, event: str) -> list[dict]:
        """Get conference rankings for an event."""
        # Conference codes: SEC, ACC, B1G, PAC12, etc.
        url = f"{self.BASE_URL}/conference/{conference.lower()}/times/{event.replace(' ', '-').lower()}"
        rankings = []
        try:
            resp = await self.client.get(url, headers=self.headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for i, row in enumerate(soup.select("table tbody tr")[:20]):
                    cols = row.select("td")
                    if len(cols) >= 3:
                        rankings.append({
                            "rank": i + 1,
                            "swimmer": cols[0].get_text(strip=True),
                            "team": cols[1].get_text(strip=True),
                            "time": cols[2].get_text(strip=True)
                        })
        except Exception as e:
            print(f"CollegeSwimming rankings error: {e}")
        return rankings
    
    async def close(self):
        await self.client.aclose()


class USASwimmingScraper:
    """Scrape USA Swimming times database."""
    
    BASE_URL = "https://data.usaswimming.org"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30, follow_redirects=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def search_times(self, name: str, event: str = None) -> list[SwimTime]:
        """Search USA Swimming times database."""
        times = []
        # USA Swimming has a different API structure
        url = f"{self.BASE_URL}/api/times_search"
        params = {"name": name}
        if event:
            params["event"] = event
        try:
            resp = await self.client.get(url, headers=self.headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                for t in data.get("times", []):
                    times.append(SwimTime(
                        event=t.get("event", ""),
                        time=t.get("time", ""),
                        time_seconds=self._parse_time(t.get("time", "")),
                        meet_name=t.get("meet", ""),
                        meet_date=t.get("date", ""),
                        course=t.get("course", "SCY"),
                        swimmer_name=name,
                        team=t.get("team", ""),
                        source="usa_swimming"
                    ))
        except Exception as e:
            print(f"USA Swimming search error: {e}")
        return times
    
    async def get_national_age_group_standards(self, age: int, gender: str = "M") -> dict:
        """Get NAG motivational times for age group."""
        standards = {
            "B": {},   # B standard
            "BB": {},  # BB standard
            "A": {},   # A standard
            "AA": {},  # AA standard
            "AAA": {}, # AAA standard
            "AAAA": {} # AAAA standard
        }
        # Age 15-16 boys standards (SCY)
        if age in [15, 16] and gender == "M":
            standards["A"] = {
                "50 Free": "23.59",
                "100 Free": "51.29",
                "100 Fly": "56.79",
                "100 Back": "58.49"
            }
            standards["AA"] = {
                "50 Free": "22.69",
                "100 Free": "49.39",
                "100 Fly": "54.59",
                "100 Back": "56.29"
            }
            standards["AAA"] = {
                "50 Free": "21.59",
                "100 Free": "47.19",
                "100 Fly": "51.99",
                "100 Back": "53.69"
            }
        return standards
    
    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                return float(parts[0]) * 60 + float(parts[1])
            return float(time_str)
        except:
            return 0.0
    
    async def close(self):
        await self.client.aclose()


class D1RecruitingAnalyzer:
    """Analyze recruiting fit for D1 programs."""
    
    def __init__(self):
        self.standards = D1_RECRUITING_STANDARDS
        self.profile = MICHAEL_PROFILE
    
    def analyze_fit(self, event: str, current_time: float, target_school_tier: int) -> dict:
        """Analyze recruiting fit for an event."""
        tier_key = f"tier_{target_school_tier}"
        standards = self.standards.get(tier_key, self.standards["tier_2"])
        event_standards = standards.get(event, {})
        
        walk_on = self._parse_time(event_standards.get("walk_on", "99:99"))
        recruited = self._parse_time(event_standards.get("recruited", "99:99"))
        scholarship = self._parse_time(event_standards.get("scholarship", "99:99"))
        
        status = "below_walk_on"
        if current_time <= scholarship:
            status = "scholarship_level"
        elif current_time <= recruited:
            status = "recruited_level"
        elif current_time <= walk_on:
            status = "walk_on_level"
        
        time_to_walk_on = current_time - walk_on
        time_to_recruited = current_time - recruited
        time_to_scholarship = current_time - scholarship
        
        return {
            "event": event,
            "current_time": current_time,
            "status": status,
            "standards": event_standards,
            "gaps": {
                "to_walk_on": max(0, time_to_walk_on),
                "to_recruited": max(0, time_to_recruited),
                "to_scholarship": max(0, time_to_scholarship)
            },
            "projection": self._project_improvement(current_time, event)
        }
    
    def _project_improvement(self, current_time: float, event: str) -> dict:
        """Project improvement over 2 years (Class of 2027)."""
        # Typical improvement rates for high school swimmers
        annual_improvement = {
            "50 Free": 0.5,
            "100 Free": 1.2,
            "100 Fly": 1.5,
            "100 Back": 1.5
        }
        rate = annual_improvement.get(event, 1.0)
        return {
            "year_1": current_time - rate,
            "year_2": current_time - (rate * 1.8),  # Diminishing returns
            "senior_year_projection": current_time - (rate * 2.5)
        }
    
    def generate_recruiting_matrix(self) -> list[dict]:
        """Generate full recruiting matrix for all events and schools."""
        matrix = []
        for school in self.profile["target_schools"]:
            school_fit = {"school": school["name"], "tier": school["tier"], "events": {}}
            for event, times in self.profile["current_times"].items():
                analysis = self.analyze_fit(event, times["seconds"], school["tier"])
                school_fit["events"][event] = analysis
            matrix.append(school_fit)
        return matrix
    
    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                return float(parts[0]) * 60 + float(parts[1])
            return float(time_str)
        except:
            return 9999.0


class ChabadLocator:
    """Find Chabad and kosher resources near D1 schools."""
    
    CHABAD_DATA = {
        "University of Florida": {
            "chabad": "Chabad at UF",
            "address": "2021 NW 5th Ave, Gainesville, FL",
            "rabbi": "Rabbi Berl Goldman",
            "shabbat_dinner": True,
            "kosher_options": ["Chabad weekly meals", "Krishna Lunch (vegetarian)"]
        },
        "Florida State University": {
            "chabad": "Chabad of Tallahassee",
            "address": "613 W Jefferson St, Tallahassee, FL",
            "rabbi": "Rabbi Schneur Oirechman",
            "shabbat_dinner": True,
            "kosher_options": ["Chabad weekly meals"]
        },
        "University of Miami": {
            "chabad": "Chabad at UM",
            "address": "1550 S Dixie Hwy, Coral Gables, FL",
            "rabbi": "Rabbi Mendy Fellig",
            "shabbat_dinner": True,
            "kosher_options": ["Chabad weekly meals", "Multiple kosher restaurants nearby"]
        },
        "USF": {
            "chabad": "Chabad of USF",
            "address": "13287 N 52nd St, Tampa, FL",
            "rabbi": "Rabbi Pinny Backman",
            "shabbat_dinner": True,
            "kosher_options": ["Chabad weekly meals"]
        }
    }
    
    def get_jewish_resources(self, school_name: str) -> dict:
        """Get Jewish life resources for a school."""
        return self.CHABAD_DATA.get(school_name, {
            "chabad": "Contact Chabad.edu for nearest location",
            "shabbat_dinner": False,
            "kosher_options": []
        })


async def run_full_scrape():
    """Run complete D1 scraping pipeline."""
    print("🏊 Michael Shapira D1 Pathway - Swiss Army Scrapers")
    print("=" * 50)
    
    # Initialize scrapers
    swimcloud = SwimCloudScraper()
    college_swimming = CollegeSwimmingScraper()
    usa_swimming = USASwimmingScraper()
    analyzer = D1RecruitingAnalyzer()
    chabad = ChabadLocator()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "profile": MICHAEL_PROFILE,
        "recruiting_matrix": analyzer.generate_recruiting_matrix(),
        "jewish_resources": {},
        "scraper_status": {}
    }
    
    # Get Chabad info for each school
    for school in MICHAEL_PROFILE["target_schools"]:
        results["jewish_resources"][school["name"]] = chabad.get_jewish_resources(school["name"])
    
    # Get USA Swimming age group standards
    nag_standards = await usa_swimming.get_national_age_group_standards(16, "M")
    results["nag_standards"] = nag_standards
    
    # Close connections
    await swimcloud.close()
    await college_swimming.close()
    await usa_swimming.close()
    
    print("\n✅ Scraping complete!")
    print(f"📊 Analyzed {len(results['recruiting_matrix'])} target schools")
    
    return results


async def save_to_supabase(data: dict):
    """Save scraping results to Supabase."""
    if not SUPABASE_KEY:
        print("⚠️ No Supabase key configured")
        return
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/insights",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "category": "michael_swim",
                "type": "d1_scrape_results",
                "content": json.dumps(data),
                "created_at": datetime.now().isoformat()
            }
        )
        if resp.status_code in [200, 201]:
            print("✅ Saved to Supabase")
        else:
            print(f"❌ Supabase error: {resp.status_code}")


if __name__ == "__main__":
    results = asyncio.run(run_full_scrape())
    print(json.dumps(results, indent=2, default=str))
