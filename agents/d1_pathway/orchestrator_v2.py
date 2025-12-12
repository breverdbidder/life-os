"""
Michael Shapira D1 Pathway - LangGraph Multi-Agent Orchestrator V2
===================================================================
Enhanced Agentic AI ecosystem for comprehensive D1 swimming recruitment.

PRIMARY TARGET: University of Florida (UF) - Class of 2027
ACADEMIC PRIORITY: Engineering with Real Estate Minor

Agents (10):
1. Kosher Meal & Diet Preparation Agent
2. Education Achievement Agent
3. School Visit Travel Agent
4. Chabad Contacts & School Information Agent
5. Competitor Swimmers Analysis Agent
6. Engineering Opportunities Agent (Real Estate Minor Focus)
7. Meet Analysis & Preparation Agent
8. Meet Results Tracking & Analysis Agent
9. Improvements Tracking & Goals Achievement Agent
10. Recruiting Communications Agent

Author: Claude Opus 4.5 (AI Architect)
Parent: Everest Capital USA
"""

from typing import TypedDict, Annotated, Sequence, Literal, Optional, Dict, List
from langgraph.graph import StateGraph, END
import operator
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os

# ============================================================
# CONSTANTS - UF 2027 PRIMARY TARGET
# ============================================================

UF_RECRUITING_TIMES = {
    "fifty_free": {"walk_on": "21.5", "scholarship": "20.5", "top_recruit": "19.8"},
    "hundred_free": {"walk_on": "46.5", "scholarship": "44.5", "top_recruit": "43.5"},
    "two_hundred_free": {"walk_on": "1:40.0", "scholarship": "1:36.0", "top_recruit": "1:34.0"},
    "hundred_fly": {"walk_on": "51.0", "scholarship": "49.0", "top_recruit": "47.5"},
    "hundred_back": {"walk_on": "51.0", "scholarship": "49.0", "top_recruit": "47.5"},
    "fifty_fly": {"walk_on": "23.5", "scholarship": "22.5", "top_recruit": "21.5"}
}

POWER_5_CONFERENCES = ["SEC", "Big Ten", "ACC", "Big 12", "Pac-12"]

TARGET_SCHOOLS_PRIORITY = [
    {"name": "Florida", "conference": "SEC", "priority": 1, "real_estate_minor": True},
    {"name": "Texas", "conference": "Big 12", "priority": 2, "real_estate_minor": True},
    {"name": "Georgia Tech", "conference": "ACC", "priority": 3, "real_estate_minor": False},
    {"name": "NC State", "conference": "ACC", "priority": 4, "real_estate_minor": True},
    {"name": "Virginia", "conference": "ACC", "priority": 5, "real_estate_minor": False},
    {"name": "Michigan", "conference": "Big Ten", "priority": 6, "real_estate_minor": True},
    {"name": "Texas A&M", "conference": "SEC", "priority": 7, "real_estate_minor": True},
    {"name": "Stanford", "conference": "Pac-12", "priority": 8, "real_estate_minor": False},
]


# ============================================================
# STATE DEFINITIONS
# ============================================================

class MichaelProfile(TypedDict):
    """Static profile data for Michael Shapira"""
    name: str
    dob: str
    age: int
    height: str
    weight: int
    high_school: str
    graduation_year: int
    current_club: str
    events: list[str]
    sat_score: int
    gpa: float
    dietary_requirements: str
    primary_target: str
    academic_major: str
    academic_minor: str


class SwimTimes(TypedDict):
    """Current personal bests - SCY"""
    fifty_free: str
    hundred_free: str
    two_hundred_free: str
    hundred_fly: str
    fifty_fly: str
    hundred_back: str
    fifty_back: str
    last_updated: str


class MeetEntry(TypedDict):
    """Individual meet entry"""
    meet_name: str
    date: str
    location: str
    events: list[dict]
    status: str


class CompetitorProfile(TypedDict):
    """Competitor swimmer profile"""
    name: str
    school: str
    grad_year: int
    events: dict
    recruiting_status: str


class D1PathwayStateV2(TypedDict):
    """Enhanced state for D1 Pathway V2 orchestrator"""
    # Core profile
    profile: MichaelProfile
    swim_times: SwimTimes
    
    # Target schools
    target_schools: list[dict]
    
    # Agent outputs
    meal_plan: dict
    academic_tracker: dict
    travel_itinerary: dict
    chabad_contacts: dict
    competitor_analysis: dict
    engineering_opportunities: dict
    meet_preparation: dict
    meet_results: dict
    improvements_tracking: dict
    recruiting_communications: dict
    
    # Workflow state
    messages: Annotated[Sequence[dict], operator.add]
    current_agent: str
    last_updated: str
    errors: list[str]
    
    # UF-specific tracking
    uf_readiness_score: float
    days_to_recruitment: int


# ============================================================
# AGENT 1: KOSHER DIET AGENT
# ============================================================

class KosherDietAgent:
    """
    Kosher Meal & Diet Preparation Agent
    Based on Michael Andrew keto framework
    """
    
    def __init__(self):
        self.calorie_target = 3800
        self.keto_days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
        self.shabbat_days = ["Friday", "Saturday", "Sunday"]
        
    def generate_weekly_plan(self, state: D1PathwayStateV2) -> dict:
        plan = {
            "week_of": datetime.now().strftime("%Y-%m-%d"),
            "athlete": state["profile"]["name"],
            "calorie_target": self.calorie_target,
            "protocol": "Michael Andrew Keto Framework - Kosher Adapted",
            "days": {}
        }
        
        keto_template = {
            "type": "strict_keto",
            "macros": {"protein": "35%", "fat": "60%", "carbs": "5%"},
            "meals": {
                "breakfast": ["4 eggs in olive oil", "beef bacon", "avocado", "kosher cheese"],
                "pre_practice": ["MCT oil coffee", "almonds"],
                "post_practice": ["Kosher chocolate milk (OU-D)", "whey protein"],
                "lunch": ["Grilled chicken (8oz)", "Caesar salad", "olive oil"],
                "dinner": ["Ribeye steak (12oz)", "broccoli", "cauliflower mash"],
            },
            "total_calories": 3800
        }
        
        shabbat_template = {
            "type": "moderate_carbs",
            "macros": {"protein": "30%", "fat": "40%", "carbs": "30%"},
            "meals": {
                "friday_dinner": ["Challah", "Chicken soup", "Roast chicken", "Kugel"],
                "shabbat_lunch": ["Cholent", "Salads", "Challah"],
                "sunday": ["Kosher asado", "Grilled veggies", "Rice", "Hummus"]
            },
            "total_calories": 4000
        }
        
        for day in self.keto_days:
            plan["days"][day] = keto_template
        for day in self.shabbat_days:
            plan["days"][day] = shabbat_template
            
        return plan
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "meal_plan": self.generate_weekly_plan(state),
            "current_agent": "kosher_diet",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 2: EDUCATION ACHIEVEMENT AGENT
# ============================================================

class EducationAchievementAgent:
    """
    Education Achievement Agent
    Tracks academics for NCAA eligibility with UF focus
    """
    
    def __init__(self):
        self.uf_requirements = {
            "min_gpa": 3.0,
            "min_sat": 1200,
            "preferred_sat": 1350,
            "core_courses": 16
        }
        
    def assess_uf_eligibility(self, state: D1PathwayStateV2) -> dict:
        profile = state["profile"]
        current_sat = profile.get("sat_score", 1280)
        current_gpa = profile.get("gpa", 3.5)
        
        return {
            "uf_eligible": current_sat >= self.uf_requirements["min_sat"] and 
                          current_gpa >= self.uf_requirements["min_gpa"],
            "sat_status": {
                "current": current_sat,
                "uf_minimum": self.uf_requirements["min_sat"],
                "uf_preferred": self.uf_requirements["preferred_sat"],
                "gap_to_preferred": self.uf_requirements["preferred_sat"] - current_sat,
                "status": "MEETS MIN" if current_sat >= 1200 else "NEEDS IMPROVEMENT"
            },
            "gpa_status": {
                "current": current_gpa,
                "uf_minimum": self.uf_requirements["min_gpa"],
                "status": "EXCEEDS" if current_gpa >= 3.5 else "MEETS"
            },
            "recommendations": [
                "Target SAT 1350+ for competitive UF admission",
                "Focus English Conventions section (+50 pts potential)",
                "Maintain current GPA trajectory"
            ]
        }
    
    def track_dual_enrollment(self) -> dict:
        return {
            "program": "Engineering Technology (ETAS)",
            "institution": "Eastern Florida State College",
            "credits_target": 60,
            "transfer_to_uf": "Yes - Florida state articulation",
            "real_estate_courses": [
                "REE 3043 - Real Estate Principles",
                "REE 4103 - Real Estate Finance",
                "REE 4204 - Real Estate Appraisal"
            ]
        }
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "academic_tracker": {
                "uf_eligibility": self.assess_uf_eligibility(state),
                "dual_enrollment": self.track_dual_enrollment(),
                "target_major": "Engineering",
                "target_minor": "Real Estate (Priority 1)"
            },
            "current_agent": "education",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 3: SCHOOL VISIT TRAVEL AGENT
# ============================================================

class SchoolVisitTravelAgent:
    """Coordinates D1 school visit logistics"""
    
    def __init__(self):
        self.home_base = "Satellite Beach, FL"
    
    def plan_uf_priority_visit(self) -> dict:
        return {
            "school": "University of Florida",
            "priority": "PRIMARY TARGET",
            "recommended_dates": ["December 22, 2025", "January 2026", "Spring Break 2026"],
            "visit_agenda": [
                {"time": "9:00 AM", "activity": "Campus Tour - Admissions"},
                {"time": "10:30 AM", "activity": "Herbert Wertheim College of Engineering"},
                {"time": "12:00 PM", "activity": "Lunch at Chabad UF"},
                {"time": "1:30 PM", "activity": "O'Connell Center - Pool Tour"},
                {"time": "2:30 PM", "activity": "Meet with Swim Coaches (if available)"},
                {"time": "4:00 PM", "activity": "Bergstrom Real Estate Center Tour"},
                {"time": "5:00 PM", "activity": "Student Athlete Academic Center"}
            ],
            "contacts": {
                "swim_coach": "Anthony Nesty",
                "recruiting": "recruiting@floridagators.com",
                "engineering": "admissions@eng.ufl.edu"
            },
            "travel": {
                "distance": "160 miles from Satellite Beach",
                "drive_time": "2.5 hours",
                "accommodation": "Hilton UF Conference Center"
            }
        }
    
    def plan_winter_break_tour(self) -> dict:
        return {
            "trip_name": "Winter Break D1 Tour 2025",
            "dates": "December 22-30, 2025",
            "schools": [
                {"name": "Florida", "date": "Dec 22", "priority": 1},
                {"name": "Texas A&M", "date": "Dec 24-25", "priority": 7},
                {"name": "Texas", "date": "Dec 26-27", "priority": 2},
                {"name": "Georgia Tech", "date": "Dec 29", "priority": 3}
            ],
            "budget": 3500
        }
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "travel_itinerary": {
                "uf_visit": self.plan_uf_priority_visit(),
                "winter_tour": self.plan_winter_break_tour()
            },
            "current_agent": "travel",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 4: CHABAD CONTACTS AGENT
# ============================================================

class ChabadContactsAgent:
    """Maintains Chabad contacts at target schools"""
    
    def __init__(self):
        self.chabad_directory = {
            "Florida": {
                "name": "Chabad UF - Lubavitch Jewish Student Center",
                "rabbi": "Rabbi Berl & Chani Goldman",
                "address": "2021 NW 5th Ave, Gainesville, FL 32603",
                "phone": "(352) 336-5877",
                "website": "https://www.jewishgator.com",
                "shabbat_dinner": "Every Friday 7:30 PM",
                "kosher_meals": "Daily lunch available"
            },
            "Texas": {
                "rabbi": "Rabbi Zev Johnson",
                "phone": "(512) 905-2573",
                "website": "https://www.chabadaustin.com"
            },
            "Georgia Tech": {
                "rabbi": "Rabbi Shlomo Sharfstein",
                "phone": "(404) 892-1000",
                "website": "https://www.chabadgatech.org"
            },
            "Texas A&M": {
                "rabbi": "Rabbi Yossi Lazaroff",
                "phone": "(979) 696-7902",
                "website": "https://www.chabadtamu.com"
            },
            "NC State": {
                "rabbi": "Rabbi Shmuly Meijers",
                "phone": "(919) 637-4893",
                "website": "https://www.chabadraleigh.org"
            },
            "Michigan": {
                "rabbi": "Rabbi Aharon Goldstein",
                "phone": "(734) 995-3276",
                "website": "https://www.jewmich.com"
            }
        }
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "chabad_contacts": self.chabad_directory,
            "current_agent": "chabad",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 5: COMPETITOR SWIMMERS ANALYSIS AGENT
# ============================================================

class CompetitorSwimmersAgent:
    """
    Analyzes competitive swimming data and tracks competitors
    Focus on UF 2027 recruiting class competition
    """
    
    def __init__(self):
        # UF 2027 recruiting class competitors (example data)
        self.uf_2027_competitors = [
            {"name": "Top Recruit A", "state": "TX", "fifty_free": "20.1", "hundred_free": "44.2", "commitment": "Uncommitted"},
            {"name": "Top Recruit B", "state": "CA", "fifty_free": "20.5", "hundred_free": "44.8", "commitment": "Verbal UF"},
            {"name": "Top Recruit C", "state": "FL", "fifty_free": "21.0", "hundred_free": "45.5", "commitment": "Uncommitted"},
        ]
        
    def analyze_uf_recruiting_class(self, michael_times: SwimTimes) -> dict:
        """Compare Michael to UF 2027 recruiting class"""
        
        michael_50 = float(michael_times.get("fifty_free", "23.22"))
        michael_100 = float(michael_times.get("hundred_free", "50.82"))
        
        analysis = {
            "target_class": "UF 2027",
            "michael_current": {
                "fifty_free": michael_times.get("fifty_free"),
                "hundred_free": michael_times.get("hundred_free")
            },
            "competitors": [],
            "michael_ranking": 0,
            "gap_to_top": 0
        }
        
        all_swimmers = self.uf_2027_competitors + [
            {"name": "Michael Shapira", "fifty_free": str(michael_50), "hundred_free": str(michael_100)}
        ]
        
        # Rank by 100 free
        sorted_swimmers = sorted(all_swimmers, key=lambda x: float(x.get("hundred_free", "99.99")))
        
        for i, swimmer in enumerate(sorted_swimmers):
            if swimmer["name"] == "Michael Shapira":
                analysis["michael_ranking"] = i + 1
                if i > 0:
                    top_time = float(sorted_swimmers[0]["hundred_free"])
                    analysis["gap_to_top"] = round(michael_100 - top_time, 2)
        
        analysis["competitors"] = self.uf_2027_competitors
        analysis["recommendation"] = self._get_recommendation(analysis["michael_ranking"], len(sorted_swimmers))
        
        return analysis
    
    def _get_recommendation(self, rank: int, total: int) -> str:
        if rank == 1:
            return "LEADING RECRUIT - Maintain momentum"
        elif rank <= 3:
            return "COMPETITIVE - Focus on time drops"
        else:
            return "DEVELOPMENT NEEDED - Accelerate training"
    
    def track_sec_sprinters(self) -> list:
        """Track SEC conference sprint times"""
        return [
            {"school": "Florida", "avg_50_free": "19.8", "avg_100_free": "43.5"},
            {"school": "Texas A&M", "avg_50_free": "20.2", "avg_100_free": "44.1"},
            {"school": "Georgia", "avg_50_free": "20.0", "avg_100_free": "43.8"},
            {"school": "Tennessee", "avg_50_free": "20.1", "avg_100_free": "44.0"},
        ]
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "competitor_analysis": {
                "uf_2027_class": self.analyze_uf_recruiting_class(state.get("swim_times", {})),
                "sec_sprinters": self.track_sec_sprinters(),
                "analysis_date": datetime.now().isoformat()
            },
            "current_agent": "competitor_analysis",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 6: ENGINEERING OPPORTUNITIES AGENT
# ============================================================

class EngineeringOpportunitiesAgent:
    """
    Engineering programs with REAL ESTATE MINOR PRIORITY
    """
    
    def __init__(self):
        self.schools_with_real_estate = {
            "Florida": {
                "engineering_rank": 27,
                "real_estate_minor": True,
                "real_estate_program": "Bergstrom Center for Real Estate Studies",
                "real_estate_courses": [
                    "REE 3043 - Real Estate Principles",
                    "REE 4103 - Real Estate Finance",
                    "REE 4204 - Real Estate Appraisal",
                    "REE 4303 - Real Estate Investment Analysis",
                    "REE 4943 - Real Estate Field Study"
                ],
                "minor_requirements": "15 credits minimum",
                "engineering_specializations": [
                    "Mechanical Engineering",
                    "Civil Engineering", 
                    "Computer Engineering",
                    "Aerospace Engineering"
                ],
                "priority_score": 10,  # Highest
                "notes": "Top real estate program in nation, perfect for Everest Capital"
            },
            "Texas": {
                "engineering_rank": 10,
                "real_estate_minor": True,
                "real_estate_program": "McCombs Real Estate Center",
                "minor_requirements": "18 credits",
                "priority_score": 9
            },
            "NC State": {
                "engineering_rank": 30,
                "real_estate_minor": True,
                "real_estate_program": "Poole College Real Estate",
                "priority_score": 8
            },
            "Michigan": {
                "engineering_rank": 4,
                "real_estate_minor": True,
                "real_estate_program": "Ross School of Business",
                "priority_score": 8
            },
            "Texas A&M": {
                "engineering_rank": 12,
                "real_estate_minor": True,
                "real_estate_program": "Mays Business School",
                "priority_score": 7
            },
            "Georgia Tech": {
                "engineering_rank": 4,
                "real_estate_minor": False,
                "real_estate_alternative": "Building Construction program",
                "priority_score": 6
            },
            "Stanford": {
                "engineering_rank": 2,
                "real_estate_minor": False,
                "real_estate_alternative": "Graduate programs only",
                "priority_score": 5
            },
            "Virginia": {
                "engineering_rank": 33,
                "real_estate_minor": False,
                "priority_score": 4
            }
        }
    
    def rank_by_real_estate_priority(self) -> list:
        """Rank schools with real estate minor as priority"""
        schools = []
        for name, data in self.schools_with_real_estate.items():
            schools.append({
                "school": name,
                "real_estate_minor": data.get("real_estate_minor", False),
                "engineering_rank": data.get("engineering_rank"),
                "real_estate_program": data.get("real_estate_program", "N/A"),
                "priority_score": data.get("priority_score", 0)
            })
        
        # Sort by real estate minor availability first, then priority score
        return sorted(schools, key=lambda x: (-int(x["real_estate_minor"]), -x["priority_score"]))
    
    def get_uf_details(self) -> dict:
        """Detailed UF engineering + real estate info"""
        return self.schools_with_real_estate["Florida"]
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "engineering_opportunities": {
                "priority_ranking": self.rank_by_real_estate_priority(),
                "uf_details": self.get_uf_details(),
                "recommendation": "UF offers ideal combination: Top-5 real estate program + competitive engineering + elite swimming"
            },
            "current_agent": "engineering",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 7: MEET ANALYSIS & PREPARATION AGENT
# ============================================================

class MeetPreparationAgent:
    """
    Analyzes upcoming meets and provides strategic preparation
    """
    
    def __init__(self):
        self.upcoming_meets = []
    
    def analyze_harry_meisel(self) -> dict:
        """Analyze Harry Meisel Championships (Dec 13-14, 2025)"""
        return {
            "meet_name": "Harry Meisel Championships East",
            "dates": "December 13-14, 2025",
            "importance": "HIGH - Last meet before recruiting push",
            "michael_entries": [
                {"event": "100 Free", "heat": 1, "lane": 6, "seed": "50.82", "target": "49.5"},
                {"event": "50 Fly", "heat": 1, "lane": 3, "seed": "25.79", "target": "25.0"},
                {"event": "100 Back", "heat": 1, "lane": 2, "seed": "1:01.62", "target": "59.9"},
                {"event": "50 Free", "heat": 1, "lane": 3, "seed": "23.22", "target": "22.5"}
            ],
            "competition_analysis": {
                "fifty_free": "Heat 1 - fastest seeded heat, expect 22-23 range",
                "hundred_free": "Heat 1 - competitive field, need sub-50 to stand out"
            },
            "race_strategy": {
                "fifty_free": "Aggressive start, maintain stroke rate through 25",
                "hundred_free": "Controlled first 50 (24.5), negative split (25.0)",
                "fifty_fly": "High tempo, minimize breathing",
                "hundred_back": "Strong underwaters, consistent tempo"
            },
            "venue_notes": "Indoor SCY, 8-lane pool, good lighting",
            "warmup_plan": {
                "arrive": "1 hour before first event",
                "warmup": "800 easy, 4x50 build, 4x25 race pace",
                "pre_race": "50 easy + 25 sprint 10 min before"
            }
        }
    
    def get_meet_schedule(self) -> list:
        """Upcoming meet schedule"""
        return [
            {"meet": "Harry Meisel Championships", "date": "Dec 13-14, 2025", "priority": "HIGH"},
            {"meet": "Florida Age Group Champs", "date": "Feb 2026", "priority": "HIGH"},
            {"meet": "Sectionals", "date": "Mar 2026", "priority": "CRITICAL"},
            {"meet": "Florida HS State", "date": "Nov 2026", "priority": "CRITICAL"}
        ]
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "meet_preparation": {
                "next_meet": self.analyze_harry_meisel(),
                "schedule": self.get_meet_schedule(),
                "focus": "Harry Meisel is crucial for UF recruiting attention"
            },
            "current_agent": "meet_prep",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 8: MEET RESULTS TRACKING AGENT
# ============================================================

class MeetResultsAgent:
    """
    Tracks and analyzes all meet results
    Benchmarks against UF Power 5 standards
    """
    
    def __init__(self):
        self.results_history = []
    
    def add_result(self, meet: str, event: str, time: str, splits: list = None) -> dict:
        """Add new meet result"""
        result = {
            "meet": meet,
            "event": event,
            "time": time,
            "splits": splits,
            "date": datetime.now().isoformat(),
            "uf_comparison": self._compare_to_uf(event, time)
        }
        self.results_history.append(result)
        return result
    
    def _compare_to_uf(self, event: str, time: str) -> dict:
        """Compare result to UF recruiting standards"""
        event_key = event.lower().replace(" ", "_").replace("100", "hundred").replace("50", "fifty").replace("200", "two_hundred")
        
        if event_key in UF_RECRUITING_TIMES:
            targets = UF_RECRUITING_TIMES[event_key]
            time_float = self._time_to_seconds(time)
            
            walk_on = self._time_to_seconds(targets["walk_on"])
            scholarship = self._time_to_seconds(targets["scholarship"])
            top = self._time_to_seconds(targets["top_recruit"])
            
            if time_float <= top:
                status = "TOP RECRUIT LEVEL"
            elif time_float <= scholarship:
                status = "SCHOLARSHIP LEVEL"
            elif time_float <= walk_on:
                status = "WALK-ON LEVEL"
            else:
                status = "DEVELOPING"
            
            return {
                "status": status,
                "gap_to_scholarship": round(time_float - scholarship, 2),
                "gap_to_walk_on": round(time_float - walk_on, 2)
            }
        
        return {"status": "EVENT NOT TRACKED"}
    
    def _time_to_seconds(self, time_str: str) -> float:
        if ":" in str(time_str):
            parts = str(time_str).split(":")
            return float(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    
    def get_season_summary(self, times: SwimTimes) -> dict:
        """Season performance summary"""
        summary = {
            "events": {},
            "uf_readiness": {}
        }
        
        for event, time in times.items():
            if time and event != "last_updated":
                comparison = self._compare_to_uf(event, time)
                summary["events"][event] = {
                    "best_time": time,
                    "uf_status": comparison.get("status", "N/A")
                }
        
        return summary
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "meet_results": {
                "season_summary": self.get_season_summary(state.get("swim_times", {})),
                "benchmark": "UF 2027 Recruiting Standards",
                "history": self.results_history[-10:]  # Last 10 results
            },
            "current_agent": "meet_results",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 9: IMPROVEMENTS TRACKING AGENT
# ============================================================

class ImprovementsTrackingAgent:
    """
    Monitors progress toward UF 2027 recruitment standards
    PRIMARY BENCHMARK: University of Florida
    """
    
    def __init__(self):
        self.uf_targets = UF_RECRUITING_TIMES
        self.recruitment_deadline = datetime(2026, 11, 1)  # Early signing period
    
    def calculate_uf_readiness(self, times: SwimTimes) -> dict:
        """Calculate overall UF readiness score"""
        
        events_analyzed = 0
        total_score = 0
        event_scores = {}
        
        for event, time in times.items():
            if time and event in self.uf_targets:
                events_analyzed += 1
                
                current = self._time_to_seconds(time)
                walk_on = self._time_to_seconds(self.uf_targets[event]["walk_on"])
                scholarship = self._time_to_seconds(self.uf_targets[event]["scholarship"])
                
                # Score: 100 = scholarship level, 70 = walk-on level, 0 = far off
                if current <= scholarship:
                    score = 100
                elif current <= walk_on:
                    # Linear scale between walk-on (70) and scholarship (100)
                    score = 70 + 30 * (walk_on - current) / (walk_on - scholarship)
                else:
                    # Scale below walk-on
                    gap = current - walk_on
                    score = max(0, 70 - gap * 10)
                
                event_scores[event] = {
                    "current": time,
                    "walk_on_target": self.uf_targets[event]["walk_on"],
                    "scholarship_target": self.uf_targets[event]["scholarship"],
                    "score": round(score, 1),
                    "gap_to_walk_on": round(current - walk_on, 2)
                }
                total_score += score
        
        overall_score = total_score / events_analyzed if events_analyzed > 0 else 0
        
        return {
            "overall_uf_readiness": round(overall_score, 1),
            "event_scores": event_scores,
            "days_to_signing": (self.recruitment_deadline - datetime.now()).days,
            "status": self._get_status(overall_score),
            "priority_improvements": self._get_priorities(event_scores)
        }
    
    def _time_to_seconds(self, time_str: str) -> float:
        if ":" in str(time_str):
            parts = str(time_str).split(":")
            return float(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    
    def _get_status(self, score: float) -> str:
        if score >= 90:
            return "SCHOLARSHIP READY"
        elif score >= 70:
            return "WALK-ON READY"
        elif score >= 50:
            return "ON TRACK"
        else:
            return "ACCELERATED IMPROVEMENT NEEDED"
    
    def _get_priorities(self, event_scores: dict) -> list:
        """Identify priority events for improvement"""
        priorities = []
        for event, data in event_scores.items():
            if data["gap_to_walk_on"] > 0:
                priorities.append({
                    "event": event,
                    "gap": data["gap_to_walk_on"],
                    "priority": "HIGH" if data["gap_to_walk_on"] > 3 else "MEDIUM"
                })
        
        return sorted(priorities, key=lambda x: x["gap"], reverse=True)
    
    def get_monthly_targets(self, times: SwimTimes) -> dict:
        """Calculate monthly improvement targets to reach UF standards"""
        days_left = (self.recruitment_deadline - datetime.now()).days
        months_left = days_left / 30
        
        targets = {}
        for event, time in times.items():
            if time and event in self.uf_targets:
                current = self._time_to_seconds(time)
                target = self._time_to_seconds(self.uf_targets[event]["walk_on"])
                
                if current > target:
                    gap = current - target
                    monthly_improvement = gap / months_left if months_left > 0 else gap
                    targets[event] = {
                        "current": time,
                        "target": self.uf_targets[event]["walk_on"],
                        "total_gap": round(gap, 2),
                        "monthly_improvement_needed": round(monthly_improvement, 3)
                    }
        
        return targets
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        times = state.get("swim_times", {})
        readiness = self.calculate_uf_readiness(times)
        
        return {
            "improvements_tracking": {
                "uf_readiness": readiness,
                "monthly_targets": self.get_monthly_targets(times),
                "primary_target": "University of Florida - Class of 2027",
                "signing_period": "November 2026"
            },
            "uf_readiness_score": readiness["overall_uf_readiness"],
            "days_to_recruitment": readiness["days_to_signing"],
            "current_agent": "improvements",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# AGENT 10: RECRUITING COMMUNICATIONS AGENT
# ============================================================

class RecruitingCommunicationsAgent:
    """
    Manages recruiting outreach and communications
    """
    
    def __init__(self):
        self.uf_contacts = {
            "head_coach": {"name": "Anthony Nesty", "email": "anesty@gators.ufl.edu"},
            "recruiting_coordinator": {"email": "swimrecruiting@gators.ufl.edu"},
            "sprint_coach": {"name": "Steve Jungbluth"}
        }
    
    def generate_uf_intro_email(self, profile: dict, times: SwimTimes) -> str:
        """Generate initial recruiting email to UF"""
        return f"""Subject: {profile['name']} - Class of {profile['graduation_year']} - Sprint Freestyle

Dear Coach Nesty,

My name is {profile['name']}, and I am a junior at {profile['high_school']} in Florida. 
I am reaching out to express my strong interest in the University of Florida swimming program 
and the Herbert Wertheim College of Engineering.

ATHLETIC PROFILE:
• Height: {profile['height']} | Weight: {profile['weight']} lbs
• Primary Events: 50/100/200 Freestyle, 100 Butterfly
• Current Club: {profile['current_club']}

BEST TIMES (SCY - December 2025):
• 50 Free: {times.get('fifty_free', 'N/A')}
• 100 Free: {times.get('hundred_free', 'N/A')}
• 100 Fly: {times.get('hundred_fly', 'N/A')}

ACADEMIC PROFILE:
• SAT: {profile.get('sat_score', 'N/A')}
• GPA: {profile.get('gpa', 'N/A')}
• Intended Major: Engineering with Real Estate Minor

As a Florida resident, UF has been my dream school. I am particularly drawn to both the 
elite swimming program under your leadership and the nationally-ranked Bergstrom Real Estate 
Center for my academic interests.

I will be attending [upcoming meet] and would welcome the opportunity to connect.

Thank you for your time and consideration.

Go Gators!

{profile['name']}
{profile['high_school']} - Class of {profile['graduation_year']}
"""
    
    def get_outreach_schedule(self) -> list:
        """Recommended recruiting outreach timeline"""
        return [
            {"date": "December 2025", "action": "Send intro emails to top 5 schools", "priority": "UF first"},
            {"date": "January 2026", "action": "Follow up with updated times post-Harry Meisel"},
            {"date": "February 2026", "action": "Request unofficial visits"},
            {"date": "March 2026", "action": "Send Sectionals results"},
            {"date": "June 2026", "action": "Official visit requests (after July 1 contact period)"},
            {"date": "November 2026", "action": "Early signing period"}
        ]
    
    def __call__(self, state: D1PathwayStateV2) -> dict:
        return {
            "recruiting_communications": {
                "uf_email_draft": self.generate_uf_intro_email(state["profile"], state.get("swim_times", {})),
                "outreach_schedule": self.get_outreach_schedule(),
                "uf_contacts": self.uf_contacts
            },
            "current_agent": "recruiting_comms",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# LANGGRAPH ORCHESTRATOR V2
# ============================================================

def create_d1_pathway_graph_v2():
    """Create enhanced LangGraph orchestrator with all 10 agents"""
    
    # Initialize all agents
    agents = {
        "diet": KosherDietAgent(),
        "education": EducationAchievementAgent(),
        "travel": SchoolVisitTravelAgent(),
        "chabad": ChabadContactsAgent(),
        "competitors": CompetitorSwimmersAgent(),
        "engineering": EngineeringOpportunitiesAgent(),
        "meet_prep": MeetPreparationAgent(),
        "meet_results": MeetResultsAgent(),
        "improvements": ImprovementsTrackingAgent(),
        "recruiting": RecruitingCommunicationsAgent()
    }
    
    workflow = StateGraph(D1PathwayStateV2)
    
    # Add nodes
    for name, agent in agents.items():
        workflow.add_node(name, agent)
    
    workflow.add_node("synthesize", synthesize_all_agents)
    
    # Routing logic
    def route_request(state: D1PathwayStateV2) -> str:
        messages = state.get("messages", [])
        if not messages:
            return "improvements"  # Default: check UF readiness
        
        last_msg = messages[-1].get("content", "").lower()
        
        if any(w in last_msg for w in ["meal", "diet", "food", "kosher", "keto"]):
            return "diet"
        elif any(w in last_msg for w in ["grade", "gpa", "sat", "academic", "course"]):
            return "education"
        elif any(w in last_msg for w in ["visit", "travel", "tour", "trip"]):
            return "travel"
        elif any(w in last_msg for w in ["chabad", "rabbi", "jewish", "shabbat"]):
            return "chabad"
        elif any(w in last_msg for w in ["competitor", "other swimmer", "recruiting class"]):
            return "competitors"
        elif any(w in last_msg for w in ["engineering", "real estate", "major", "minor"]):
            return "engineering"
        elif any(w in last_msg for w in ["meet", "race", "prepare", "strategy"]):
            return "meet_prep"
        elif any(w in last_msg for w in ["result", "split", "performance"]):
            return "meet_results"
        elif any(w in last_msg for w in ["progress", "improve", "goal", "target", "uf readiness"]):
            return "improvements"
        elif any(w in last_msg for w in ["email", "coach", "recruit", "outreach"]):
            return "recruiting"
        else:
            return "improvements"
    
    # Add routing
    workflow.add_conditional_edges(
        "__start__",
        route_request,
        {name: name for name in agents.keys()}
    )
    
    # All agents flow to synthesize
    for name in agents.keys():
        workflow.add_edge(name, "synthesize")
    
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()


def synthesize_all_agents(state: D1PathwayStateV2) -> dict:
    """Synthesize outputs from all agents"""
    
    uf_score = state.get("uf_readiness_score", 0)
    days = state.get("days_to_recruitment", 0)
    
    return {
        "messages": [{
            "role": "assistant",
            "content": f"D1 Pathway V2 Update | UF Readiness: {uf_score}/100 | Days to signing: {days}",
            "timestamp": datetime.now().isoformat()
        }],
        "current_agent": "synthesize",
        "last_updated": datetime.now().isoformat()
    }


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_michael_state_v2() -> D1PathwayStateV2:
    """Initialize Michael's D1 pathway state V2"""
    return {
        "profile": {
            "name": "Michael Shapira",
            "dob": "2009-07-22",
            "age": 16,
            "height": "6'4\"",
            "weight": 215,
            "high_school": "Satellite Beach High School",
            "graduation_year": 2027,
            "current_club": "Swim Melbourne (MELB-FL)",
            "events": ["50 Free", "100 Free", "200 Free", "100 Fly", "50 Fly", "100 Back"],
            "sat_score": 1280,
            "gpa": 3.5,
            "dietary_requirements": "Kosher",
            "primary_target": "University of Florida",
            "academic_major": "Engineering",
            "academic_minor": "Real Estate"
        },
        "swim_times": {
            "fifty_free": "23.22",
            "hundred_free": "50.82",
            "two_hundred_free": "",
            "hundred_fly": "57.21",
            "fifty_fly": "25.79",
            "hundred_back": "1:01.62",
            "fifty_back": "31.00",
            "last_updated": "2025-12-12"
        },
        "target_schools": TARGET_SCHOOLS_PRIORITY,
        "messages": [],
        "current_agent": "",
        "last_updated": datetime.now().isoformat(),
        "errors": [],
        "uf_readiness_score": 0.0,
        "days_to_recruitment": 0
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("🏊 Michael Shapira D1 Pathway - LangGraph Orchestrator V2")
    print("=" * 60)
    print("PRIMARY TARGET: University of Florida - Class of 2027")
    print("ACADEMIC: Engineering + Real Estate Minor")
    print("=" * 60)
    
    state = initialize_michael_state_v2()
    graph = create_d1_pathway_graph_v2()
    
    # Run improvements agent to get UF readiness
    result = graph.invoke(state)
    
    print(f"\n✅ D1 Pathway V2 initialized")
    print(f"📊 UF Readiness Score: {result.get('uf_readiness_score', 'calculating...')}")
    print(f"📅 Days to signing period: {result.get('days_to_recruitment', 'calculating...')}")
    
    # Save state
    with open("d1_pathway_state_v2.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 State saved to d1_pathway_state_v2.json")
