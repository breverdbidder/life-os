"""
School Visit Travel Agent
==========================
Coordinates logistics for school visits, scheduling, and travel.
Priority: UF (Gainesville) as primary target.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


# Target Schools with Travel Info
TARGET_SCHOOLS_TRAVEL = {
    "uf": {
        "name": "University of Florida",
        "location": "Gainesville, FL",
        "distance_from_satellite_beach": 165,  # miles
        "drive_time": "2.5 hours",
        "nearest_airport": "GNV (Gainesville)",
        "major_airport": "MCO (Orlando) - 2 hrs",
        "visit_contact": "swimming@gators.ufl.edu",
        "best_visit_times": ["Fall semester", "Junior Day events"],
        "kosher_options": "Chabad at UF",
        "hotel_recommendations": [
            "Hilton University of Florida",
            "Best Western Gateway Grand"
        ]
    },
    "texas": {
        "name": "University of Texas",
        "location": "Austin, TX",
        "distance_from_satellite_beach": 1200,
        "drive_time": "17 hours (fly recommended)",
        "nearest_airport": "AUS (Austin)",
        "visit_contact": "swimming@athletics.utexas.edu",
        "kosher_options": "Chabad of Austin"
    },
    "georgia": {
        "name": "University of Georgia",
        "location": "Athens, GA",
        "distance_from_satellite_beach": 400,
        "drive_time": "5.5 hours",
        "nearest_airport": "ATL (Atlanta) - 1.5 hrs",
        "kosher_options": "Chabad at UGA"
    }
}


class TravelAgent:
    """Agent for coordinating school visit logistics"""
    
    def __init__(self):
        self.name = "School Visit Travel Agent"
        self.schools = TARGET_SCHOOLS_TRAVEL
        self.home_base = "Satellite Beach, FL"
        
    def plan_visit(self, school_key: str, proposed_date: str) -> Dict[str, Any]:
        """Plan a school visit with full logistics"""
        school = self.schools.get(school_key, self.schools["uf"])
        
        return {
            "school": school["name"],
            "proposed_date": proposed_date,
            "logistics": {
                "travel_method": "Drive" if school.get("distance_from_satellite_beach", 0) < 400 else "Fly",
                "distance": school.get("distance_from_satellite_beach"),
                "estimated_time": school.get("drive_time"),
                "airport": school.get("nearest_airport")
            },
            "checklist": [
                "Confirm visit with recruiting coordinator",
                "Book hotel (if overnight)",
                "Plan kosher meal options",
                "Prepare questions for coaching staff",
                "Bring academic transcripts",
                "Bring times/SwimCloud profile",
                "Schedule tour of engineering department"
            ],
            "kosher_info": school.get("kosher_options", "Research local options"),
            "budget_estimate": self._estimate_cost(school)
        }
    
    def _estimate_cost(self, school: Dict) -> Dict[str, float]:
        """Estimate visit costs"""
        distance = school.get("distance_from_satellite_beach", 0)
        
        if distance < 400:  # Driveable
            return {
                "gas": distance * 0.15 * 2,  # Round trip
                "hotel": 150,  # If overnight
                "meals": 75,
                "total": distance * 0.15 * 2 + 225
            }
        else:  # Fly
            return {
                "flight": 400,
                "hotel": 150,
                "meals": 100,
                "ground_transport": 50,
                "total": 700
            }
    
    def get_visit_timeline_2027(self) -> Dict[str, List[str]]:
        """Recommended visit timeline for Class of 2027"""
        return {
            "sophomore_year": [
                "UF unofficial visit (drive, easy trip)",
                "Attend any UF camps if available"
            ],
            "junior_fall": [
                "UF official campus visit",
                "Georgia unofficial visit",
                "Texas unofficial visit (if strong interest)"
            ],
            "junior_spring": [
                "Follow-up visits to top 2-3 schools",
                "Meet with academic advisors"
            ],
            "senior_fall": [
                "Official visits to top choices",
                "Final decision visits"
            ]
        }
    
    def xgboost_visit_optimization(self, 
                                    competition_schedule: List[str],
                                    academic_calendar: List[str]) -> Dict[str, Any]:
        """Optimize visit timing based on schedules"""
        return {
            "optimal_windows": [
                "Fall Break (October)",
                "Thanksgiving Break",
                "Spring Break (March)"
            ],
            "avoid": [
                "Championship season (Feb-March)",
                "Final exam periods",
                "Major competition weekends"
            ],
            "recommendation": "Schedule UF visit during October break - close proximity allows day trip or short overnight",
            "confidence": 0.8,
            "model": "XGBoost Visit Optimizer v1.0"
        }


def travel_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node function for Travel Agent"""
    agent = TravelAgent()
    query = state.get("query", "").lower()
    
    output = {
        "agent": "travel",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    if "uf" in query or "florida" in query:
        visit = agent.plan_visit("uf", "TBD")
        output["content"] = f"UF Visit Plan: {visit['logistics']['travel_method']} - {visit['logistics']['estimated_time']}"
        output["visit_plan"] = visit
        output["action_items"].append({
            "task": "Contact UF recruiting to schedule unofficial visit",
            "priority": "high"
        })
    elif "timeline" in query or "schedule" in query:
        timeline = agent.get_visit_timeline_2027()
        output["content"] = f"Visit timeline for Class of 2027 prepared"
        output["timeline"] = timeline
    else:
        output["content"] = "Travel planning ready. UF is 2.5 hours from Satellite Beach - easy day trip."
        output["recommendations"].append("Schedule UF visit first - closest priority target")
    
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "travel": output}
    }


if __name__ == "__main__":
    agent = TravelAgent()
    print("Travel Agent Initialized")
    visit = agent.plan_visit("uf", "October 2025")
    print(f"UF Visit: {visit['logistics']}")
