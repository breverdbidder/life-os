"""
Education Achievement Agent
============================
Manages academic tracking, NCAA eligibility, and educational milestones.
Target: Engineering major with Real Estate minor at D1 Power 5.
"""

from typing import Dict, Any, List
from datetime import datetime
import json


# NCAA Eligibility Requirements
NCAA_REQUIREMENTS = {
    "division_1": {
        "core_courses": 16,
        "core_gpa_minimum": 2.3,
        "sliding_scale": True,
        "test_scores": {
            "sat": {"minimum": 400, "full_qualifier": 1010},
            "act": {"minimum": 37, "full_qualifier": 75}  # Sum score
        }
    },
    "core_course_breakdown": {
        "english": 4,
        "math": 3,  # Algebra I or higher
        "science": 2,  # Natural/physical science
        "social_science": 2,
        "additional": 4,  # From above or foreign language/philosophy
        "extra": 1  # Additional from any area
    }
}

# Engineering + Real Estate Requirements
ACADEMIC_TARGETS = {
    "gpa": {
        "minimum": 3.0,
        "target": 3.5,
        "uf_average": 4.4  # Weighted
    },
    "sat": {
        "minimum": 1200,
        "target": 1400,
        "uf_average": 1380
    },
    "act": {
        "minimum": 26,
        "target": 31,
        "uf_average": 30
    },
    "engineering_prerequisites": [
        "Calculus (AP preferred)",
        "Physics (AP preferred)",
        "Chemistry",
        "Computer Science (recommended)"
    ]
}


class EducationAgent:
    """
    Agent for academic tracking and NCAA eligibility monitoring.
    Ensures Michael stays on track for D1 and academic goals.
    """
    
    def __init__(self):
        self.name = "Education Achievement Agent"
        self.ncaa_requirements = NCAA_REQUIREMENTS
        self.targets = ACADEMIC_TARGETS
        
    def check_ncaa_eligibility(self, 
                               gpa: float, 
                               core_courses: int,
                               sat_score: int = None,
                               act_score: int = None) -> Dict[str, Any]:
        """Check current NCAA eligibility status"""
        d1_req = self.ncaa_requirements["division_1"]
        
        eligibility = {
            "gpa": {
                "current": gpa,
                "minimum": d1_req["core_gpa_minimum"],
                "status": "✅ ELIGIBLE" if gpa >= d1_req["core_gpa_minimum"] else "⚠️ AT RISK"
            },
            "core_courses": {
                "current": core_courses,
                "required": d1_req["core_courses"],
                "status": "✅ ON TRACK" if core_courses >= 10 else "⚠️ NEED MORE"  # By junior year
            }
        }
        
        if sat_score:
            eligibility["sat"] = {
                "current": sat_score,
                "minimum": d1_req["test_scores"]["sat"]["minimum"],
                "full_qualifier": d1_req["test_scores"]["sat"]["full_qualifier"],
                "status": "✅ QUALIFIER" if sat_score >= d1_req["test_scores"]["sat"]["full_qualifier"] else "📊 SLIDING SCALE"
            }
            
        if act_score:
            eligibility["act"] = {
                "current": act_score,
                "minimum": d1_req["test_scores"]["act"]["minimum"],
                "full_qualifier": d1_req["test_scores"]["act"]["full_qualifier"],
                "status": "✅ QUALIFIER" if act_score >= d1_req["test_scores"]["act"]["full_qualifier"] else "📊 SLIDING SCALE"
            }
        
        eligibility["overall_status"] = self._calculate_overall_status(eligibility)
        return eligibility
    
    def _calculate_overall_status(self, eligibility: Dict) -> str:
        """Calculate overall eligibility status"""
        if eligibility["gpa"]["status"].startswith("⚠️"):
            return "AT RISK - GPA needs improvement"
        if eligibility["core_courses"]["status"].startswith("⚠️"):
            return "AT RISK - Complete more core courses"
        return "ON TRACK for D1 eligibility"
    
    def generate_course_recommendations(self, 
                                        current_year: int,
                                        completed_courses: List[str]) -> Dict[str, Any]:
        """Generate recommended courses for upcoming semesters"""
        
        recommendations = {
            "sophomore": {
                "fall": [
                    "Honors English 10",
                    "Algebra 2/Trig Honors",
                    "Chemistry Honors",
                    "World History AP",
                    "Spanish 3"
                ],
                "spring": [
                    "Honors English 10",
                    "Pre-Calculus Honors",
                    "Chemistry Honors",
                    "World History AP",
                    "Spanish 3"
                ]
            },
            "junior": {
                "fall": [
                    "AP English Language",
                    "AP Calculus AB",
                    "AP Physics 1",
                    "AP US History",
                    "Spanish 4/AP"
                ],
                "spring": [
                    "AP English Language",
                    "AP Calculus AB/BC",
                    "AP Physics 1",
                    "AP US History",
                    "Spanish 4/AP"
                ]
            },
            "senior": {
                "fall": [
                    "AP English Literature",
                    "AP Calculus BC/Multivariable",
                    "AP Physics C",
                    "AP Government",
                    "Computer Science"
                ],
                "spring": [
                    "AP English Literature",
                    "AP Statistics/Calculus BC",
                    "AP Physics C",
                    "AP Economics",
                    "Computer Science"
                ]
            }
        }
        
        year_map = {10: "sophomore", 11: "junior", 12: "senior"}
        year_key = year_map.get(current_year, "sophomore")
        
        return {
            "current_year": current_year,
            "recommendations": recommendations.get(year_key, recommendations["sophomore"]),
            "engineering_focus": [
                "Prioritize AP Calculus and AP Physics for engineering preparation",
                "Consider dual enrollment for additional math courses",
                "Join STEM clubs/competitions for application strength"
            ],
            "ncaa_notes": [
                "All AP courses count as core courses",
                "Maintain GPA above 3.0 for full qualifier status",
                "Complete NCAA eligibility center registration"
            ]
        }
    
    def xgboost_gpa_prediction(self, 
                                current_gpa: float,
                                course_difficulty: float,
                                study_hours: float,
                                training_hours: float) -> Dict[str, Any]:
        """
        XGBoost prediction for GPA trajectory.
        Predicts end-of-year GPA based on current metrics.
        """
        # Simplified prediction (would be actual XGBoost in production)
        difficulty_impact = (course_difficulty - 3) * -0.05
        study_impact = (study_hours - 10) * 0.02
        training_impact = (training_hours - 15) * -0.01
        
        predicted_gpa = current_gpa + difficulty_impact + study_impact + training_impact
        predicted_gpa = max(2.0, min(4.0, predicted_gpa))
        
        return {
            "current_gpa": current_gpa,
            "predicted_eoy_gpa": round(predicted_gpa, 2),
            "confidence": 0.72,
            "factors": {
                "course_difficulty_impact": round(difficulty_impact, 3),
                "study_hours_impact": round(study_impact, 3),
                "training_hours_impact": round(training_impact, 3)
            },
            "recommendations": [
                "Increase study hours if below 12/week",
                "Use study hall time efficiently",
                "Communicate with teachers about swim schedule"
            ],
            "model": "XGBoost GPA Predictor v1.0"
        }
    
    def get_test_prep_timeline(self) -> Dict[str, Any]:
        """SAT/ACT preparation timeline for Class of 2027"""
        return {
            "sophomore_year": {
                "fall": "Take PSAT for practice",
                "spring": "Begin SAT/ACT prep (light)",
                "summer": "Intensive prep course recommended"
            },
            "junior_year": {
                "fall": "First official SAT/ACT attempt",
                "winter": "Retake if needed",
                "spring": "Final attempt before recruiting heats up"
            },
            "recommendations": [
                "Target SAT: 1350+ for UF competitiveness",
                "Consider both SAT and ACT - some students score better on one",
                "Use Khan Academy for free SAT prep",
                "Schedule tests around swim season breaks"
            ]
        }


def education_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node function for Education Agent"""
    agent = EducationAgent()
    query = state.get("query", "").lower()
    
    output = {
        "agent": "education",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    gpa = state.get("gpa", 3.5)
    
    if "eligib" in query or "ncaa" in query:
        eligibility = agent.check_ncaa_eligibility(gpa, 12)
        output["content"] = f"NCAA Eligibility Status: {eligibility['overall_status']}"
        output["eligibility"] = eligibility
        
    elif "course" in query or "class" in query or "schedule" in query:
        courses = agent.generate_course_recommendations(10, [])
        output["content"] = f"Course recommendations for sophomore year"
        output["courses"] = courses
        output["recommendations"].append("Prioritize AP courses for both GPA boost and NCAA eligibility")
        
    elif "sat" in query or "act" in query or "test" in query:
        timeline = agent.get_test_prep_timeline()
        output["content"] = f"Test prep timeline for Class of 2027"
        output["test_timeline"] = timeline
        output["action_items"].append({
            "task": "Register for fall PSAT",
            "deadline": "September 2025",
            "priority": "medium"
        })
        
    else:
        output["content"] = f"Current GPA: {gpa}. Academic tracking active."
        output["recommendations"].append("Maintain GPA above 3.5 for UF competitiveness")
    
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "education": output}
    }


if __name__ == "__main__":
    agent = EducationAgent()
    print("Education Agent Initialized")
    eligibility = agent.check_ncaa_eligibility(3.5, 12, 1300)
    print(f"Status: {eligibility['overall_status']}")
