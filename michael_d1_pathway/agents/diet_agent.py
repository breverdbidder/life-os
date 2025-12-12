"""
Kosher Meal & Diet Preparation Agent
=====================================
Handles dietary requirements, kosher meal planning, and nutrition.
Based on Michael Andrew Framework (Race Pace Club methodology).

Protocol: Keto Mon-Thu, Moderate Carbs Fri-Sun (Shabbat)
"""

from typing import Dict, Any, List
from datetime import datetime, date
import json


# Michael Andrew Framework Constants
MICHAEL_ANDREW_FRAMEWORK = {
    "philosophy": "Ultra Short Race Pace Training (USRPT)",
    "diet_protocol": "Targeted Ketogenic",
    "meal_timing": "Strategic carb cycling around competition",
    "hydration": "Electrolyte-rich, 1 gallon/day minimum",
    "supplements": ["Creatine", "Beta-Alanine", "Omega-3", "Vitamin D", "Magnesium"]
}

# Kosher Keto Macro Targets
MACRO_TARGETS = {
    "weekday": {  # Mon-Thu: Strict Keto
        "protein_g": 180,
        "fat_g": 150,
        "carbs_g": 30,
        "calories": 2800,
        "protein_per_lb": 1.0  # Per lb body weight
    },
    "shabbat": {  # Fri-Sun: Moderate Carbs
        "protein_g": 180,
        "fat_g": 120,
        "carbs_g": 100,
        "calories": 3000,
        "notes": "Challah, wine, traditional foods allowed"
    },
    "competition": {  # Meet days
        "protein_g": 150,
        "fat_g": 100,
        "carbs_g": 150,
        "calories": 2800,
        "timing": "Carb load 2 hrs pre-race"
    }
}

# Sample Kosher Keto Meals
KOSHER_KETO_MEALS = {
    "breakfast": [
        {
            "name": "Salmon & Eggs",
            "ingredients": ["Smoked salmon (4oz)", "3 eggs scrambled", "Avocado half", "Cream cheese"],
            "macros": {"protein": 45, "fat": 35, "carbs": 4},
            "kosher_notes": "Use kosher salmon, check cream cheese hechsher"
        },
        {
            "name": "Greek Yogurt Bowl",
            "ingredients": ["Full-fat Greek yogurt (1 cup)", "Walnuts", "Chia seeds", "Berries (small portion)"],
            "macros": {"protein": 25, "fat": 20, "carbs": 10},
            "kosher_notes": "Check yogurt hechsher, ensure no gelatin"
        }
    ],
    "lunch": [
        {
            "name": "Grilled Chicken Salad",
            "ingredients": ["Chicken breast (8oz)", "Mixed greens", "Olive oil dressing", "Feta cheese", "Olives"],
            "macros": {"protein": 55, "fat": 30, "carbs": 5},
            "kosher_notes": "Kosher chicken, separate from meat if using cheese"
        },
        {
            "name": "Tuna Avocado Boats",
            "ingredients": ["Tuna (canned in oil, 2 cans)", "Avocado (2 halves)", "Mayo", "Celery"],
            "macros": {"protein": 50, "fat": 40, "carbs": 6},
            "kosher_notes": "Check tuna hechsher"
        }
    ],
    "dinner": [
        {
            "name": "Ribeye Steak & Vegetables",
            "ingredients": ["Ribeye (10oz)", "Broccoli (roasted)", "Asparagus", "Butter"],
            "macros": {"protein": 70, "fat": 50, "carbs": 8},
            "kosher_notes": "Kosher meat, no dairy with meat meal"
        },
        {
            "name": "Baked Salmon & Cauliflower",
            "ingredients": ["Salmon fillet (8oz)", "Cauliflower mash", "Green beans", "Lemon butter sauce"],
            "macros": {"protein": 55, "fat": 35, "carbs": 10},
            "kosher_notes": "Fish meal - can include dairy"
        }
    ],
    "snacks": [
        {"name": "Hard boiled eggs (3)", "macros": {"protein": 18, "fat": 15, "carbs": 1}},
        {"name": "Beef jerky (kosher)", "macros": {"protein": 20, "fat": 5, "carbs": 3}},
        {"name": "Cheese cubes & almonds", "macros": {"protein": 15, "fat": 25, "carbs": 4}},
        {"name": "Celery with almond butter", "macros": {"protein": 8, "fat": 20, "carbs": 6}}
    ]
}


class KosherDietAgent:
    """
    Agent for kosher meal planning using Michael Andrew's framework.
    Optimizes nutrition for competitive swimming performance.
    """
    
    def __init__(self):
        self.name = "Kosher Meal & Diet Preparation Agent"
        self.protocol = "Keto Mon-Thu, Moderate Fri-Sun"
        self.framework = MICHAEL_ANDREW_FRAMEWORK
        
    def get_day_type(self, target_date: date = None) -> str:
        """Determine if day is weekday (keto) or Shabbat (moderate)"""
        if target_date is None:
            target_date = date.today()
        
        day_of_week = target_date.weekday()
        
        # Friday (4), Saturday (5), Sunday (6) = Shabbat/moderate
        if day_of_week >= 4:
            return "shabbat"
        return "weekday"
    
    def get_macro_targets(self, day_type: str = None, is_competition: bool = False) -> Dict[str, Any]:
        """Get macro targets for specified day type"""
        if is_competition:
            return MACRO_TARGETS["competition"]
        
        if day_type is None:
            day_type = self.get_day_type()
            
        return MACRO_TARGETS.get(day_type, MACRO_TARGETS["weekday"])
    
    def generate_meal_plan(self, day_type: str = None) -> Dict[str, Any]:
        """Generate a complete meal plan for the day"""
        if day_type is None:
            day_type = self.get_day_type()
        
        targets = self.get_macro_targets(day_type)
        
        # Select meals
        plan = {
            "day_type": day_type,
            "targets": targets,
            "meals": {
                "breakfast": KOSHER_KETO_MEALS["breakfast"][0],
                "lunch": KOSHER_KETO_MEALS["lunch"][0],
                "dinner": KOSHER_KETO_MEALS["dinner"][0],
                "snacks": KOSHER_KETO_MEALS["snacks"][:2]
            },
            "hydration": {
                "water_oz": 128,
                "electrolytes": "Add sodium/potassium to 2 bottles",
                "timing": "32oz by 10am, 32oz by 2pm, 32oz by 6pm, 32oz by 9pm"
            },
            "supplements": MICHAEL_ANDREW_FRAMEWORK["supplements"],
            "supplement_timing": {
                "morning": ["Vitamin D", "Omega-3"],
                "pre_workout": ["Creatine", "Beta-Alanine"],
                "evening": ["Magnesium"]
            }
        }
        
        # Calculate totals
        total_macros = {"protein": 0, "fat": 0, "carbs": 0}
        for meal_type, meal in plan["meals"].items():
            if isinstance(meal, dict) and "macros" in meal:
                for macro, value in meal["macros"].items():
                    total_macros[macro] += value
            elif isinstance(meal, list):
                for item in meal:
                    for macro, value in item.get("macros", {}).items():
                        total_macros[macro] += value
        
        plan["total_macros"] = total_macros
        plan["compliance"] = self._check_compliance(total_macros, targets)
        
        return plan
    
    def _check_compliance(self, actual: Dict, targets: Dict) -> Dict[str, Any]:
        """Check if meal plan meets macro targets"""
        return {
            "protein": {
                "target": targets["protein_g"],
                "actual": actual["protein"],
                "status": "✅" if actual["protein"] >= targets["protein_g"] * 0.9 else "⚠️"
            },
            "fat": {
                "target": targets["fat_g"],
                "actual": actual["fat"],
                "status": "✅" if actual["fat"] >= targets["fat_g"] * 0.9 else "⚠️"
            },
            "carbs": {
                "target": targets["carbs_g"],
                "actual": actual["carbs"],
                "status": "✅" if actual["carbs"] <= targets["carbs_g"] * 1.1 else "⚠️"
            }
        }
    
    def get_pre_race_nutrition(self, hours_before: int = 2) -> Dict[str, Any]:
        """Get pre-race nutrition recommendations"""
        return {
            "timing": f"{hours_before} hours before race",
            "meal": {
                "name": "Pre-Race Fuel",
                "options": [
                    "White rice (1 cup) with chicken breast (4oz)",
                    "Banana with almond butter",
                    "Energy bar (low fiber)"
                ],
                "macros_target": {"protein": 20, "carbs": 50, "fat": 10}
            },
            "hydration": {
                "water": "16-20 oz",
                "electrolytes": "Yes - sodium/potassium"
            },
            "avoid": [
                "High fiber foods",
                "Heavy fats",
                "New/unfamiliar foods",
                "Excessive protein"
            ],
            "kosher_notes": "Plan ahead for meet-day kosher options"
        }
    
    def xgboost_nutrition_prediction(self, training_load: float, competition_days: int) -> Dict[str, Any]:
        """
        XGBoost-based prediction for optimal nutrition adjustments.
        Returns predicted optimal macro adjustments based on training load.
        """
        # Simplified prediction logic (would be actual XGBoost model in production)
        base_multiplier = 1.0
        
        if training_load > 8:  # High training load
            base_multiplier = 1.15
        elif training_load > 5:
            base_multiplier = 1.0
        else:
            base_multiplier = 0.9
        
        # Adjust for competition proximity
        if competition_days <= 3:
            carb_adjustment = 1.5  # Increase carbs for taper
        else:
            carb_adjustment = 1.0
        
        return {
            "predicted_adjustments": {
                "calorie_multiplier": base_multiplier,
                "protein_multiplier": base_multiplier,
                "carb_adjustment": carb_adjustment,
                "recommendations": [
                    f"Adjust calories by {(base_multiplier-1)*100:.0f}% based on training load",
                    f"Carb intake {'increased' if carb_adjustment > 1 else 'normal'} for competition prep"
                ]
            },
            "confidence": 0.75,
            "model": "XGBoost Nutrition Optimizer v1.0"
        }


def diet_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node function for Diet Agent"""
    agent = KosherDietAgent()
    query = state.get("query", "").lower()
    
    output = {
        "agent": "diet",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    if "meal plan" in query or "what to eat" in query:
        plan = agent.generate_meal_plan()
        output["content"] = f"Today's meal plan ({plan['day_type']}): {json.dumps(plan['meals'], indent=2)}"
        output["meal_plan"] = plan
        output["recommendations"].append(f"Follow {plan['day_type']} protocol - target {plan['targets']['carbs_g']}g carbs")
        
    elif "pre-race" in query or "competition" in query or "meet" in query:
        pre_race = agent.get_pre_race_nutrition()
        output["content"] = f"Pre-race nutrition: {json.dumps(pre_race, indent=2)}"
        output["pre_race"] = pre_race
        output["action_items"].append({
            "task": "Prepare kosher pre-race meal",
            "priority": "high"
        })
        
    elif "macro" in query or "target" in query:
        targets = agent.get_macro_targets()
        output["content"] = f"Daily macro targets: {json.dumps(targets, indent=2)}"
        output["targets"] = targets
        
    else:
        day_type = agent.get_day_type()
        output["content"] = f"Today is {day_type} protocol. Keto Mon-Thu, moderate carbs Fri-Sun."
        output["day_type"] = day_type
    
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "diet": output}
    }


if __name__ == "__main__":
    agent = KosherDietAgent()
    print("Kosher Diet Agent Initialized")
    print(f"Protocol: {agent.protocol}")
    plan = agent.generate_meal_plan()
    print(f"Today's type: {plan['day_type']}")
