"""
Michael Shapira D1 Pathway - Specialized Agents Package

Agents:
- KosherDietAgent: Nutrition planning (keto/Shabbat)
- EducationAgent: NCAA eligibility and academics
- SchoolVisitAgent: D1 visit planning
- ChabadContactsAgent: Jewish resources at target schools
"""

from .kosher_diet_agent import KosherDietAgent
from .education_agent import EducationAgent
from .school_visit_agent import SchoolVisitAgent
from .chabad_contacts_agent import ChabadContactsAgent

__all__ = [
    "KosherDietAgent",
    "EducationAgent", 
    "SchoolVisitAgent",
    "ChabadContactsAgent"
]
