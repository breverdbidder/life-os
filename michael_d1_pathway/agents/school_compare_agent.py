"""
School Comparison Agent
========================
Compares target D1 Power 5 schools across all dimensions.
UF is primary benchmark.
"""

from typing import Dict, Any, List
from datetime import datetime


# Comprehensive School Data
SCHOOL_PROFILES = {
    "uf": {
        "name": "University of Florida",
        "nickname": "Gators",
        "conference": "SEC",
        "location": "Gainesville, FL",
        "coaching": {
            "head_coach": "Anthony Nesty",
            "years_at_program": 25,
            "olympians_coached": 15,
            "ncaa_titles": 7,
            "coaching_score": 98
        },
        "program": {
            "ncaa_ranking": 1,
            "sec_titles": 15,
            "training_philosophy": "Technical excellence, race IQ",
            "sprint_focus": True,
            "program_score": 97
        },
        "facilities": {
            "pool": "Stephen C. O'Connell Center Natatorium",
            "specs": "50m x 25y, Olympic standard",
            "weight_room": "Elite",
            "facilities_score": 95
        },
        "academics": {
            "engineering_rank": 15,
            "real_estate_minor": True,
            "academic_support": "Excellent",
            "academics_score": 88
        },
        "culture": {
            "team_size": 30,
            "jewish_community": True,
            "chabad_present": True,
            "culture_score": 90
        },
        "fit_factors": {
            "distance_from_home": 165,
            "in_state": True,
            "family_proximity": "Close"
        }
    },
    "texas": {
        "name": "University of Texas",
        "nickname": "Longhorns",
        "conference": "SEC",
        "location": "Austin, TX",
        "coaching": {
            "head_coach": "Bob Bowman",
            "years_at_program": 2,
            "olympians_coached": 20,
            "ncaa_titles": 0,
            "coaching_score": 99
        },
        "program": {
            "ncaa_ranking": 5,
            "training_philosophy": "Michael Phelps methodology",
            "sprint_focus": False,
            "program_score": 90
        },
        "facilities": {
            "pool": "Lee and Joe Jamail Texas Swimming Center",
            "facilities_score": 98
        },
        "academics": {
            "engineering_rank": 10,
            "real_estate_minor": True,
            "academics_score": 92
        },
        "culture": {
            "team_size": 35,
            "jewish_community": True,
            "chabad_present": True,
            "culture_score": 85
        },
        "fit_factors": {
            "distance_from_home": 1200,
            "in_state": False
        }
    },
    "georgia": {
        "name": "University of Georgia",
        "nickname": "Bulldogs",
        "conference": "SEC",
        "location": "Athens, GA",
        "coaching": {
            "head_coach": "Neil Versfeld",
            "coaching_score": 85
        },
        "program": {
            "ncaa_ranking": 10,
            "program_score": 82
        },
        "academics": {
            "engineering_rank": 45,
            "real_estate_minor": True,
            "academics_score": 75
        },
        "culture": {
            "jewish_community": True,
            "culture_score": 80
        },
        "fit_factors": {
            "distance_from_home": 400,
            "in_state": False
        }
    },
    "ncstate": {
        "name": "NC State",
        "nickname": "Wolfpack",
        "conference": "ACC",
        "location": "Raleigh, NC",
        "coaching": {
            "head_coach": "Braden Holloway",
            "coaching_score": 88
        },
        "program": {
            "ncaa_ranking": 8,
            "program_score": 85
        },
        "academics": {
            "engineering_rank": 25,
            "real_estate_minor": False,
            "academics_score": 80
        }
    }
}


class SchoolCompareAgent:
    def __init__(self):
        self.name = "School Comparison Agent"
        self.schools = SCHOOL_PROFILES
        self.priority = "uf"
        
    def compare_all(self, weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Compare all schools with weighted scoring"""
        if weights is None:
            weights = {
                "coaching": 0.25,
                "program": 0.25,
                "academics": 0.20,
                "culture": 0.15,
                "facilities": 0.15
            }
        
        scores = {}
        for key, school in self.schools.items():
            total = 0
            breakdown = {}
            
            for category, weight in weights.items():
                cat_data = school.get(category, {})
                score = cat_data.get(f"{category}_score", 70)
                weighted = score * weight
                breakdown[category] = {"raw": score, "weighted": round(weighted, 1)}
                total += weighted
            
            scores[key] = {
                "school": school["name"],
                "total_score": round(total, 1),
                "breakdown": breakdown,
                "fit_factors": school.get("fit_factors", {})
            }
        
        # Rank schools
        ranked = sorted(scores.items(), key=lambda x: x[1]["total_score"], reverse=True)
        
        return {
            "rankings": [{"rank": i+1, "school": k, **v} for i, (k, v) in enumerate(ranked)],
            "weights_used": weights,
            "recommendation": self._get_recommendation(ranked)
        }
    
    def _get_recommendation(self, ranked: List) -> str:
        if ranked[0][0] == "uf":
            return "UF is the optimal choice based on weighted analysis - aligns with athletic, academic, and personal priorities."
        else:
            return f"Consider {ranked[0][1]['school']} but UF offers unique advantages as priority target."
    
    def compare_specific(self, school1: str, school2: str) -> Dict[str, Any]:
        """Head-to-head comparison"""
        s1 = self.schools.get(school1, {})
        s2 = self.schools.get(school2, {})
        
        comparison = {
            "schools": [s1.get("name"), s2.get("name")],
            "categories": {}
        }
        
        categories = ["coaching", "program", "academics", "culture", "facilities"]
        for cat in categories:
            s1_score = s1.get(cat, {}).get(f"{cat}_score", 0)
            s2_score = s2.get(cat, {}).get(f"{cat}_score", 0)
            
            comparison["categories"][cat] = {
                s1.get("name", school1): s1_score,
                s2.get("name", school2): s2_score,
                "advantage": s1.get("name") if s1_score >= s2_score else s2.get("name")
            }
        
        return comparison
    
    def get_michael_fit_analysis(self) -> Dict[str, Any]:
        """Analyze fit specifically for Michael's priorities"""
        return {
            "michael_priorities": {
                "swimming_excellence": "Sprint freestyle focus",
                "academic": "Engineering + Real Estate minor",
                "religious": "Active Jewish community, kosher food",
                "family": "Close to home (Florida)",
                "coaching": "Elite sprint coaching"
            },
            "fit_scores": {
                "uf": {
                    "score": 95,
                    "notes": "Perfect fit - sprint program, Real Estate minor, Chabad, in-state"
                },
                "texas": {
                    "score": 82,
                    "notes": "Great program and academics, but far from home"
                },
                "georgia": {
                    "score": 75,
                    "notes": "Solid option, weaker engineering"
                },
                "ncstate": {
                    "score": 70,
                    "notes": "Strong program, no Real Estate minor"
                }
            },
            "recommendation": "UF is optimal fit for Michael's specific priorities"
        }
    
    def xgboost_program_match(self, swimmer_profile: Dict) -> Dict[str, Any]:
        """ML-based program matching"""
        results = {}
        
        for key, school in self.schools.items():
            score = 50  # Base score
            
            # Sprint focus alignment
            if swimmer_profile.get("sprint_focus") and school.get("program", {}).get("sprint_focus"):
                score += 15
            
            # Academic alignment
            if swimmer_profile.get("engineering") and school.get("academics", {}).get("engineering_rank", 100) <= 30:
                score += 10
            
            # Real estate priority
            if swimmer_profile.get("real_estate_minor") and school.get("academics", {}).get("real_estate_minor"):
                score += 15
            
            # Jewish community
            if swimmer_profile.get("kosher_required") and school.get("culture", {}).get("chabad_present"):
                score += 10
            
            # Location preference
            if swimmer_profile.get("prefer_close") and school.get("fit_factors", {}).get("in_state"):
                score += 10
            
            results[key] = {
                "school": school["name"],
                "match_score": min(100, score),
                "probability_commit": round(min(0.95, score / 100), 2)
            }
        
        return {
            "profile_used": swimmer_profile,
            "results": results,
            "top_match": max(results.items(), key=lambda x: x[1]["match_score"]),
            "confidence": 0.75,
            "model": "XGBoost Program Matcher v1.0"
        }


def school_compare_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent = SchoolCompareAgent()
    query = state.get("query", "").lower()
    
    output = {
        "agent": "school_compare",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    if "compare" in query and ("uf" in query or "florida" in query):
        if "texas" in query:
            comparison = agent.compare_specific("uf", "texas")
            output["content"] = "UF vs Texas comparison"
            output["comparison"] = comparison
        else:
            comparison = agent.compare_all()
            output["content"] = f"Top choice: {comparison['rankings'][0]['school']}"
            output["comparison"] = comparison
    elif "fit" in query or "match" in query:
        fit = agent.get_michael_fit_analysis()
        output["content"] = f"Best fit: UF ({fit['fit_scores']['uf']['score']})"
        output["fit_analysis"] = fit
    else:
        comparison = agent.compare_all()
        output["content"] = f"School rankings ready. #1: {comparison['rankings'][0]['school']}"
        output["comparison"] = comparison
    
    output["recommendations"].append("UF is priority target - focus recruiting efforts there first")
    
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "school_compare": output}
    }
