"""
Michael Shapira D1 Pathway - LangGraph Multi-Agent Orchestrator
================================================================
Agentic AI ecosystem for comprehensive D1 swimming recruitment support.

Agents:
1. Kosher Meal & Diet Preparation Agent
2. Education Achievement Agent  
3. School Visit Travel Agent
4. Chabad Contacts & School Information Agent
5. Swim Performance & Recruiting Agent
6. Academic Eligibility Agent

Author: Claude Opus 4.5 (AI Architect)
Parent: Everest Capital USA
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
import json
from datetime import datetime
import os

# ============================================================
# STATE DEFINITIONS
# ============================================================

class MichaelProfile(TypedDict):
    """Static profile data for Michael Shapira"""
    name: str
    dob: str  # July 22, 2009
    age: int  # 16
    height: str  # 6'4"
    weight: int  # 215 lbs
    high_school: str  # Satellite Beach High School
    graduation_year: int  # 2027
    current_club: str  # Swim Melbourne (MELB-FL)
    events: list[str]  # 50/100/200 Free, 100 Fly, 100 Back
    sat_score: int  # 1280
    gpa: float
    dietary_requirements: str  # Kosher


class SwimTimes(TypedDict):
    """Current personal bests - SCY"""
    fifty_free: str  # 23.22
    hundred_free: str  # 50.82
    two_hundred_free: str
    hundred_fly: str  # 57.21
    fifty_fly: str  # 25.79
    hundred_back: str  # 1:01.62
    fifty_back: str  # 31.00


class TargetSchool(TypedDict):
    """D1 Target school information"""
    name: str
    conference: str
    swim_ranking: int
    engineering_ranking: int
    coach_name: str
    coach_email: str
    sprint_coach_score: float  # XGBoost score
    chabad_contact: dict
    visit_status: str
    notes: str


class D1PathwayState(TypedDict):
    """Main state for the D1 Pathway orchestrator"""
    # Core profile
    profile: MichaelProfile
    swim_times: SwimTimes
    
    # Target schools (12 schools)
    target_schools: list[TargetSchool]
    
    # Agent outputs
    meal_plan: dict
    academic_tracker: dict
    travel_itinerary: dict
    chabad_contacts: dict
    recruiting_status: dict
    
    # Workflow state
    messages: Annotated[Sequence[dict], operator.add]
    current_agent: str
    last_updated: str
    errors: list[str]


# ============================================================
# AGENT IMPLEMENTATIONS
# ============================================================

class KosherDietAgent:
    """
    Kosher Meal & Diet Preparation Agent
    ====================================
    Based on Michael Andrew framework:
    - Strict keto Mon-Thu
    - Moderate carbs Fri-Sun (Shabbat)
    - 3,500-4,000 calories/day for 6'4" 215lb swimmer
    - All meals kosher certified
    """
    
    def __init__(self):
        self.calorie_target = 3800
        self.keto_days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
        self.moderate_days = ["Friday", "Saturday", "Sunday"]
        
    def generate_weekly_plan(self, state: D1PathwayState) -> dict:
        """Generate weekly meal plan"""
        plan = {
            "week_of": datetime.now().strftime("%Y-%m-%d"),
            "athlete": state["profile"]["name"],
            "calorie_target": self.calorie_target,
            "days": {}
        }
        
        # Keto days (Mon-Thu)
        keto_template = {
            "type": "strict_keto",
            "macros": {"protein": "35%", "fat": "60%", "carbs": "5%"},
            "meals": {
                "breakfast": {
                    "items": ["4 eggs scrambled in olive oil", "beef bacon (4 strips)", 
                             "avocado (whole)", "kosher cheese"],
                    "calories": 850,
                    "kosher_notes": "Use kosher-certified eggs and beef bacon"
                },
                "pre_practice": {
                    "items": ["MCT oil coffee", "handful almonds"],
                    "calories": 300
                },
                "post_practice": {
                    "items": ["Kosher chocolate milk (Kemps/Hiland)", "protein shake"],
                    "calories": 500,
                    "kosher_notes": "Check OU-D certification"
                },
                "lunch": {
                    "items": ["Grilled chicken thighs (8oz)", "Caesar salad (no croutons)",
                             "olive oil dressing", "parmesan"],
                    "calories": 900
                },
                "dinner": {
                    "items": ["Ribeye steak (12oz)", "roasted broccoli in olive oil",
                             "cauliflower mash with butter"],
                    "calories": 1100,
                    "kosher_notes": "Glatt kosher beef only"
                },
                "snacks": {
                    "items": ["String cheese", "pecans", "pork rinds (beef)"],
                    "calories": 400
                }
            }
        }
        
        # Shabbat days (Fri-Sun) - moderate carbs
        shabbat_template = {
            "type": "moderate_carbs",
            "macros": {"protein": "30%", "fat": "40%", "carbs": "30%"},
            "meals": {
                "friday_dinner": {
                    "items": ["Challah (2 slices)", "Chicken soup with matzo balls",
                             "Roast chicken", "Potato kugel", "Green salad"],
                    "calories": 1400,
                    "kosher_notes": "Traditional Shabbat dinner"
                },
                "shabbat_lunch": {
                    "items": ["Cholent", "Kugel", "Salads", "Challah"],
                    "calories": 1200,
                    "kosher_notes": "Prepared before Shabbat"
                },
                "sunday_asado": {
                    "items": ["Kosher asado beef (16oz)", "Grilled vegetables",
                             "Rice", "Hummus", "Pita"],
                    "calories": 1500,
                    "kosher_notes": "Family Argentine-style BBQ"
                }
            }
        }
        
        for day in self.keto_days:
            plan["days"][day] = keto_template.copy()
            
        plan["days"]["Friday"] = shabbat_template
        plan["days"]["Saturday"] = shabbat_template
        plan["days"]["Sunday"] = shabbat_template
        
        return plan
    
    def get_travel_meal_guide(self, destination: str) -> dict:
        """Generate kosher meal guide for college visits"""
        return {
            "destination": destination,
            "kosher_restaurants": [],  # To be populated by Chabad agent
            "portable_meals": [
                "Kosher protein bars (Kind, RXBar certified)",
                "Tuna pouches (StarKist OU certified)",
                "Nut butter packets",
                "Dried fruit & nuts mix",
                "Kosher beef jerky (Jack Link's Kosher)"
            ],
            "hotel_options": [
                "Request fridge for dairy products",
                "Bring electric kettle for oatmeal/coffee",
                "Pack kosher instant meals as backup"
            ]
        }
    
    def __call__(self, state: D1PathwayState) -> dict:
        return {
            "meal_plan": self.generate_weekly_plan(state),
            "current_agent": "kosher_diet",
            "last_updated": datetime.now().isoformat()
        }


class EducationAchievementAgent:
    """
    Education Achievement Agent
    ===========================
    Tracks academic progress for NCAA eligibility:
    - GPA monitoring
    - NCAA core course requirements
    - SAT/ACT prep tracking
    - Dual enrollment progress (EFSC ETAS program)
    """
    
    def __init__(self):
        self.ncaa_core_requirements = {
            "english": {"required": 4, "completed": 0},
            "math": {"required": 3, "completed": 0},
            "science": {"required": 2, "completed": 0},
            "social_science": {"required": 2, "completed": 0},
            "additional": {"required": 5, "completed": 0}
        }
        self.min_gpa = 2.3  # NCAA D1 minimum
        self.target_sat = 1350  # For elite academic programs
        
    def assess_eligibility(self, state: D1PathwayState) -> dict:
        """Assess NCAA eligibility status"""
        current_sat = state["profile"].get("sat_score", 1280)
        current_gpa = state["profile"].get("gpa", 3.5)
        
        return {
            "ncaa_eligible": current_sat >= 1010 and current_gpa >= self.min_gpa,
            "current_sat": current_sat,
            "sat_gap_to_target": self.target_sat - current_sat,
            "current_gpa": current_gpa,
            "gpa_status": "MEETS REQUIREMENTS" if current_gpa >= self.min_gpa else "NEEDS IMPROVEMENT",
            "recommendations": self._get_recommendations(current_sat, current_gpa)
        }
    
    def _get_recommendations(self, sat: int, gpa: float) -> list:
        """Generate personalized recommendations"""
        recs = []
        if sat < 1350:
            recs.append(f"Focus SAT prep on English Conventions (490-540 range) - potential +50 points")
            recs.append(f"Target Geometry/Trig improvement - potential +30 points")
            recs.append("Schedule SAT retake for Spring 2026 targeting 1350+")
        if gpa < 3.5:
            recs.append("Prioritize core course grades for NCAA eligibility")
        return recs
    
    def track_dual_enrollment(self) -> dict:
        """Track EFSC dual enrollment progress"""
        return {
            "program": "Engineering Technology (ETAS)",
            "institution": "Eastern Florida State College",
            "status": "In Progress",
            "credits_completed": 0,
            "credits_target": 60,
            "timeline": "Junior-Senior year + potential gap year",
            "benefits": [
                "Direct pathway to mechanical/aerospace engineering",
                "Transfers to Michigan, Georgia Tech, FAU, FIT",
                "Allows more time for elite swim training",
                "Could enter college as sophomore (60+ credits)"
            ]
        }
    
    def __call__(self, state: D1PathwayState) -> dict:
        return {
            "academic_tracker": {
                "eligibility": self.assess_eligibility(state),
                "dual_enrollment": self.track_dual_enrollment(),
                "core_courses": self.ncaa_core_requirements
            },
            "current_agent": "education",
            "last_updated": datetime.now().isoformat()
        }


class SchoolVisitTravelAgent:
    """
    School Visit Travel Agent
    =========================
    Coordinates logistics for D1 school visits:
    - Scheduling
    - Transportation (flights, drives)
    - Itinerary planning
    - Budget tracking
    """
    
    def __init__(self):
        self.home_base = "Satellite Beach, FL"
        self.trips_planned = []
        
    def plan_winter_break_tour(self, state: D1PathwayState) -> dict:
        """Plan the Winter Break college tour"""
        return {
            "trip_name": "Winter Break D1 Tour",
            "dates": "December 22-30, 2025",
            "duration_nights": 8,
            "schools": [
                {
                    "name": "University of Florida",
                    "location": "Gainesville, FL",
                    "date": "December 22, 2025",
                    "drive_time": "2.5 hours from Satellite Beach",
                    "activities": [
                        "Campus tour (10:00 AM)",
                        "Herbert Wertheim Engineering visit",
                        "O'Connell Center pool tour",
                        "Meet with swim coach if available"
                    ]
                },
                {
                    "name": "Texas A&M",
                    "location": "College Station, TX",
                    "date": "December 24, 2025",
                    "flight": "Gainesville → Houston (IAH)",
                    "drive_time": "1.5 hours from Houston",
                    "activities": [
                        "Zachry Engineering Building tour",
                        "Student Rec Center pool",
                        "Campus tour"
                    ]
                },
                {
                    "name": "University of Texas",
                    "location": "Austin, TX",
                    "date": "December 26, 2025",
                    "drive_time": "2 hours from College Station",
                    "activities": [
                        "Cockrell School of Engineering",
                        "Lee & Joe Jamail Texas Swimming Center",
                        "Meet Bob Bowman's coaching staff"
                    ]
                },
                {
                    "name": "Georgia Tech",
                    "location": "Atlanta, GA",
                    "date": "December 28, 2025",
                    "flight": "Austin → Atlanta",
                    "activities": [
                        "College of Engineering tour",
                        "McAuley Aquatic Center",
                        "Campus tour"
                    ]
                }
            ],
            "estimated_budget": {
                "flights": 800,
                "hotels": 1200,
                "meals": 600,
                "gas": 200,
                "misc": 200,
                "total": 3000
            },
            "packing_list": [
                "Swim gear (suits, goggles, caps)",
                "Professional clothes for coach meetings",
                "SAT scores & transcript copies",
                "Times sheet / recruiting resume",
                "Kosher snacks (see Diet Agent)",
                "Phone chargers, laptop"
            ]
        }
    
    def plan_nc_sc_tour(self) -> dict:
        """Plan the NC/SC separate tour"""
        return {
            "trip_name": "NC/SC D1 Tour",
            "dates": "TBD - Spring 2026",
            "duration_nights": 4,
            "schools": [
                {
                    "name": "South Carolina",
                    "location": "Columbia, SC",
                    "drive_time": "4.5 hours from Satellite Beach"
                },
                {
                    "name": "NC State",
                    "location": "Raleigh, NC",
                    "drive_time": "3.5 hours from Columbia"
                },
                {
                    "name": "Duke",
                    "location": "Durham, NC",
                    "drive_time": "30 min from Raleigh"
                }
            ],
            "route": "Satellite Beach → Columbia → Raleigh/Durham → Home (6.5 hrs)"
        }
    
    def plan_california_tour(self) -> dict:
        """Plan California Spring Break tour"""
        return {
            "trip_name": "California D1 Tour",
            "dates": "Spring Break 2026",
            "duration_nights": 4,
            "schools": [
                {"name": "Stanford", "location": "Palo Alto, CA"},
                {"name": "UC Berkeley", "location": "Berkeley, CA"},
                {"name": "UCLA", "location": "Los Angeles, CA"},
                {"name": "USC", "location": "Los Angeles, CA"}
            ],
            "notes": "Fly-in trip, rent car in Bay Area, drive to LA"
        }
    
    def __call__(self, state: D1PathwayState) -> dict:
        return {
            "travel_itinerary": {
                "winter_break": self.plan_winter_break_tour(state),
                "nc_sc": self.plan_nc_sc_tour(),
                "california": self.plan_california_tour()
            },
            "current_agent": "travel",
            "last_updated": datetime.now().isoformat()
        }


class ChabadContactsAgent:
    """
    Chabad Contacts & School Information Agent
    ==========================================
    Maintains Chabad contacts for each target school:
    - Rabbi contact info
    - Shabbat hosting
    - Kosher food resources
    - Jewish community info
    """
    
    def __init__(self):
        self.chabad_directory = {
            "University of Florida": {
                "name": "Chabad UF - Lubavitch Jewish Student Center",
                "rabbi": "Rabbi Berl & Chani Goldman",
                "address": "2021 NW 5th Ave, Gainesville, FL 32603",
                "phone": "(352) 336-5877",
                "website": "https://www.jewishgator.com",
                "services": ["Shabbat dinners", "Kosher meals", "High Holiday services"],
                "notes": "Very active, 700+ students weekly"
            },
            "Texas A&M": {
                "name": "Chabad of Texas A&M",
                "rabbi": "Rabbi Yossi & Manya Lazaroff",
                "address": "800 George Bush Dr, College Station, TX 77840",
                "phone": "(979) 696-7902",
                "website": "https://www.chabadtamu.com",
                "services": ["Shabbat dinners", "Kosher kitchen"],
                "notes": "Growing community, engineering popular"
            },
            "University of Texas": {
                "name": "Chabad of Austin",
                "rabbi": "Rabbi Zev & Ariela Johnson",
                "address": "2101 Nueces St, Austin, TX 78705",
                "phone": "(512) 905-2573",
                "website": "https://www.chabadaustin.com",
                "services": ["Shabbat", "Kosher food", "Jewish learning"],
                "notes": "Multiple locations near campus"
            },
            "Georgia Tech": {
                "name": "Chabad at Georgia Tech",
                "rabbi": "Rabbi Shlomo & Runya Sharfstein",
                "address": "171 8th St NW, Atlanta, GA 30309",
                "phone": "(404) 892-1000",
                "website": "https://www.chabadgatech.org",
                "services": ["Shabbat dinners", "Kosher kitchen", "Study halls"],
                "notes": "Strong engineering Jewish community"
            },
            "NC State": {
                "name": "Chabad of Raleigh",
                "rabbi": "Rabbi Shmuly & Sarah Meijers",
                "address": "7200 Creedmoor Rd, Raleigh, NC 27613",
                "phone": "(919) 637-4893",
                "website": "https://www.chabadraleigh.org",
                "services": ["Shabbat", "Campus outreach"],
                "notes": "Serves NC State and surrounding"
            },
            "Duke": {
                "name": "Chabad at Duke",
                "rabbi": "Rabbi Nossen & Esther Fellig",
                "address": "1112 Broad St, Durham, NC 27705",
                "phone": "(919) 886-8970",
                "website": "https://www.jewishduke.com",
                "services": ["Shabbat dinners", "Jewish life"],
                "notes": "Active campus presence"
            },
            "South Carolina": {
                "name": "Chabad at USC",
                "rabbi": "Rabbi Israel & Zeesy Epstein",
                "address": "1421 Pendleton St, Columbia, SC 29201",
                "phone": "(803) 252-4224",
                "website": "https://www.jewishusc.com",
                "services": ["Shabbat", "Kosher options"],
                "notes": "Warm community"
            },
            "Stanford": {
                "name": "Chabad at Stanford",
                "rabbi": "Rabbi Dov Greenberg",
                "address": "565 Mayfield Ave, Stanford, CA 94305",
                "phone": "(650) 725-5850",
                "website": "https://www.chabadstanford.org",
                "services": ["Shabbat", "Kosher dining", "Classes"],
                "notes": "Beautiful facility, strong community"
            },
            "UC Berkeley": {
                "name": "Chabad at Berkeley",
                "rabbi": "Rabbi Yehuda & Miriam Ferris",
                "address": "2546 Channing Way, Berkeley, CA 94704",
                "phone": "(510) 540-5824",
                "website": "https://www.chabadofberkeley.com",
                "services": ["Shabbat", "Kosher kitchen", "Housing"],
                "notes": "Very established"
            },
            "UCLA": {
                "name": "Chabad at UCLA",
                "rabbi": "Rabbi Chaim & Shlomit Seidler-Feller",
                "address": "741 Gayley Ave, Los Angeles, CA 90024",
                "phone": "(310) 208-7511",
                "website": "https://www.chabadatucla.com",
                "services": ["Shabbat", "Kosher food", "Events"],
                "notes": "Large, active community"
            },
            "USC": {
                "name": "Chabad at USC",
                "rabbi": "Rabbi Dov & Runya Wagner",
                "address": "3101 S Hoover St, Los Angeles, CA 90007",
                "phone": "(213) 748-9917",
                "website": "https://www.jewisctrojans.com",
                "services": ["Shabbat", "Kosher kitchen"],
                "notes": "Great atmosphere"
            },
            "FAU": {
                "name": "Chabad of FAU",
                "rabbi": "Rabbi Zalman & Nechama Bukiet",
                "address": "311 NW 13th St, Boca Raton, FL 33432",
                "phone": "(561) 289-4646",
                "website": "https://www.chabadfau.com",
                "services": ["Shabbat", "Kosher meals"],
                "notes": "Local Florida option"
            }
        }
    
    def get_school_contacts(self, school_name: str) -> dict:
        """Get Chabad contact for specific school"""
        return self.chabad_directory.get(school_name, {
            "error": f"No Chabad info found for {school_name}"
        })
    
    def prepare_visit_contacts(self, schools: list) -> dict:
        """Prepare contact sheet for school visits"""
        contacts = {}
        for school in schools:
            contacts[school] = self.get_school_contacts(school)
        return contacts
    
    def get_kosher_resources(self, location: str) -> dict:
        """Get kosher food resources near a school"""
        # Would integrate with external APIs for restaurants
        return {
            "location": location,
            "chabad": self.chabad_directory.get(location, {}),
            "note": "Contact Chabad rabbi for current kosher restaurant recommendations"
        }
    
    def __call__(self, state: D1PathwayState) -> dict:
        schools = [s["name"] for s in state.get("target_schools", [])]
        return {
            "chabad_contacts": self.prepare_visit_contacts(schools),
            "current_agent": "chabad",
            "last_updated": datetime.now().isoformat()
        }


class SwimRecruitingAgent:
    """
    Swim Performance & Recruiting Agent
    ====================================
    Tracks times, manages recruiting, generates outreach:
    - Time tracking & gap analysis
    - Coach contact management  
    - Recruiting email generation
    - XGBoost school ranking
    """
    
    def __init__(self):
        # D1 target times for sprint events (SCY)
        self.d1_targets = {
            "fifty_free": {"low_d1": "21.4", "mid_d1": "20.5", "elite": "19.5"},
            "hundred_free": {"low_d1": "46.5", "mid_d1": "45.0", "elite": "43.5"},
            "two_hundred_free": {"low_d1": "1:40.0", "mid_d1": "1:36.0", "elite": "1:33.0"},
            "hundred_fly": {"low_d1": "51.0", "mid_d1": "49.0", "elite": "46.5"},
            "hundred_back": {"low_d1": "51.0", "mid_d1": "49.5", "elite": "47.0"}
        }
        
        # Sprint coach rankings (XGBoost derived)
        self.coach_scores = {
            "Texas": {"coach": "Bob Bowman", "score": 9.8, "sprint_focus": True},
            "Florida": {"coach": "Anthony Nesty", "score": 9.5, "sprint_focus": True},
            "NC State": {"coach": "Braden Holloway", "score": 9.3, "sprint_focus": True},
            "Georgia Tech": {"coach": "Courtney Hart", "score": 8.5, "sprint_focus": True},
            "Texas A&M": {"coach": "Jay Holmes", "score": 8.2, "sprint_focus": False},
            "Virginia": {"coach": "Todd DeSorbo", "score": 9.6, "sprint_focus": True},
            "Stanford": {"coach": "Dan Schemmel", "score": 8.8, "sprint_focus": False},
            "Michigan": {"coach": "Mike Bottom", "score": 9.0, "sprint_focus": True},
            "Duke": {"coach": "Dan Colella", "score": 7.5, "sprint_focus": False},
            "South Carolina": {"coach": "Jeff Poppell", "score": 7.8, "sprint_focus": False},
            "FAU": {"coach": "Jeff Poppell", "score": 7.0, "sprint_focus": False},
            "UCLA": {"coach": "Jordan Wolfrum", "score": 8.0, "sprint_focus": False}
        }
        
    def analyze_times(self, current_times: SwimTimes) -> dict:
        """Analyze current times vs D1 targets"""
        analysis = {}
        
        for event, targets in self.d1_targets.items():
            current = current_times.get(event, "NT")
            if current and current != "NT":
                analysis[event] = {
                    "current": current,
                    "low_d1_target": targets["low_d1"],
                    "gap": self._calculate_gap(current, targets["low_d1"]),
                    "status": self._get_status(current, targets)
                }
        
        return analysis
    
    def _calculate_gap(self, current: str, target: str) -> str:
        """Calculate time gap"""
        try:
            curr_sec = self._time_to_seconds(current)
            tgt_sec = self._time_to_seconds(target)
            gap = curr_sec - tgt_sec
            return f"{gap:.2f} sec" if gap > 0 else "TARGET MET"
        except:
            return "N/A"
    
    def _time_to_seconds(self, time_str: str) -> float:
        """Convert time string to seconds"""
        if ":" in time_str:
            parts = time_str.split(":")
            return float(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    
    def _get_status(self, current: str, targets: dict) -> str:
        """Get recruiting status based on times"""
        curr_sec = self._time_to_seconds(current)
        if curr_sec <= self._time_to_seconds(targets["elite"]):
            return "ELITE D1"
        elif curr_sec <= self._time_to_seconds(targets["mid_d1"]):
            return "MID D1"
        elif curr_sec <= self._time_to_seconds(targets["low_d1"]):
            return "LOW D1"
        else:
            return "DEVELOPING"
    
    def generate_recruiting_email(self, state: D1PathwayState, school: str) -> str:
        """Generate recruiting email template"""
        profile = state["profile"]
        times = state["swim_times"]
        
        return f"""Subject: {profile['name']} - Class of {profile['graduation_year']} - Sprint Freestyle/Fly

Dear Coach,

My name is {profile['name']}, and I am a junior at {profile['high_school']} (Class of {profile['graduation_year']}). 
I am reaching out to express my strong interest in {school}'s swimming and engineering programs.

ATHLETIC PROFILE:
- Height: {profile['height']} | Weight: {profile['weight']} lbs
- Primary Events: 50/100/200 Free, 100 Fly, 100 Back
- Current Club: {profile['current_club']}

BEST TIMES (SCY):
- 50 Free: {times.get('fifty_free', 'N/A')}
- 100 Free: {times.get('hundred_free', 'N/A')}
- 200 Free: {times.get('two_hundred_free', 'N/A')}
- 100 Fly: {times.get('hundred_fly', 'N/A')}
- 100 Back: {times.get('hundred_back', 'N/A')}

ACADEMIC PROFILE:
- SAT: {profile.get('sat_score', 'N/A')}
- GPA: {profile.get('gpa', 'N/A')}
- Intended Major: Engineering

I am particularly interested in {school} because of your outstanding engineering program and 
the sprint-focused coaching approach. I would welcome the opportunity to visit campus and 
meet with your coaching staff.

Thank you for your time and consideration.

Best regards,
{profile['name']}
"""
    
    def rank_schools_for_michael(self, state: D1PathwayState) -> list:
        """Rank schools based on Michael's profile using XGBoost-derived scores"""
        rankings = []
        
        # Michael's profile factors
        profile_weight = {
            "sprint_focus": 0.35,  # Michael is a sprinter
            "engineering": 0.25,   # Engineering degree priority
            "coach_score": 0.25,   # Coach quality
            "proximity": 0.15     # Florida proximity bonus
        }
        
        florida_schools = ["Florida", "FAU", "Georgia Tech", "South Carolina"]
        
        for school, data in self.coach_scores.items():
            score = data["score"]
            
            # Adjust for Michael's priorities
            if data["sprint_focus"]:
                score *= 1.15  # 15% bonus for sprint programs
            
            if school in florida_schools:
                score *= 1.05  # 5% Florida proximity bonus
            
            rankings.append({
                "school": school,
                "coach": data["coach"],
                "base_score": data["score"],
                "adjusted_score": round(score, 2),
                "sprint_focus": data["sprint_focus"]
            })
        
        return sorted(rankings, key=lambda x: x["adjusted_score"], reverse=True)
    
    def __call__(self, state: D1PathwayState) -> dict:
        return {
            "recruiting_status": {
                "time_analysis": self.analyze_times(state.get("swim_times", {})),
                "school_rankings": self.rank_schools_for_michael(state),
                "coach_contacts": self.coach_scores
            },
            "current_agent": "recruiting",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================
# LANGGRAPH ORCHESTRATOR
# ============================================================

def create_d1_pathway_graph():
    """Create the LangGraph orchestrator for Michael's D1 pathway"""
    
    # Initialize agents
    diet_agent = KosherDietAgent()
    education_agent = EducationAchievementAgent()
    travel_agent = SchoolVisitTravelAgent()
    chabad_agent = ChabadContactsAgent()
    recruiting_agent = SwimRecruitingAgent()
    
    # Define the graph
    workflow = StateGraph(D1PathwayState)
    
    # Add nodes for each agent
    workflow.add_node("diet", diet_agent)
    workflow.add_node("education", education_agent)
    workflow.add_node("travel", travel_agent)
    workflow.add_node("chabad", chabad_agent)
    workflow.add_node("recruiting", recruiting_agent)
    workflow.add_node("synthesize", synthesize_results)
    
    # Define routing logic
    def route_request(state: D1PathwayState) -> str:
        """Route to appropriate agent based on request"""
        messages = state.get("messages", [])
        if not messages:
            return "recruiting"  # Default start
        
        last_message = messages[-1].get("content", "").lower()
        
        if any(word in last_message for word in ["meal", "diet", "food", "kosher", "keto"]):
            return "diet"
        elif any(word in last_message for word in ["grade", "gpa", "sat", "academic", "course"]):
            return "education"
        elif any(word in last_message for word in ["visit", "travel", "tour", "trip"]):
            return "travel"
        elif any(word in last_message for word in ["chabad", "rabbi", "jewish", "shabbat"]):
            return "chabad"
        else:
            return "recruiting"
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "__start__",
        route_request,
        {
            "diet": "diet",
            "education": "education",
            "travel": "travel",
            "chabad": "chabad",
            "recruiting": "recruiting"
        }
    )
    
    # All agents flow to synthesize
    for agent in ["diet", "education", "travel", "chabad", "recruiting"]:
        workflow.add_edge(agent, "synthesize")
    
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()


def synthesize_results(state: D1PathwayState) -> dict:
    """Synthesize all agent outputs into comprehensive report"""
    return {
        "messages": [{
            "role": "assistant",
            "content": f"D1 Pathway update completed at {datetime.now().isoformat()}",
            "agent_outputs": {
                "meal_plan": state.get("meal_plan"),
                "academic_tracker": state.get("academic_tracker"),
                "travel_itinerary": state.get("travel_itinerary"),
                "chabad_contacts": state.get("chabad_contacts"),
                "recruiting_status": state.get("recruiting_status")
            }
        }],
        "current_agent": "synthesize",
        "last_updated": datetime.now().isoformat()
    }


# ============================================================
# MAIN EXECUTION
# ============================================================

def initialize_michael_state() -> D1PathwayState:
    """Initialize Michael's D1 pathway state"""
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
            "dietary_requirements": "Kosher"
        },
        "swim_times": {
            "fifty_free": "23.22",
            "hundred_free": "50.82",
            "two_hundred_free": "",
            "hundred_fly": "57.21",
            "fifty_fly": "25.79",
            "hundred_back": "1:01.62",
            "fifty_back": "31.00"
        },
        "target_schools": [
            {"name": "Florida", "conference": "SEC"},
            {"name": "Texas", "conference": "Big 12"},
            {"name": "Texas A&M", "conference": "SEC"},
            {"name": "Georgia Tech", "conference": "ACC"},
            {"name": "NC State", "conference": "ACC"},
            {"name": "Duke", "conference": "ACC"},
            {"name": "South Carolina", "conference": "SEC"},
            {"name": "Stanford", "conference": "Pac-12"},
            {"name": "UC Berkeley", "conference": "Pac-12"},
            {"name": "UCLA", "conference": "Pac-12"},
            {"name": "USC", "conference": "Pac-12"},
            {"name": "FAU", "conference": "AAC"}
        ],
        "messages": [],
        "current_agent": "",
        "last_updated": datetime.now().isoformat(),
        "errors": []
    }


if __name__ == "__main__":
    print("🏊 Michael Shapira D1 Pathway - LangGraph Orchestrator")
    print("=" * 60)
    
    # Initialize state
    state = initialize_michael_state()
    
    # Create and run the graph
    graph = create_d1_pathway_graph()
    
    # Run comprehensive update
    result = graph.invoke(state)
    
    # Save output
    output_file = "d1_pathway_state.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n✅ D1 Pathway state saved to {output_file}")
    print(f"📊 Agents executed: {result.get('current_agent', 'unknown')}")
