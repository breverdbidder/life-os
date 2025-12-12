"""
Chabad Contacts & School Information Agent
==========================================
Maintains Chabad contacts and Jewish community info at target schools.
"""

from typing import Dict, Any
from datetime import datetime

CHABAD_CONTACTS = {
    "uf": {
        "name": "Chabad at UF / Lubavitch Jewish Center",
        "rabbi": "Rabbi Berl Goldman",
        "rebbetzin": "Rebbetzin Channie Goldman",
        "address": "2021 NW 5th Ave, Gainesville, FL 32603",
        "phone": "(352) 336-5877",
        "website": "https://jewishgator.com",
        "email": "rabbi@jewishgator.com",
        "services": [
            "Weekly Shabbat dinners (200+ students)",
            "Daily minyan",
            "Kosher meals available",
            "High Holiday services",
            "Jewish student housing",
            "Israel trips"
        ],
        "distance_from_pool": "1.2 miles from O'Connell Center",
        "notes": "Very active Jewish community. Accommodating for athletes."
    },
    "texas": {
        "name": "Chabad at UT Austin",
        "rabbi": "Rabbi Zev Johnson",
        "address": "2101 Nueces St, Austin, TX 78705",
        "phone": "(512) 478-8899",
        "website": "https://chabadut.org",
        "services": ["Shabbat dinners", "Kosher food", "High Holidays"],
        "notes": "Growing Jewish community"
    },
    "georgia": {
        "name": "Chabad at UGA",
        "rabbi": "Rabbi Michoel Refson",
        "address": "749 Baxter St, Athens, GA 30605",
        "phone": "(706) 543-2973",
        "website": "https://chabaduga.com",
        "services": ["Shabbat dinners", "Kosher options", "Jewish life"],
        "notes": "Active Chabad presence"
    },
    "ncstate": {
        "name": "Chabad at NC State",
        "rabbi": "Rabbi Pinchas Herman",
        "address": "Raleigh, NC",
        "phone": "(919) 637-3738",
        "services": ["Shabbat", "Kosher food"]
    }
}


class ChabadAgent:
    def __init__(self):
        self.name = "Chabad Contacts & School Information Agent"
        self.contacts = CHABAD_CONTACTS
        
    def get_chabad_info(self, school_key: str) -> Dict[str, Any]:
        return self.contacts.get(school_key, {})
    
    def get_all_contacts(self) -> Dict[str, Any]:
        return self.contacts
    
    def evaluate_jewish_life(self, school_key: str) -> Dict[str, Any]:
        chabad = self.contacts.get(school_key, {})
        services = chabad.get("services", [])
        
        score = len(services) * 15  # Base score on services
        if "Kosher meals" in str(services) or "kosher" in str(services).lower():
            score += 20
        if "housing" in str(services).lower():
            score += 15
            
        return {
            "school": school_key,
            "jewish_life_score": min(100, score),
            "kosher_available": "kosher" in str(services).lower(),
            "shabbat_community": "shabbat" in str(services).lower(),
            "contact_info": chabad
        }


def chabad_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent = ChabadAgent()
    query = state.get("query", "").lower()
    
    output = {
        "agent": "chabad",
        "timestamp": datetime.now().isoformat(),
        "content": "",
        "recommendations": [],
        "action_items": []
    }
    
    if "uf" in query or "florida" in query:
        info = agent.get_chabad_info("uf")
        output["content"] = f"UF Chabad: {info['name']} - Rabbi {info['rabbi']}"
        output["chabad_info"] = info
        output["recommendations"].append("Contact Chabad before campus visit for meal arrangements")
    else:
        output["content"] = "Chabad contacts available for all target schools"
        output["all_contacts"] = agent.get_all_contacts()
    
    return {
        "agent_outputs": {**state.get("agent_outputs", {}), "chabad": output}
    }
