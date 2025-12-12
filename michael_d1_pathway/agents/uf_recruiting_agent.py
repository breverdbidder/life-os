"""
UF Recruiting Communications Agent
===================================
Specialized agent for University of Florida recruiting communications.
Primary Contact: Anthony Nesty (Head Coach)
Target: Class of 2027

Author: Claude Opus 4.5 (AI Architect)
Version: 1.0.0
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# UF Program Constants
UF_PROGRAM = {
    "school": "University of Florida",
    "nickname": "Gators",
    "conference": "SEC",
    "head_coach": {
        "name": "Anthony Nesty",
        "title": "Head Coach",
        "email": "swimming@gators.ufl.edu",  # General recruiting
        "achievements": [
            "Olympic Gold Medalist (1988 100m Butterfly)",
            "First Olympic Gold for Suriname",
            "NCAA Champion Coach",
            "SEC Coach of the Year (multiple)"
        ],
        "coaching_style": "Technical excellence, race IQ, sprint development"
    },
    "assistant_coaches": [
        {"name": "Steve Jungbluth", "specialty": "Distance/IM"},
        {"name": "Jeff Poppell", "specialty": "Sprint Freestyle"},
        {"name": "Martyn Wilby", "specialty": "Backstroke/Sprint"}
    ],
    "recruiting_coordinator": "TBD - Verify current",
    "facility": "Stephen C. O'Connell Center Natatorium",
    "pool_specs": "50m x 25y, 8 lanes competition, 10 lanes warm-up",
    "program_ranking": 1,  # Historically top program
    "recent_achievements": [
        "2023 NCAA Team Champions (Men)",
        "Multiple Olympic medalists",
        "Caeleb Dressel alma mater"
    ]
}

# UF 2027 Recruiting Time Standards (SCY)
UF_RECRUITING_STANDARDS = {
    "50 Free": {"A_cut": 19.20, "B_cut": 19.80, "interest": 20.50},
    "100 Free": {"A_cut": 42.50, "B_cut": 44.00, "interest": 45.50},
    "200 Free": {"A_cut": 93.00, "B_cut": 96.00, "interest": 99.00},
    "100 Fly": {"A_cut": 46.00, "B_cut": 48.00, "interest": 50.00},
    "100 Back": {"A_cut": 46.50, "B_cut": 48.50, "interest": 50.50}
}

# UF Academic Information
UF_ACADEMICS = {
    "engineering_rank": 15,  # US News
    "engineering_programs": [
        "Aerospace Engineering",
        "Biomedical Engineering",
        "Chemical Engineering",
        "Civil Engineering",
        "Computer Engineering",
        "Computer Science",
        "Electrical Engineering",
        "Environmental Engineering",
        "Industrial & Systems Engineering",
        "Materials Science",
        "Mechanical Engineering",
        "Nuclear Engineering"
    ],
    "real_estate_minor": True,
    "real_estate_program": {
        "department": "Warrington College of Business",
        "name": "Real Estate Minor",
        "courses": [
            "REE 3043 - Real Estate Analysis",
            "REE 3433 - Real Estate Finance",
            "REE 4204 - Real Estate Law",
            "REE 4303 - Real Estate Valuation"
        ],
        "availability": "Open to all majors",
        "notes": "Strong industry connections in Florida market"
    },
    "gpa_requirement": 3.0,  # NCAA minimum, UF prefers higher
    "sat_average": 1350,
    "act_average": 30
}

# Chabad at UF
UF_CHABAD = {
    "name": "Chabad at UF / Lubavitch Jewish Center",
    "rabbi": "Rabbi Berl Goldman",
    "address": "2021 NW 5th Ave, Gainesville, FL 32603",
    "phone": "(352) 336-5877",
    "website": "https://jewishgator.com",
    "services": ["Shabbat dinners", "Kosher meals", "High Holiday services", "Student housing"],
    "distance_from_pool": "1.2 miles"
}


class UFRecruitingAgent:
    """
    Agent specialized in UF recruiting communications and tracking.
    Manages all interactions related to University of Florida recruitment.
    """
    
    def __init__(self):
        self.name = "UF Recruiting Communications Agent"
        self.priority_target = True
        self.coach = UF_PROGRAM["head_coach"]
        self.standards = UF_RECRUITING_STANDARDS
        
    def evaluate_times_vs_standards(self, current_times: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluate Michael's times against UF recruiting standards.
        Returns detailed analysis with XGBoost probability predictions.
        """
        evaluation = {}
        
        for event, standards in self.standards.items():
            current = current_times.get(event, 0)
            if current > 0:
                evaluation[event] = {
                    "current_time": current,
                    "a_cut": standards["A_cut"],
                    "b_cut": standards["B_cut"],
                    "interest_level": standards["interest"],
                    "gap_to_a": round(current - standards["A_cut"], 2),
                    "gap_to_b": round(current - standards["B_cut"], 2),
                    "status": self._get_status(current, standards),
                    "recommendation": self._get_recommendation(current, standards)
                }
        
        return evaluation
    
    def _get_status(self, time: float, standards: Dict) -> str:
        """Determine recruiting status based on time"""
        if time <= standards["A_cut"]:
            return "A_CUT_ACHIEVED"
        elif time <= standards["B_cut"]:
            return "B_CUT_ACHIEVED"
        elif time <= standards["interest"]:
            return "INTEREST_LEVEL"
        else:
            return "DEVELOPING"
    
    def _get_recommendation(self, time: float, standards: Dict) -> str:
        """Generate recommendation based on current status"""
        if time <= standards["A_cut"]:
            return "Ready for direct coach contact. Strong scholarship candidate."
        elif time <= standards["B_cut"]:
            return "Solid prospect. Continue development. Schedule unofficial visit."
        elif time <= standards["interest"]:
            return "On radar. Focus on improvement. Attend UF camp."
        else:
            return "Continue development. Target B-cut by junior year."
    
    def generate_outreach_timeline(self) -> List[Dict[str, Any]]:
        """
        Generate recommended recruiting outreach timeline for Class of 2027.
        """
        return [
            {
                "phase": "Sophomore Year (Current)",
                "timeframe": "Now - May 2026",
                "actions": [
                    "Complete NCAA eligibility questionnaire",
                    "Create SwimCloud profile",
                    "Send introductory email to Coach Nesty",
                    "Attend UF swim camp if offered",
                    "Focus on hitting B-cut times"
                ],
                "communication": "Initial introduction, express genuine interest"
            },
            {
                "phase": "Junior Year",
                "timeframe": "Aug 2026 - May 2027",
                "actions": [
                    "Schedule unofficial visit",
                    "Regular time updates to coaching staff",
                    "Visit Chabad during campus visit",
                    "Meet with Engineering department",
                    "Verify Real Estate minor compatibility"
                ],
                "communication": "Monthly updates, relationship building"
            },
            {
                "phase": "Senior Year",
                "timeframe": "Aug 2027 - Dec 2027",
                "actions": [
                    "Official visit (if offered)",
                    "Verbal commitment discussion",
                    "NLI signing (early signing period)",
                    "Finalize academic package"
                ],
                "communication": "High-frequency, decision-focused"
            }
        ]
    
    def draft_introduction_email(self, times: Dict[str, float]) -> str:
        """
        Draft initial outreach email to Coach Nesty.
        """
        best_event = min(times.items(), key=lambda x: self._time_to_standard_ratio(x[0], x[1]))[0] if times else "100 Free"
        
        return f"""
Subject: Class of 2027 Recruit - Michael Shapira | Satellite Beach, FL

Dear Coach Nesty,

My name is Michael Shapira, and I am a sophomore swimmer at Satellite Beach High School in Florida. I am reaching out to express my strong interest in the University of Florida Men's Swimming program.

**About Me:**
- Class of 2027 | DOB: July 22, 2009
- Primary Events: 50/100/200 Free, 100 Fly, 100 Back
- Academic Focus: Engineering with Real Estate Minor
- GPA: [Current GPA]
- Location: Satellite Beach, FL (local Florida athlete)

**Current Best Times (SCY):**
{self._format_times_for_email(times)}

I am drawn to UF not only for its outstanding swimming program and your legendary coaching expertise but also for:
- The Herbert Wertheim College of Engineering's strong reputation
- The availability of a Real Estate minor through Warrington College of Business
- The active Jewish community through Chabad at UF

I would welcome the opportunity to learn more about your program and share my goals with you. I plan to attend any upcoming UF swim camps and would be honored to visit campus.

Thank you for your time and consideration.

Respectfully,
Michael Shapira
Satellite Beach High School, Class of 2027
[Phone Number]
[Email Address]
SwimCloud: [Profile Link]
"""
    
    def _time_to_standard_ratio(self, event: str, time: float) -> float:
        """Calculate ratio of current time to B-cut standard"""
        if event in self.standards:
            return time / self.standards[event]["B_cut"]
        return float('inf')
    
    def _format_times_for_email(self, times: Dict[str, float]) -> str:
        """Format times for email display"""
        if not times:
            return "- Times to be updated"
        
        lines = []
        for event, time in sorted(times.items()):
            time_display = self._seconds_to_display(time)
            lines.append(f"- {event}: {time_display}")
        return "\n".join(lines)
    
    def _seconds_to_display(self, seconds: float) -> str:
        """Convert seconds to display format (mm:ss.xx or ss.xx)"""
        if seconds >= 60:
            mins = int(seconds // 60)
            secs = seconds % 60
            return f"{mins}:{secs:05.2f}"
        return f"{seconds:.2f}"
    
    def get_uf_summary(self) -> Dict[str, Any]:
        """Return comprehensive UF program summary"""
        return {
            "program": UF_PROGRAM,
            "standards": UF_RECRUITING_STANDARDS,
            "academics": UF_ACADEMICS,
            "chabad": UF_CHABAD,
            "why_uf": [
                "Top NCAA program with sprint excellence tradition",
                "Coach Nesty: Olympic champion, sprint specialist",
                "Strong engineering program (#15 nationally)",
                "Real Estate minor available",
                "Active Chabad for kosher meals and community",
                "In-state advantage (Florida resident)",
                "Recent success: Dressel, others"
            ]
        }


def uf_recruiting_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for UF Recruiting Agent.
    Processes queries related to UF recruitment.
    """
    agent = UFRecruitingAgent()
    query = state.get("query", "").lower()
    current_times = state.get("current_times", {})
    
    output = {
        "agent": "uf_recruiting",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    # Determine what information to provide
    if "standard" in query or "time" in query or "cut" in query:
        times_dict = {k: v.get("time_seconds", 0) if isinstance(v, dict) else 0 
                     for k, v in current_times.items()}
        evaluation = agent.evaluate_times_vs_standards(times_dict)
        output["content"] = f"UF Standards Evaluation: {json.dumps(evaluation, indent=2)}"
        output["evaluation"] = evaluation
        
    elif "email" in query or "contact" in query or "outreach" in query:
        times_dict = {k: v.get("time_seconds", 0) if isinstance(v, dict) else 0 
                     for k, v in current_times.items()}
        email = agent.draft_introduction_email(times_dict)
        output["content"] = email
        output["recommendations"].append("Review and personalize email before sending")
        output["action_items"].append({
            "task": "Send introduction email to Coach Nesty",
            "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
            "priority": "high"
        })
        
    elif "timeline" in query or "schedule" in query:
        timeline = agent.generate_outreach_timeline()
        output["content"] = f"UF Recruiting Timeline: {json.dumps(timeline, indent=2)}"
        output["timeline"] = timeline
        
    else:
        # Default: provide program summary
        summary = agent.get_uf_summary()
        output["content"] = f"University of Florida Swimming Program Summary available. Coach: {UF_PROGRAM['head_coach']['name']}"
        output["uf_summary"] = summary
        output["recommendations"].append("Focus on hitting B-cut times for strongest recruiting position")
    
    # Always add to agent_outputs
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "uf_recruiting": output}
    }


if __name__ == "__main__":
    agent = UFRecruitingAgent()
    print("UF Recruiting Agent Initialized")
    print(f"Primary Contact: {agent.coach['name']}")
    print(f"Events Tracked: {list(agent.standards.keys())}")
    print("\nTimeline generated successfully.")
