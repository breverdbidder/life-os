"""
Michael D1 Pathway - LangGraph State Management
================================================
Centralized state for multi-agent orchestration system.
Target: UF 2027 Class (Anthony Nesty, Head Coach)
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime
import operator


class MichaelProfile(TypedDict):
    """Michael Shapira's core profile data"""
    name: str
    dob: str  # July 22, 2009
    high_school: str  # Satellite Beach HS
    graduation_year: int  # 2027
    target_events: List[str]  # 50/100/200 Free, 100 Fly, 100 Back
    academic_focus: str  # Engineering
    minor_priority: str  # Real Estate
    dietary_protocol: str  # Kosher Keto (Mon-Thu strict, Fri-Sun moderate)


class SwimPerformance(TypedDict):
    """Swimming performance metrics"""
    event: str
    time_seconds: float
    time_display: str
    meet_name: str
    date: str
    course: str  # SCY, SCM, LCM
    splits: Optional[List[float]]
    improvement_from_pb: Optional[float]


class UFRecruitingStandards(TypedDict):
    """UF 2027 recruiting time standards"""
    event: str
    target_time: float
    current_time: float
    gap_seconds: float
    on_track: bool
    probability_achieve: float  # XGBoost prediction


class AgentMessage(TypedDict):
    """Inter-agent communication message"""
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    priority: int  # 1-5, 5 being highest


class D1PathwayState(TypedDict):
    """
    Central state for the Michael D1 Pathway orchestration system.
    All agents read from and write to this shared state.
    """
    # Core Profile
    profile: MichaelProfile
    
    # Current Query/Task
    query: str
    intent: str
    active_agents: List[str]
    
    # Swimming Performance Data
    current_times: Dict[str, SwimPerformance]
    personal_bests: Dict[str, SwimPerformance]
    uf_standards: Dict[str, UFRecruitingStandards]
    improvement_trajectory: Dict[str, Any]
    
    # Academic Data
    gpa: float
    courses: List[Dict[str, Any]]
    test_scores: Dict[str, int]
    academic_eligibility: bool
    
    # Nutrition/Diet
    current_meal_plan: Dict[str, Any]
    macro_targets: Dict[str, float]
    kosher_compliance: bool
    
    # School Visits & Travel
    scheduled_visits: List[Dict[str, Any]]
    visit_history: List[Dict[str, Any]]
    travel_budget: float
    
    # Target Schools Analysis
    target_schools: List[Dict[str, Any]]
    school_rankings: Dict[str, float]  # XGBoost match scores
    uf_analysis: Dict[str, Any]  # Priority target detailed analysis
    
    # Competitor Analysis
    competitors: Dict[str, List[SwimPerformance]]
    recruiting_class_ranking: Dict[str, int]
    
    # Chabad/Community
    chabad_contacts: Dict[str, Dict[str, Any]]
    
    # Agent Communication
    messages: Annotated[List[AgentMessage], operator.add]
    agent_outputs: Dict[str, Any]
    
    # XGBoost Predictions
    ml_predictions: Dict[str, Dict[str, float]]
    
    # Final Response
    response: str
    recommendations: List[str]
    action_items: List[Dict[str, Any]]


def get_initial_state() -> D1PathwayState:
    """Initialize state with Michael's profile"""
    return D1PathwayState(
        profile=MichaelProfile(
            name="Michael Shapira",
            dob="2009-07-22",
            high_school="Satellite Beach High School",
            graduation_year=2027,
            target_events=["50 Free", "100 Free", "200 Free", "100 Fly", "100 Back"],
            academic_focus="Engineering",
            minor_priority="Real Estate",
            dietary_protocol="Kosher Keto (Michael Andrew Framework)"
        ),
        query="",
        intent="",
        active_agents=[],
        current_times={},
        personal_bests={},
        uf_standards={
            "50 Free": UFRecruitingStandards(
                event="50 Free",
                target_time=19.50,  # UF recruiting standard
                current_time=0.0,
                gap_seconds=0.0,
                on_track=False,
                probability_achieve=0.0
            ),
            "100 Free": UFRecruitingStandards(
                event="100 Free",
                target_time=43.50,
                current_time=0.0,
                gap_seconds=0.0,
                on_track=False,
                probability_achieve=0.0
            ),
            "200 Free": UFRecruitingStandards(
                event="200 Free",
                target_time=96.00,  # 1:36.00
                current_time=0.0,
                gap_seconds=0.0,
                on_track=False,
                probability_achieve=0.0
            ),
            "100 Fly": UFRecruitingStandards(
                event="100 Fly",
                target_time=47.50,
                current_time=0.0,
                gap_seconds=0.0,
                on_track=False,
                probability_achieve=0.0
            ),
            "100 Back": UFRecruitingStandards(
                event="100 Back",
                target_time=48.00,
                current_time=0.0,
                gap_seconds=0.0,
                on_track=False,
                probability_achieve=0.0
            )
        },
        improvement_trajectory={},
        gpa=0.0,
        courses=[],
        test_scores={},
        academic_eligibility=True,
        current_meal_plan={},
        macro_targets={
            "protein_g": 180,
            "fat_g": 150,
            "carbs_weekday_g": 30,
            "carbs_shabbat_g": 100,
            "calories": 3000
        },
        kosher_compliance=True,
        scheduled_visits=[],
        visit_history=[],
        travel_budget=5000.0,
        target_schools=[
            {"name": "University of Florida", "priority": 1, "status": "primary"},
            {"name": "University of Texas", "priority": 2, "status": "target"},
            {"name": "NC State", "priority": 3, "status": "target"},
            {"name": "University of Georgia", "priority": 4, "status": "target"},
            {"name": "Auburn University", "priority": 5, "status": "target"}
        ],
        school_rankings={},
        uf_analysis={
            "coach": "Anthony Nesty",
            "program_rank": 1,
            "engineering_rank": 15,
            "real_estate_minor": True,
            "chabad_present": True
        },
        competitors={},
        recruiting_class_ranking={},
        chabad_contacts={},
        messages=[],
        agent_outputs={},
        ml_predictions={},
        response="",
        recommendations=[],
        action_items=[]
    )
