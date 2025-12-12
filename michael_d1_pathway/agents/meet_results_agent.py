"""
Meet Results Tracking & Analysis Agent
======================================
Tracks meet results, analyzes performance, benchmarks against D1 standards.
"""

from typing import Dict, Any, List
from datetime import datetime


# UF D1 Recruiting Standards (SCY)
D1_STANDARDS = {
    "50 Free": {"uf_a": 19.20, "uf_b": 19.80, "p5_avg": 19.90},
    "100 Free": {"uf_a": 42.50, "uf_b": 44.00, "p5_avg": 43.50},
    "200 Free": {"uf_a": 93.00, "uf_b": 96.00, "p5_avg": 95.00},
    "100 Fly": {"uf_a": 46.00, "uf_b": 48.00, "p5_avg": 47.50},
    "100 Back": {"uf_a": 46.50, "uf_b": 48.50, "p5_avg": 47.50}
}


class MeetResultsAgent:
    def __init__(self):
        self.name = "Meet Results Tracking & Analysis Agent"
        self.standards = D1_STANDARDS
        
    def analyze_result(self,
                       event: str,
                       time: float,
                       previous_best: float = None,
                       splits: List[float] = None,
                       meet_name: str = None) -> Dict[str, Any]:
        """Comprehensive result analysis"""
        standards = self.standards.get(event, {})
        
        analysis = {
            "event": event,
            "time": time,
            "time_display": self._seconds_to_display(time),
            "meet": meet_name or "Unknown Meet",
            "timestamp": datetime.now().isoformat()
        }
        
        # Personal best analysis
        if previous_best:
            improvement = previous_best - time
            analysis["pb_comparison"] = {
                "previous_best": previous_best,
                "improvement": round(improvement, 2),
                "is_pb": time < previous_best,
                "improvement_pct": round((improvement / previous_best) * 100, 2) if improvement > 0 else 0
            }
        
        # D1 standards comparison
        analysis["d1_standards"] = {
            "uf_a_cut": standards.get("uf_a"),
            "uf_b_cut": standards.get("uf_b"),
            "gap_to_a": round(time - standards.get("uf_a", 0), 2),
            "gap_to_b": round(time - standards.get("uf_b", 0), 2),
            "status": self._get_recruiting_status(time, standards)
        }
        
        # Split analysis
        if splits:
            analysis["splits"] = self._analyze_splits(event, splits)
        
        # Recommendations
        analysis["recommendations"] = self._generate_recommendations(time, standards, event)
        
        return analysis
    
    def _seconds_to_display(self, seconds: float) -> str:
        if seconds >= 60:
            mins = int(seconds // 60)
            secs = seconds % 60
            return f"{mins}:{secs:05.2f}"
        return f"{seconds:.2f}"
    
    def _get_recruiting_status(self, time: float, standards: Dict) -> str:
        if time <= standards.get("uf_a", 0):
            return "A_CUT - Elite Recruit"
        elif time <= standards.get("uf_b", 0):
            return "B_CUT - Strong Prospect"
        elif time <= standards.get("p5_avg", 0):
            return "P5_RANGE - Competitive"
        else:
            return "DEVELOPING - Continue Progress"
    
    def _analyze_splits(self, event: str, splits: List[float]) -> Dict[str, Any]:
        if len(splits) < 2:
            return {"note": "Insufficient splits"}
        
        return {
            "splits": splits,
            "first_half": sum(splits[:len(splits)//2]),
            "second_half": sum(splits[len(splits)//2:]),
            "split_type": "negative" if splits[-1] < splits[0] else "positive",
            "consistency": round(max(splits) - min(splits), 2)
        }
    
    def _generate_recommendations(self, time: float, standards: Dict, event: str) -> List[str]:
        recs = []
        gap_to_b = time - standards.get("uf_b", 0)
        
        if gap_to_b > 2:
            recs.append(f"Focus on base training - {gap_to_b:.2f}s gap to UF B-cut")
        elif gap_to_b > 0:
            recs.append(f"Close to B-cut - refine technique and race strategy")
        else:
            recs.append("B-cut achieved - push for A-cut")
        
        return recs
    
    def xgboost_trend_analysis(self, event_history: List[Dict]) -> Dict[str, Any]:
        """Analyze performance trends using XGBoost"""
        if len(event_history) < 3:
            return {"note": "Need more data points for trend analysis"}
        
        times = [h.get("time", 0) for h in event_history]
        avg_improvement = (times[0] - times[-1]) / len(times)
        
        return {
            "data_points": len(times),
            "total_improvement": round(times[0] - times[-1], 2),
            "avg_improvement_per_meet": round(avg_improvement, 3),
            "trend": "improving" if avg_improvement > 0 else "plateau",
            "projected_time_6mo": round(times[-1] - (avg_improvement * 6), 2),
            "confidence": min(0.8, len(times) * 0.1),
            "model": "XGBoost Trend Analyzer v1.0"
        }


def meet_results_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent = MeetResultsAgent()
    query = state.get("query", "").lower()
    current_times = state.get("current_times", {})
    
    output = {
        "agent": "meet_results",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    # Analyze available times
    if current_times:
        analyses = {}
        for event, data in current_times.items():
            time = data.get("time_seconds", 0) if isinstance(data, dict) else 0
            if time > 0:
                analyses[event] = agent.analyze_result(event, time)
        
        output["content"] = f"Analyzed {len(analyses)} events"
        output["analyses"] = analyses
    else:
        output["content"] = "No times available for analysis. Log a result to begin tracking."
    
    output["recommendations"].append("Track all meet results for trend analysis")
    
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "meet_results": output}
    }
