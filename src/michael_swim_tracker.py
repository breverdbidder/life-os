"""
Michael Shapira D1 Swimming Tracker
Automated SwimCloud scraping for Life OS
Author: Ariel Shapira, Everest Capital USA
Version: 1.0.0
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

MICHAEL_CONFIG = {
    "name": "Michael Shapira",
    "dob": "2009-07-22",
    "age": 16,
    "graduation_year": 2027,
    "high_school": "Satellite Beach High School",
    "club_team": "Swim Melbourne",
    "club_team_id": 10023007,
    "gender": "M",
    "target_events": ["50 Free", "100 Free", "200 Free", "100 Fly", "100 Back"],
    "d1_target": True
}

# Event IDs mapping (SCY)
EVENT_IDS = {
    "50 Free": 150,
    "100 Free": 1100,
    "200 Free": 2100,
    "100 Fly": 1200,
    "100 Back": 1300,
    "50 Fly": 150,
    "200 IM": 2500
}

# D1 Recruiting Standards (approximate SCY times for mid-major D1)
D1_STANDARDS = {
    "50 Free": {"A_cut": 20.5, "B_cut": 21.5, "consider": 22.5},
    "100 Free": {"A_cut": 45.0, "B_cut": 47.0, "consider": 49.0},
    "200 Free": {"A_cut": 1*60+40, "B_cut": 1*60+45, "consider": 1*60+50},
    "100 Fly": {"A_cut": 50.0, "B_cut": 52.0, "consider": 54.0},
    "100 Back": {"A_cut": 50.0, "B_cut": 52.0, "consider": 55.0}
}

# Florida Swimming Southern Zone cuts
FL_ZONE_CUTS = {
    "50 Free": 22.29,
    "100 Free": 48.29,
    "200 Free": 105.79,  # 1:45.79
    "100 Fly": 52.29,
    "100 Back": 55.09
}

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ============================================
# SWIMCLOUD SCRAPER (Using SwimScraper patterns)
# ============================================

class SwimCloudScraper:
    """SwimCloud data extraction - based on SwimScraper package patterns"""
    
    BASE_URL = "https://www.swimcloud.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
    
    def get_team_roster(self, team_id: int, gender: str = "M", year: int = 2025) -> List[Dict]:
        """Get team roster from SwimCloud"""
        url = f"{self.BASE_URL}/team/{team_id}/roster/?page=1&gender={gender}&season_id="
        try:
            resp = self.session.get(url, timeout=30)
            if resp.status_code == 200:
                # Parse HTML for swimmer data
                return self._parse_roster(resp.text)
        except Exception as e:
            logger.error(f"Error fetching roster: {e}")
        return []
    
    def search_swimmer(self, name: str) -> Optional[Dict]:
        """Search for swimmer by name"""
        url = f"{self.BASE_URL}/search/?q={name.replace(' ', '+')}&swimmer=1"
        try:
            resp = self.session.get(url, timeout=30)
            if resp.status_code == 200:
                return self._parse_search_results(resp.text, name)
        except Exception as e:
            logger.error(f"Error searching swimmer: {e}")
        return None
    
    def get_swimmer_times(self, swimmer_id: int, event_id: Optional[int] = None) -> List[Dict]:
        """Get all times for a swimmer"""
        url = f"{self.BASE_URL}/swimmer/{swimmer_id}/times/"
        if event_id:
            url += f"?event={event_id}"
        try:
            resp = self.session.get(url, timeout=30)
            if resp.status_code == 200:
                return self._parse_swimmer_times(resp.text)
        except Exception as e:
            logger.error(f"Error fetching swimmer times: {e}")
        return []
    
    def get_swimmer_profile(self, swimmer_id: int) -> Optional[Dict]:
        """Get swimmer profile data"""
        url = f"{self.BASE_URL}/swimmer/{swimmer_id}/"
        try:
            resp = self.session.get(url, timeout=30)
            if resp.status_code == 200:
                return self._parse_swimmer_profile(resp.text)
        except Exception as e:
            logger.error(f"Error fetching swimmer profile: {e}")
        return None
    
    def _parse_roster(self, html: str) -> List[Dict]:
        """Parse roster HTML - extract swimmer names and IDs"""
        import re
        swimmers = []
        # Pattern: /swimmer/(\d+)/">([^<]+)</a>
        pattern = r'/swimmer/(\d+)/"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        for swimmer_id, name in matches:
            swimmers.append({
                "swimmer_id": int(swimmer_id),
                "name": name.strip()
            })
        return swimmers
    
    def _parse_search_results(self, html: str, target_name: str) -> Optional[Dict]:
        """Parse search results to find specific swimmer"""
        import re
        pattern = r'/swimmer/(\d+)/"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        for swimmer_id, name in matches:
            if target_name.lower() in name.lower():
                return {"swimmer_id": int(swimmer_id), "name": name.strip()}
        return None
    
    def _parse_swimmer_times(self, html: str) -> List[Dict]:
        """Parse swimmer times from HTML"""
        import re
        times = []
        # This is a simplified parser - real implementation would use BeautifulSoup
        # Pattern for time entries
        time_pattern = r'(\d{1,2}:?\d{2}\.\d{2})'
        event_pattern = r'(50|100|200|400|500|1000|1650)\s*(Free|Fly|Back|Breast|IM)'
        
        # Extract time data from HTML structure
        time_matches = re.findall(time_pattern, html)
        event_matches = re.findall(event_pattern, html)
        
        # Combine matches (simplified - would need proper HTML parsing)
        for i, time_str in enumerate(time_matches[:20]):  # Limit to first 20
            times.append({
                "time_str": time_str,
                "time_seconds": self._convert_time(time_str),
                "extracted_at": datetime.now(timezone.utc).isoformat()
            })
        return times
    
    def _parse_swimmer_profile(self, html: str) -> Optional[Dict]:
        """Parse swimmer profile data"""
        import re
        profile = {}
        
        # Extract Power Index if available
        pi_pattern = r'Power Index[:\s]*(\d+\.?\d*)'
        pi_match = re.search(pi_pattern, html)
        if pi_match:
            profile["power_index"] = float(pi_match.group(1))
        
        # Extract team
        team_pattern = r'/team/(\d+)/"[^>]*>([^<]+)</a>'
        team_match = re.search(team_pattern, html)
        if team_match:
            profile["team_id"] = int(team_match.group(1))
            profile["team_name"] = team_match.group(2).strip()
        
        return profile if profile else None
    
    @staticmethod
    def _convert_time(time_str: str) -> float:
        """Convert time string to seconds"""
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                return float(time_str)
        except:
            return 0.0


# ============================================
# D1 RECRUITING ANALYZER
# ============================================

class D1RecruitingAnalyzer:
    """Analyze swimmer times against D1 recruiting standards"""
    
    def __init__(self, swimmer_config: Dict):
        self.config = swimmer_config
        self.scraper = SwimCloudScraper()
    
    def analyze_d1_readiness(self, times: Dict[str, float]) -> Dict:
        """Analyze current times against D1 standards"""
        analysis = {
            "swimmer": self.config["name"],
            "graduation_year": self.config["graduation_year"],
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "events": {},
            "overall_d1_score": 0,
            "recommendation": ""
        }
        
        total_score = 0
        events_analyzed = 0
        
        for event, time_seconds in times.items():
            if event in D1_STANDARDS:
                standards = D1_STANDARDS[event]
                fl_cut = FL_ZONE_CUTS.get(event, 999)
                
                event_analysis = {
                    "current_time": time_seconds,
                    "current_time_str": self._seconds_to_time_str(time_seconds),
                    "d1_a_cut": standards["A_cut"],
                    "d1_b_cut": standards["B_cut"],
                    "d1_consider": standards["consider"],
                    "fl_zone_cut": fl_cut,
                    "gap_to_b_cut": time_seconds - standards["B_cut"],
                    "gap_to_fl_zone": time_seconds - fl_cut,
                    "d1_tier": self._calculate_tier(time_seconds, standards),
                    "fl_zone_qualified": time_seconds <= fl_cut
                }
                
                # Score: 100 if at A cut, 75 at B cut, 50 at consider, 0 if slower
                if time_seconds <= standards["A_cut"]:
                    event_analysis["d1_score"] = 100
                elif time_seconds <= standards["B_cut"]:
                    event_analysis["d1_score"] = 75
                elif time_seconds <= standards["consider"]:
                    event_analysis["d1_score"] = 50
                else:
                    # Calculate partial score based on gap
                    gap = time_seconds - standards["consider"]
                    event_analysis["d1_score"] = max(0, 50 - (gap * 10))
                
                total_score += event_analysis["d1_score"]
                events_analyzed += 1
                analysis["events"][event] = event_analysis
        
        if events_analyzed > 0:
            analysis["overall_d1_score"] = round(total_score / events_analyzed, 1)
        
        # Generate recommendation
        score = analysis["overall_d1_score"]
        if score >= 75:
            analysis["recommendation"] = "STRONG D1 CANDIDATE - Target Power 5 & mid-major programs"
        elif score >= 50:
            analysis["recommendation"] = "D1 POTENTIAL - Focus on time drops, target mid-major D1"
        elif score >= 25:
            analysis["recommendation"] = "DEVELOPING - D2/D3 now, D1 walkOn possible with improvement"
        else:
            analysis["recommendation"] = "BUILDING FOUNDATION - Focus on technique and training"
        
        return analysis
    
    def _calculate_tier(self, time: float, standards: Dict) -> str:
        """Calculate D1 recruiting tier"""
        if time <= standards["A_cut"]:
            return "TIER_1_A_CUT"
        elif time <= standards["B_cut"]:
            return "TIER_2_B_CUT"
        elif time <= standards["consider"]:
            return "TIER_3_CONSIDER"
        else:
            return "TIER_4_DEVELOPING"
    
    @staticmethod
    def _seconds_to_time_str(seconds: float) -> str:
        """Convert seconds to MM:SS.ss format"""
        if seconds >= 60:
            mins = int(seconds // 60)
            secs = seconds % 60
            return f"{mins}:{secs:05.2f}"
        return f"{seconds:.2f}"


# ============================================
# SUPABASE INTEGRATION
# ============================================

class SupabaseClient:
    """Supabase client for storing swim data"""
    
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def insert_swim_times(self, swimmer_name: str, times: List[Dict]) -> bool:
        """Insert swim times to michael_swim_times table"""
        endpoint = f"{self.url}/rest/v1/michael_swim_times"
        
        records = []
        for t in times:
            records.append({
                "swimmer_name": swimmer_name,
                "event": t.get("event", "Unknown"),
                "time_seconds": t.get("time_seconds", 0),
                "time_str": t.get("time_str", ""),
                "meet_name": t.get("meet_name", ""),
                "meet_date": t.get("meet_date", ""),
                "pool_type": t.get("pool_type", "SCY"),
                "improvement": t.get("improvement", 0),
                "source": "swimcloud",
                "scraped_at": datetime.now(timezone.utc).isoformat()
            })
        
        try:
            resp = requests.post(endpoint, headers=self.headers, json=records)
            if resp.status_code in [200, 201]:
                logger.info(f"✅ Inserted {len(records)} swim times to Supabase")
                return True
            else:
                logger.error(f"❌ Supabase insert failed: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Supabase error: {e}")
            return False
    
    def insert_d1_analysis(self, analysis: Dict) -> bool:
        """Insert D1 recruiting analysis to insights table"""
        endpoint = f"{self.url}/rest/v1/insights"
        
        record = {
            "category": "michael_swim",
            "subcategory": "d1_analysis",
            "title": f"D1 Recruiting Analysis - {analysis['swimmer']}",
            "content": json.dumps(analysis),
            "tags": ["swimming", "d1", "recruiting", "michael"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            resp = requests.post(endpoint, headers=self.headers, json=record)
            if resp.status_code in [200, 201]:
                logger.info(f"✅ D1 analysis saved to Supabase insights")
                return True
            else:
                logger.error(f"❌ Supabase insert failed: {resp.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Supabase error: {e}")
            return False
    
    def get_latest_times(self, swimmer_name: str) -> List[Dict]:
        """Get latest times from Supabase"""
        endpoint = f"{self.url}/rest/v1/michael_swim_times"
        params = {
            "swimmer_name": f"eq.{swimmer_name}",
            "order": "scraped_at.desc",
            "limit": 50
        }
        
        try:
            resp = requests.get(endpoint, headers=self.headers, params=params)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.error(f"Error fetching times: {e}")
        return []


# ============================================
# MAIN TRACKER CLASS
# ============================================

class MichaelSwimTracker:
    """Main orchestrator for Michael's swim tracking"""
    
    def __init__(self):
        self.config = MICHAEL_CONFIG
        self.scraper = SwimCloudScraper()
        self.analyzer = D1RecruitingAnalyzer(self.config)
        self.supabase = SupabaseClient()
        self.swimmer_id = None
    
    def find_swimmer(self) -> Optional[int]:
        """Find Michael's SwimCloud swimmer ID"""
        logger.info(f"🔍 Searching for {self.config['name']} on SwimCloud...")
        
        # First try direct search
        result = self.scraper.search_swimmer(self.config['name'])
        if result:
            self.swimmer_id = result['swimmer_id']
            logger.info(f"✅ Found swimmer ID: {self.swimmer_id}")
            return self.swimmer_id
        
        # Try searching team roster
        logger.info(f"🔍 Searching {self.config['club_team']} roster...")
        roster = self.scraper.get_team_roster(
            self.config['club_team_id'],
            self.config['gender']
        )
        
        for swimmer in roster:
            if self.config['name'].lower() in swimmer['name'].lower():
                self.swimmer_id = swimmer['swimmer_id']
                logger.info(f"✅ Found in roster - swimmer ID: {self.swimmer_id}")
                return self.swimmer_id
        
        logger.warning(f"⚠️ Could not find swimmer ID for {self.config['name']}")
        return None
    
    def fetch_all_times(self) -> Dict[str, List[Dict]]:
        """Fetch times for all target events"""
        if not self.swimmer_id:
            self.find_swimmer()
        
        if not self.swimmer_id:
            logger.error("Cannot fetch times without swimmer ID")
            return {}
        
        all_times = {}
        for event in self.config['target_events']:
            event_id = EVENT_IDS.get(event)
            logger.info(f"📊 Fetching {event} times...")
            times = self.scraper.get_swimmer_times(self.swimmer_id, event_id)
            if times:
                all_times[event] = times
                logger.info(f"  → Found {len(times)} times for {event}")
        
        return all_times
    
    def run_full_analysis(self) -> Dict:
        """Run complete analysis and save to Supabase"""
        logger.info("=" * 50)
        logger.info(f"🏊 MICHAEL SHAPIRA D1 SWIM TRACKER")
        logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
        # Known best times (from past conversations)
        known_times = {
            "50 Free": 21.86,
            "100 Free": 48.80,
            "100 Back": 61.62,  # 1:01.62
            "50 Fly": 25.79    # From Harry Meisel entry
        }
        
        # Run D1 analysis
        analysis = self.analyzer.analyze_d1_readiness(known_times)
        
        # Print results
        logger.info("\n📊 D1 RECRUITING ANALYSIS:")
        logger.info(f"Overall D1 Score: {analysis['overall_d1_score']}/100")
        logger.info(f"Recommendation: {analysis['recommendation']}")
        
        for event, data in analysis['events'].items():
            status = "✅ QUALIFIED" if data['fl_zone_qualified'] else "❌ NOT YET"
            logger.info(f"\n{event}:")
            logger.info(f"  Current: {data['current_time_str']} | FL Zone: {status}")
            logger.info(f"  Gap to D1 B-Cut: {data['gap_to_b_cut']:+.2f}s")
            logger.info(f"  Tier: {data['d1_tier']}")
        
        # Save to Supabase
        if SUPABASE_KEY:
            self.supabase.insert_d1_analysis(analysis)
            
            # Also insert known times
            time_records = [
                {"event": e, "time_seconds": t, "time_str": self.analyzer._seconds_to_time_str(t)}
                for e, t in known_times.items()
            ]
            self.supabase.insert_swim_times(self.config['name'], time_records)
        
        return analysis


# ============================================
# CLI ENTRY POINT
# ============================================

def main():
    """Main entry point"""
    tracker = MichaelSwimTracker()
    analysis = tracker.run_full_analysis()
    
    # Output JSON for GitHub Actions
    print("\n" + "=" * 50)
    print("JSON OUTPUT:")
    print(json.dumps(analysis, indent=2))
    
    return analysis


if __name__ == "__main__":
    main()
