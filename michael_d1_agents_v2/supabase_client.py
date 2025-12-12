"""
Michael D1 Pathway V2.2 - Supabase Client
==========================================

Handles all database operations for:
- Personal Best Times (MCP-scraped)
- Meet Schedule
- Agent Execution Logs
- MCP Tool Calls
- UF Progress Tracking
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass, asdict


# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


@dataclass
class PersonalBestRecord:
    swimmer_name: str
    event: str
    time: float
    date_achieved: Optional[str] = None
    meet_name: Optional[str] = None
    meet_location: Optional[str] = None
    swim_club: Optional[str] = None
    high_school: Optional[str] = None
    competition_level: str = "club"
    source: str = "swimcloud"


@dataclass
class MeetRecord:
    meet_name: str
    meet_date: str
    location: Optional[str] = None
    events: Optional[List[str]] = None
    competitors: Optional[List[str]] = None


@dataclass
class AgentExecutionRecord:
    agent_name: str
    query: str
    context: Dict[str, Any]
    response: Dict[str, Any]
    mcp_servers_used: List[str]
    execution_time_ms: int


class SupabaseClient:
    """
    Supabase client for Michael D1 Pathway V2.2
    
    Tables:
    - personal_best_times
    - michael_meets
    - agent_executions
    - mcp_tool_calls
    - uf_progress
    - competitor_profiles
    - college_visits
    - nutrition_plans
    - michael_swim_times
    """
    
    def __init__(self, url: str = None, key: str = None):
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        self._client = None
        
        # Try to initialize supabase client
        try:
            from supabase import create_client
            if self.url and self.key:
                self._client = create_client(self.url, self.key)
        except ImportError:
            print("⚠️ Supabase library not installed. Using mock mode.")
        except Exception as e:
            print(f"⚠️ Supabase connection failed: {e}. Using mock mode.")
    
    @property
    def connected(self) -> bool:
        return self._client is not None
    
    # ==========================================
    # PERSONAL BEST TIMES
    # ==========================================
    
    def upsert_pb(self, pb: PersonalBestRecord) -> Dict[str, Any]:
        """Insert or update a personal best time"""
        data = {
            "swimmer_name": pb.swimmer_name,
            "event": pb.event,
            "time": pb.time,
            "date_achieved": pb.date_achieved,
            "meet_name": pb.meet_name,
            "meet_location": pb.meet_location,
            "swim_club": pb.swim_club,
            "high_school": pb.high_school,
            "competition_level": pb.competition_level,
            "source": pb.source,
            "scraped_at": datetime.now().isoformat()
        }
        
        if self._client:
            result = self._client.table("personal_best_times").upsert(
                data, on_conflict="swimmer_name,event"
            ).execute()
            return {"success": True, "data": result.data}
        
        return {"success": False, "mock": True, "data": data}
    
    def get_swimmer_pbs(self, swimmer_name: str) -> List[Dict[str, Any]]:
        """Get all PBs for a swimmer"""
        if self._client:
            result = self._client.table("personal_best_times").select("*").eq(
                "swimmer_name", swimmer_name
            ).execute()
            return result.data
        
        # Mock data
        return []
    
    def get_event_pbs(self, event: str) -> List[Dict[str, Any]]:
        """Get all PBs for an event (for competitor comparison)"""
        if self._client:
            result = self._client.table("personal_best_times").select("*").eq(
                "event", event
            ).order("time").execute()
            return result.data
        return []
    
    # ==========================================
    # MEET SCHEDULE
    # ==========================================
    
    def get_upcoming_meets(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming meets in the next N days"""
        if self._client:
            today = date.today().isoformat()
            result = self._client.table("michael_meets").select("*").gte(
                "meet_date", today
            ).order("meet_date").execute()
            return result.data
        
        # Mock data
        return [
            {"meet_name": "Harry Meisel Championships", "meet_date": "2025-12-13", 
             "location": "Melbourne", "events": ["100 Free", "50 Free", "100 Fly"],
             "competitors": ["Bastian Soto", "Aaron Gordon"]},
        ]
    
    def get_meets_needing_scrape(self, hours_before: int = 72) -> List[Dict[str, Any]]:
        """Get meets that need pre-meet scraping"""
        if self._client:
            result = self._client.table("michael_meets").select("*").eq(
                "scrape_triggered", False
            ).execute()
            return result.data
        return []
    
    def mark_meet_scraped(self, meet_id: str) -> bool:
        """Mark a meet as having been scraped"""
        if self._client:
            self._client.table("michael_meets").update(
                {"scrape_triggered": True}
            ).eq("id", meet_id).execute()
            return True
        return False
    
    # ==========================================
    # AGENT EXECUTION LOGGING
    # ==========================================
    
    def log_agent_execution(self, record: AgentExecutionRecord) -> Dict[str, Any]:
        """Log an agent execution"""
        data = {
            "agent_name": record.agent_name,
            "query": record.query,
            "context": record.context,
            "response": record.response,
            "mcp_servers_used": record.mcp_servers_used,
            "execution_time_ms": record.execution_time_ms,
            "created_at": datetime.now().isoformat()
        }
        
        if self._client:
            result = self._client.table("agent_executions").insert(data).execute()
            return {"success": True, "data": result.data}
        
        return {"success": False, "mock": True, "data": data}
    
    # ==========================================
    # MCP TOOL CALLS
    # ==========================================
    
    def log_mcp_call(self, server_type: str, tool_name: str, 
                     parameters: Dict, result: Dict, success: bool,
                     error: str = None, latency_ms: int = 0) -> Dict[str, Any]:
        """Log an MCP tool call"""
        data = {
            "server_type": server_type,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "success": success,
            "error": error,
            "latency_ms": latency_ms,
            "created_at": datetime.now().isoformat()
        }
        
        if self._client:
            result = self._client.table("mcp_tool_calls").insert(data).execute()
            return {"success": True}
        
        return {"success": False, "mock": True}
    
    # ==========================================
    # UF PROGRESS
    # ==========================================
    
    def update_uf_progress(self, event: str, current_pb: float) -> Dict[str, Any]:
        """Update UF progress for an event"""
        uf_targets = {
            "50 Free": 20.5,
            "100 Free": 45.0,
            "100 Fly": 50.0,
            "100 Back": 52.0,
            "200 Free": 98.0
        }
        
        target = uf_targets.get(event, 999)
        gap = round(current_pb - target, 2)
        
        data = {
            "event": event,
            "current_pb": current_pb,
            "uf_target": target,
            "gap": gap,
            "recorded_at": datetime.now().isoformat()
        }
        
        if self._client:
            result = self._client.table("uf_progress").upsert(
                data, on_conflict="event"
            ).execute()
            return {"success": True, "data": result.data}
        
        return {"success": False, "mock": True, "data": data}
    
    def get_uf_progress(self) -> List[Dict[str, Any]]:
        """Get all UF progress records"""
        if self._client:
            result = self._client.table("uf_progress").select("*").order("gap").execute()
            return result.data
        
        # Mock data
        return [
            {"event": "50 Free", "current_pb": 23.22, "uf_target": 20.5, "gap": 2.72},
            {"event": "100 Free", "current_pb": 50.82, "uf_target": 45.0, "gap": 5.82},
            {"event": "100 Fly", "current_pb": 57.21, "uf_target": 50.0, "gap": 7.21},
            {"event": "100 Back", "current_pb": 61.62, "uf_target": 52.0, "gap": 9.62},
        ]
    
    # ==========================================
    # COMPETITOR PROFILES
    # ==========================================
    
    def get_tracked_competitors(self) -> List[Dict[str, Any]]:
        """Get all tracked competitor profiles"""
        if self._client:
            result = self._client.table("competitor_profiles").select("*").eq(
                "tracked", True
            ).execute()
            return result.data
        
        return [
            {"swimmer_name": "Bastian Soto", "swim_club": "Brevard Aquatic Club", 
             "high_school": "Eau Gallie HS", "threat_level": "high"},
            {"swimmer_name": "Aaron Gordon", "swim_club": "Melbourne Swim Team",
             "high_school": "Melbourne HS", "threat_level": "medium"},
        ]
    
    def add_competitor(self, swimmer_name: str, swim_club: str = None,
                       high_school: str = None, threat_level: str = "medium") -> Dict:
        """Add a new competitor to track"""
        data = {
            "swimmer_name": swimmer_name,
            "swim_club": swim_club,
            "high_school": high_school,
            "threat_level": threat_level,
            "tracked": True
        }
        
        if self._client:
            result = self._client.table("competitor_profiles").upsert(
                data, on_conflict="swimmer_name"
            ).execute()
            return {"success": True, "data": result.data}
        
        return {"success": False, "mock": True, "data": data}
    
    # ==========================================
    # COLLEGE VISITS
    # ==========================================
    
    def log_college_visit(self, school: str, visit_date: str, 
                          itinerary: Dict = None) -> Dict[str, Any]:
        """Log a planned college visit"""
        data = {
            "school": school,
            "visit_date": visit_date,
            "status": "planned",
            "itinerary": itinerary,
            "created_at": datetime.now().isoformat()
        }
        
        if self._client:
            result = self._client.table("college_visits").insert(data).execute()
            return {"success": True, "data": result.data}
        
        return {"success": False, "mock": True, "data": data}
    
    # ==========================================
    # NUTRITION PLANS
    # ==========================================
    
    def log_nutrition_plan(self, plan_date: str, day_type: str,
                           meals: Dict, total_macros: Dict,
                           meet_name: str = None) -> Dict[str, Any]:
        """Log a nutrition plan"""
        data = {
            "plan_date": plan_date,
            "day_type": day_type,
            "meals": meals,
            "total_macros": total_macros,
            "meet_specific": meet_name is not None,
            "meet_name": meet_name,
            "created_at": datetime.now().isoformat()
        }
        
        if self._client:
            result = self._client.table("nutrition_plans").insert(data).execute()
            return {"success": True, "data": result.data}
        
        return {"success": False, "mock": True, "data": data}


# ==========================================
# MAIN - TEST SUPABASE CLIENT
# ==========================================

if __name__ == "__main__":
    print("🗄️ Michael D1 V2.2 - Supabase Client Test")
    print("=" * 60)
    
    client = SupabaseClient()
    print(f"   Connected: {client.connected}")
    
    # Test get upcoming meets
    print("\n📅 Upcoming Meets:")
    meets = client.get_upcoming_meets()
    for meet in meets:
        print(f"   • {meet['meet_name']} - {meet['meet_date']}")
    
    # Test UF progress
    print("\n🎯 UF Progress:")
    progress = client.get_uf_progress()
    for p in progress:
        print(f"   • {p['event']}: {p['current_pb']} → {p['uf_target']} (gap: {p['gap']})")
    
    # Test competitors
    print("\n👥 Tracked Competitors:")
    competitors = client.get_tracked_competitors()
    for c in competitors:
        print(f"   • {c['swimmer_name']} ({c['swim_club']}) - {c['threat_level']}")
    
    print("\n" + "=" * 60)
    print("✅ Supabase Client Ready")
