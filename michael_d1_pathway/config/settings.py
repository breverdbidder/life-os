"""
Michael D1 Pathway Configuration
=================================
Central configuration for the multi-agent system.
"""

import os
from datetime import datetime

# System Configuration
CONFIG = {
    "system": {
        "name": "Michael D1 Pathway",
        "version": "1.0.0",
        "author": "Claude Opus 4.5 (AI Architect)",
        "created": "2025-12-12"
    },
    
    # Primary Target
    "primary_target": {
        "school": "University of Florida",
        "class": 2027,
        "coach": "Anthony Nesty",
        "deadline": "2027-08-01"
    },
    
    # Athlete Profile
    "athlete": {
        "name": "Michael Shapira",
        "dob": "2009-07-22",
        "high_school": "Satellite Beach High School",
        "grad_year": 2027,
        "events": ["50 Free", "100 Free", "200 Free", "100 Fly", "100 Back"],
        "academic_focus": "Engineering",
        "minor_priority": "Real Estate",
        "dietary": "Kosher Keto"
    },
    
    # Target Schools (Priority Order)
    "target_schools": [
        {"key": "uf", "name": "University of Florida", "priority": 1},
        {"key": "texas", "name": "University of Texas", "priority": 2},
        {"key": "georgia", "name": "University of Georgia", "priority": 3},
        {"key": "ncstate", "name": "NC State", "priority": 4}
    ],
    
    # Database
    "supabase": {
        "url": os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co"),
        "tables": {
            "swim_times": "michael_swim_times",
            "nutrition": "michael_nutrition",
            "recruiting": "michael_recruiting",
            "goals": "goals",
            "insights": "insights"
        }
    },
    
    # XGBoost Models
    "ml_models": {
        "recruiting_predictor": {
            "version": "1.0.0",
            "features": ["time", "improvement_rate", "roster_need", "class_depth"],
            "target": "recruitment_probability"
        },
        "performance_predictor": {
            "version": "1.0.0",
            "features": ["current_time", "taper_quality", "competition_level"],
            "target": "predicted_time"
        },
        "achievement_predictor": {
            "version": "1.0.0", 
            "features": ["gap_to_target", "months_remaining", "improvement_history"],
            "target": "achievement_probability"
        }
    },
    
    # Agent Configuration
    "agents": {
        "concurrent_max": 5,
        "timeout_seconds": 30,
        "retry_attempts": 3
    }
}


def get_config(key: str = None):
    """Get configuration value"""
    if key is None:
        return CONFIG
    
    parts = key.split(".")
    value = CONFIG
    for part in parts:
        value = value.get(part, {})
    return value
