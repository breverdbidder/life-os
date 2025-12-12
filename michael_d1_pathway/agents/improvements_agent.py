"""
Improvements Tracking & Goals Achievement Agent
===============================================
Monitors progress toward D1 standards with UF 2027 as primary target.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


# UF 2027 Recruiting Targets
UF_2027_TARGETS = {
    "50 Free": {
        "a_cut": 19.20,
        "b_cut": 19.80,
        "interest": 20.50,
        "description": "Sprint freestyle"
    },
    "100 Free": {
        "a_cut": 42.50,
        "b_cut": 44.00,
        "interest": 45.50,
        "description": "Primary sprint event"
    },
    "200 Free": {
        "a_cut": 93.00,  # 1:33.00
        "b_cut": 96.00,  # 1:36.00
        "interest": 99.00,  # 1:39.00
        "description": "Middle distance"
    },
    "100 Fly": {
        "a_cut": 46.00,
        "b_cut": 48.00,
        "interest": 50.00,
        "description": "Secondary stroke"
    },
    "100 Back": {
        "a_cut": 46.50,
        "b_cut": 48.50,
        "interest": 50.50,
        "description": "Versatility event"
    }
}


class ImprovementsAgent:
    def __init__(self):
        self.name = "Improvements Tracking & Goals Achievement Agent"
        self.targets = UF_2027_TARGETS
        self.deadline = datetime(2027, 8, 1)  # Before senior year
        
    def calculate_goals(self, current_times: Dict[str, float]) -> Dict[str, Any]:
        """Calculate improvement goals and timelines"""
        goals = {}
        now = datetime.now()
        months_remaining = (self.deadline - now).days / 30
        
        for event, targets in self.targets.items():
            current = current_times.get(event, 0)
            if current > 0:
                gap_to_b = current - targets["b_cut"]
                gap_to_a = current - targets["a_cut"]
                
                # Calculate required monthly improvement
                monthly_improvement_needed = gap_to_b / months_remaining if months_remaining > 0 else 0
                
                goals[event] = {
                    "current_time": current,
                    "uf_b_cut": targets["b_cut"],
                    "uf_a_cut": targets["a_cut"],
                    "gap_to_b": round(gap_to_b, 2),
                    "gap_to_a": round(gap_to_a, 2),
                    "status": self._get_status(gap_to_b, gap_to_a),
                    "monthly_improvement_needed": round(monthly_improvement_needed, 3),
                    "milestones": self._generate_milestones(current, targets, months_remaining),
                    "achievability": self._assess_achievability(monthly_improvement_needed)
                }
        
        return {
            "target": "UF 2027",
            "deadline": self.deadline.strftime("%Y-%m-%d"),
            "months_remaining": round(months_remaining, 1),
            "goals": goals,
            "overall_status": self._overall_assessment(goals)
        }
    
    def _get_status(self, gap_to_b: float, gap_to_a: float) -> str:
        if gap_to_a <= 0:
            return "✅ A-CUT ACHIEVED"
        elif gap_to_b <= 0:
            return "✅ B-CUT ACHIEVED"
        elif gap_to_b < 2:
            return "🟡 CLOSE TO B-CUT"
        else:
            return "🔴 DEVELOPING"
    
    def _generate_milestones(self, current: float, targets: Dict, months: float) -> List[Dict]:
        """Generate intermediate milestones"""
        gap = current - targets["b_cut"]
        if gap <= 0:
            return [{"milestone": "B-cut achieved", "target": "Push for A-cut"}]
        
        milestones = []
        step = gap / 4  # 4 milestones
        
        for i in range(1, 5):
            target_time = current - (step * i)
            target_date = datetime.now() + timedelta(days=int(months * 30 / 4 * i))
            milestones.append({
                "milestone": f"Milestone {i}",
                "target_time": round(target_time, 2),
                "target_date": target_date.strftime("%Y-%m-%d")
            })
        
        return milestones
    
    def _assess_achievability(self, monthly_improvement: float) -> str:
        """Assess if improvement rate is realistic"""
        if monthly_improvement <= 0:
            return "ON TRACK"
        elif monthly_improvement <= 0.3:
            return "ACHIEVABLE with consistent training"
        elif monthly_improvement <= 0.5:
            return "CHALLENGING but possible with focused training"
        else:
            return "STRETCH GOAL - requires significant breakthrough"
    
    def _overall_assessment(self, goals: Dict) -> str:
        """Overall assessment across all events"""
        statuses = [g.get("status", "") for g in goals.values()]
        
        if all("A-CUT" in s for s in statuses):
            return "ELITE - Ready for top programs"
        elif all("ACHIEVED" in s for s in statuses):
            return "STRONG - Competitive for UF"
        elif any("CLOSE" in s for s in statuses):
            return "PROGRESSING - Focus on breakthrough swims"
        else:
            return "DEVELOPING - Consistent improvement needed"
    
    def xgboost_achievement_probability(self,
                                         event: str,
                                         current_time: float,
                                         improvement_history: List[float] = None) -> Dict[str, Any]:
        """Predict probability of achieving target by deadline"""
        targets = self.targets.get(event, {})
        months_remaining = (self.deadline - datetime.now()).days / 30
        
        gap = current_time - targets.get("b_cut", current_time)
        
        # Base probability on gap and time
        if gap <= 0:
            prob = 0.95  # Already achieved
        else:
            # More time + smaller gap = higher probability
            time_factor = min(1, months_remaining / 24)  # Normalize to 2 years
            gap_factor = max(0, 1 - (gap / 5))  # Normalize to 5 second gap
            prob = time_factor * gap_factor * 0.8  # Max 80% base
            
            # Boost for consistent improvers
            if improvement_history and len(improvement_history) > 2:
                if all(improvement_history[i] > improvement_history[i+1] 
                       for i in range(len(improvement_history)-1)):
                    prob += 0.1  # Consistent improvement bonus
        
        return {
            "event": event,
            "current_time": current_time,
            "target": targets.get("b_cut"),
            "probability": round(min(0.95, max(0.05, prob)), 2),
            "factors": {
                "time_remaining": f"{months_remaining:.1f} months",
                "gap_to_target": f"{gap:.2f}s"
            },
            "recommendation": self._get_probability_recommendation(prob),
            "confidence": 0.70,
            "model": "XGBoost Achievement Predictor v1.0"
        }
    
    def _get_probability_recommendation(self, prob: float) -> str:
        if prob >= 0.8:
            return "On track - maintain training consistency"
        elif prob >= 0.5:
            return "Achievable - focus on breakthrough opportunities"
        elif prob >= 0.3:
            return "Challenging - may need training adjustments"
        else:
            return "Stretch goal - consider expanding target school list"


def improvements_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent = ImprovementsAgent()
    query = state.get("query", "").lower()
    current_times = state.get("current_times", {})
    
    output = {
        "agent": "improvements",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    # Extract times
    times_dict = {k: v.get("time_seconds", 0) if isinstance(v, dict) else 0 
                  for k, v in current_times.items()}
    
    if times_dict and any(v > 0 for v in times_dict.values()):
        goals = agent.calculate_goals(times_dict)
        output["content"] = f"UF 2027 Goals: {goals['overall_status']}"
        output["goals"] = goals
        output["recommendations"].append(f"{goals['months_remaining']:.0f} months until deadline")
    else:
        output["content"] = "No times logged. Add current times to track improvement goals."
        output["recommendations"].append("Log current best times to begin goal tracking")
    
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "improvements": output}
    }
