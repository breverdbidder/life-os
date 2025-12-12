"""
Michael D1 Pathway - Specialized Agents
========================================
Multi-agent orchestration for D1 swimming pathway.
Target: UF 2027 (Anthony Nesty, Head Coach)
"""

from agents.diet_agent import diet_agent_node, KosherDietAgent
from agents.education_agent import education_agent_node, EducationAgent
from agents.travel_agent import travel_agent_node, TravelAgent
from agents.chabad_agent import chabad_agent_node, ChabadAgent
from agents.competitors_agent import competitors_agent_node, CompetitorsAgent
from agents.engineering_agent import engineering_agent_node, EngineeringAgent
from agents.meet_prep_agent import meet_prep_agent_node, MeetPrepAgent
from agents.meet_results_agent import meet_results_agent_node, MeetResultsAgent
from agents.improvements_agent import improvements_agent_node, ImprovementsAgent
from agents.school_compare_agent import school_compare_agent_node, SchoolCompareAgent
from agents.uf_recruiting_agent import uf_recruiting_agent_node, UFRecruitingAgent

__all__ = [
    # Node Functions
    "diet_agent_node",
    "education_agent_node", 
    "travel_agent_node",
    "chabad_agent_node",
    "competitors_agent_node",
    "engineering_agent_node",
    "meet_prep_agent_node",
    "meet_results_agent_node",
    "improvements_agent_node",
    "school_compare_agent_node",
    "uf_recruiting_agent_node",
    # Agent Classes
    "KosherDietAgent",
    "EducationAgent",
    "TravelAgent", 
    "ChabadAgent",
    "CompetitorsAgent",
    "EngineeringAgent",
    "MeetPrepAgent",
    "MeetResultsAgent",
    "ImprovementsAgent",
    "SchoolCompareAgent",
    "UFRecruitingAgent"
]

AGENTS = {
    "diet": {"node": diet_agent_node, "class": KosherDietAgent, "description": "Kosher Meal & Diet Preparation"},
    "education": {"node": education_agent_node, "class": EducationAgent, "description": "Education Achievement"},
    "travel": {"node": travel_agent_node, "class": TravelAgent, "description": "School Visit Travel"},
    "chabad": {"node": chabad_agent_node, "class": ChabadAgent, "description": "Chabad Contacts"},
    "competitors": {"node": competitors_agent_node, "class": CompetitorsAgent, "description": "Competitor Analysis"},
    "engineering": {"node": engineering_agent_node, "class": EngineeringAgent, "description": "Engineering Opportunities"},
    "meet_prep": {"node": meet_prep_agent_node, "class": MeetPrepAgent, "description": "Meet Preparation"},
    "meet_results": {"node": meet_results_agent_node, "class": MeetResultsAgent, "description": "Meet Results"},
    "improvements": {"node": improvements_agent_node, "class": ImprovementsAgent, "description": "Goals Achievement"},
    "school_compare": {"node": school_compare_agent_node, "class": SchoolCompareAgent, "description": "School Comparison"},
    "uf_recruiting": {"node": uf_recruiting_agent_node, "class": UFRecruitingAgent, "description": "UF Recruiting"}
}
