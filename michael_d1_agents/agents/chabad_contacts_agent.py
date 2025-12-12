"""
Chabad Contacts & School Information Agent
Michael Shapira D1 Pathway - Specialized Agent

Maintains:
- Chabad center contacts at each target school
- Kosher resources in college towns
- Jewish life information
- Shabbat hospitality connections
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, time
from dataclasses import dataclass, field
from enum import Enum


class KosherLevel(Enum):
    STRICT = "strict"  # Under rabbinical supervision
    MODERATE = "moderate"  # Kosher-style
    VEGETARIAN = "vegetarian"  # Safe for kosher observers
    LIMITED = "limited"  # Few options


@dataclass
class ChabadCenter:
    """Chabad center information"""
    name: str
    university: str
    city: str
    state: str
    address: str
    phone: str
    email: str
    website: str
    rabbi_name: str
    rebbetzin_name: str
    
    # Services
    shabbat_dinner_time: str
    shabbat_lunch: bool
    daily_minyan: bool
    kosher_meals_available: str  # "Daily", "Shabbat only", etc.
    student_housing: bool
    
    # Programs
    weekly_programs: List[str] = field(default_factory=list)
    high_holiday_services: bool = True
    
    # Stats
    weekly_attendance: int = 0
    notes: str = ""


@dataclass
class KosherResource:
    """Kosher food resource"""
    name: str
    resource_type: str  # "restaurant", "grocery", "meal_service"
    address: str
    phone: str
    kosher_certification: str  # "OU", "OK", "Star-K", etc.
    hours: str
    delivery: bool
    notes: str = ""


@dataclass
class JewishLife:
    """Jewish life at a university"""
    university: str
    chabad: ChabadCenter
    hillel_present: bool
    kosher_dining_hall: bool
    jewish_student_population: int
    kosher_resources: List[KosherResource] = field(default_factory=list)
    nearest_orthodox_synagogue: str = ""
    mikvah_available: bool = False
    eruv_present: bool = False


class ChabadContactsAgent:
    """
    Specialized agent for Jewish life and Chabad resources at target schools.
    Ensures Michael has religious support during visits and potential enrollment.
    """
    
    def __init__(self):
        self.chabad_centers: Dict[str, ChabadCenter] = {}
        self.kosher_resources: Dict[str, List[KosherResource]] = {}
        self.jewish_life: Dict[str, JewishLife] = {}
        self._load_data()
    
    def _load_data(self):
        """Load Chabad and kosher resource data for target schools"""
        
        # University of Florida - Primary Target
        uf_chabad = ChabadCenter(
            name="Chabad UF - Lubavitch Jewish Student Center",
            university="University of Florida",
            city="Gainesville",
            state="FL",
            address="2021 NW 5th Ave, Gainesville, FL 32603",
            phone="(352) 336-5877",
            email="rabbi@jewishgator.com",
            website="https://www.jewishgator.com",
            rabbi_name="Rabbi Berl Goldman",
            rebbetzin_name="Chani Goldman",
            shabbat_dinner_time="7:30 PM (varies by sunset)",
            shabbat_lunch=True,
            daily_minyan=True,
            kosher_meals_available="Daily lunch + Shabbat",
            student_housing=False,
            weekly_programs=["Torah & Tea Tuesday", "Shabbat 500", "Jewish Learning Institute"],
            weekly_attendance=700,
            notes="One of the largest Chabad on Campus programs. Very active - 700+ weekly."
        )
        self.chabad_centers["UF"] = uf_chabad
        
        # UF Kosher Resources
        uf_kosher = [
            KosherResource(
                name="Chabad UF Daily Lunch",
                resource_type="meal_service",
                address="2021 NW 5th Ave",
                phone="(352) 336-5877",
                kosher_certification="Chabad supervision",
                hours="12:00 PM - 2:00 PM weekdays",
                delivery=False,
                notes="Free kosher lunch for students"
            ),
            KosherResource(
                name="Krishna Lunch",
                resource_type="meal_service",
                address="Plaza of Americas, UF Campus",
                phone="N/A",
                kosher_certification="Vegetarian/Vegan",
                hours="11:00 AM - 1:30 PM weekdays",
                delivery=False,
                notes="Vegetarian - safe for kosher observers"
            ),
            KosherResource(
                name="Publix (Kosher Section)",
                resource_type="grocery",
                address="Multiple Gainesville locations",
                phone="Various",
                kosher_certification="Various products",
                hours="7 AM - 10 PM",
                delivery=True,
                notes="Good kosher section, delivery via Instacart"
            )
        ]
        self.kosher_resources["UF"] = uf_kosher
        
        # Florida State University
        fsu_chabad = ChabadCenter(
            name="Chabad at FSU",
            university="Florida State University",
            city="Tallahassee",
            state="FL",
            address="519 Copeland St, Tallahassee, FL 32304",
            phone="(850) 583-0808",
            email="rabbi@chabadfsu.com",
            website="https://www.chabadfsu.com",
            rabbi_name="Rabbi Schneur Oirechman",
            rebbetzin_name="Chaya Oirechman",
            shabbat_dinner_time="7:00 PM",
            shabbat_lunch=True,
            daily_minyan=False,
            kosher_meals_available="Shabbat + special events",
            student_housing=False,
            weekly_programs=["Shabbat dinner", "Holiday events"],
            weekly_attendance=150,
            notes="Smaller but active community"
        )
        self.chabad_centers["FSU"] = fsu_chabad
        
        # University of Miami
        um_chabad = ChabadCenter(
            name="Chabad at UM",
            university="University of Miami",
            city="Coral Gables",
            state="FL",
            address="1501 Brescia Ave, Coral Gables, FL 33146",
            phone="(305) 935-5333",
            email="info@chabadum.com",
            website="https://www.chabadum.com",
            rabbi_name="Rabbi Mendy Fellig",
            rebbetzin_name="Sashi Fellig",
            shabbat_dinner_time="7:30 PM",
            shabbat_lunch=True,
            daily_minyan=True,
            kosher_meals_available="Daily + Shabbat",
            student_housing=False,
            weekly_programs=["Sinai Scholars", "Shabbat", "Lunch & Learn"],
            weekly_attendance=200,
            notes="Strong program, proximity to Miami kosher restaurants"
        )
        self.chabad_centers["UM"] = um_chabad
        
        # USF
        usf_chabad = ChabadCenter(
            name="Chabad of USF",
            university="University of South Florida",
            city="Tampa",
            state="FL",
            address="13287 Arbor Pointe Dr, Tampa, FL 33617",
            phone="(813) 978-0077",
            email="rabbi@chabadusf.com",
            website="https://www.chabadusf.com",
            rabbi_name="Rabbi Pinny Backman",
            rebbetzin_name="Shternie Backman",
            shabbat_dinner_time="7:00 PM",
            shabbat_lunch=True,
            daily_minyan=False,
            kosher_meals_available="Shabbat",
            student_housing=False,
            weekly_programs=["Shabbat dinner", "JLI courses"],
            weekly_attendance=100,
            notes="Growing community"
        )
        self.chabad_centers["USF"] = usf_chabad
        
        # FAU
        fau_chabad = ChabadCenter(
            name="Chabad at FAU",
            university="Florida Atlantic University",
            city="Boca Raton",
            state="FL",
            address="777 Glades Rd, Boca Raton, FL 33431",
            phone="(561) 962-0770",
            email="rabbi@chabadfau.com",
            website="https://www.chabadfau.com",
            rabbi_name="Rabbi Zalman Bukiet",
            rebbetzin_name="Chana Bukiet",
            shabbat_dinner_time="7:30 PM",
            shabbat_lunch=True,
            daily_minyan=False,
            kosher_meals_available="Shabbat + events",
            student_housing=False,
            weekly_programs=["Shabbat", "Holiday programs"],
            weekly_attendance=80,
            notes="Boca has many kosher options nearby"
        )
        self.chabad_centers["FAU"] = fau_chabad
        
        # Build Jewish Life profiles
        self._build_jewish_life_profiles()
    
    def _build_jewish_life_profiles(self):
        """Build comprehensive Jewish life profiles for each school"""
        
        self.jewish_life["UF"] = JewishLife(
            university="University of Florida",
            chabad=self.chabad_centers["UF"],
            hillel_present=True,
            kosher_dining_hall=False,
            jewish_student_population=6000,
            kosher_resources=self.kosher_resources.get("UF", []),
            nearest_orthodox_synagogue="Congregation B'nai Israel (Conservative/Orthodox minyan)",
            mikvah_available=True,
            eruv_present=False
        )
        
        self.jewish_life["UM"] = JewishLife(
            university="University of Miami",
            chabad=self.chabad_centers["UM"],
            hillel_present=True,
            kosher_dining_hall=True,  # Miami Beach proximity
            jewish_student_population=2500,
            kosher_resources=[],
            nearest_orthodox_synagogue="Multiple in Miami Beach area",
            mikvah_available=True,
            eruv_present=True  # Miami Beach eruv
        )
        
        self.jewish_life["FSU"] = JewishLife(
            university="Florida State University",
            chabad=self.chabad_centers["FSU"],
            hillel_present=True,
            kosher_dining_hall=False,
            jewish_student_population=2000,
            kosher_resources=[],
            nearest_orthodox_synagogue="Chabad FSU",
            mikvah_available=False,
            eruv_present=False
        )
    
    def get_chabad_info(self, school_code: str) -> Optional[ChabadCenter]:
        """Get Chabad center info for a school"""
        return self.chabad_centers.get(school_code.upper())
    
    def get_jewish_life(self, school_code: str) -> Optional[JewishLife]:
        """Get comprehensive Jewish life info for a school"""
        return self.jewish_life.get(school_code.upper())
    
    def get_kosher_resources(self, school_code: str) -> List[KosherResource]:
        """Get kosher resources for a school location"""
        return self.kosher_resources.get(school_code.upper(), [])
    
    def get_shabbat_hospitality(self, school_code: str) -> Dict[str, Any]:
        """Get Shabbat hospitality information"""
        chabad = self.get_chabad_info(school_code)
        if not chabad:
            return {"available": False, "message": "No Chabad info for this school"}
        
        return {
            "available": True,
            "chabad_name": chabad.name,
            "rabbi": chabad.rabbi_name,
            "phone": chabad.phone,
            "email": chabad.email,
            "friday_night": {
                "time": chabad.shabbat_dinner_time,
                "rsvp_required": True,
                "rsvp_contact": chabad.email
            },
            "shabbat_lunch": {
                "available": chabad.shabbat_lunch,
                "time": "12:30 PM" if chabad.shabbat_lunch else "N/A"
            },
            "advice": [
                f"Contact {chabad.rabbi_name} at least 1 week before visit",
                "Mention Michael is a prospective student-athlete",
                "Ask about hosting with a local family for authentic experience",
                "Bring a small gift (wine, challah cover) as hakarat hatov"
            ]
        }
    
    def prepare_visit_jewish_info(self, school_code: str) -> Dict[str, Any]:
        """Prepare comprehensive Jewish info packet for school visit"""
        chabad = self.get_chabad_info(school_code)
        jewish_life = self.get_jewish_life(school_code)
        kosher = self.get_kosher_resources(school_code)
        shabbat = self.get_shabbat_hospitality(school_code)
        
        return {
            "school": school_code,
            "generated_at": datetime.now().isoformat(),
            "chabad": {
                "name": chabad.name if chabad else "Not available",
                "contact": {
                    "rabbi": chabad.rabbi_name if chabad else "",
                    "phone": chabad.phone if chabad else "",
                    "email": chabad.email if chabad else "",
                    "website": chabad.website if chabad else ""
                },
                "services": {
                    "daily_minyan": chabad.daily_minyan if chabad else False,
                    "kosher_meals": chabad.kosher_meals_available if chabad else "",
                    "weekly_programs": chabad.weekly_programs if chabad else []
                }
            },
            "shabbat_hospitality": shabbat,
            "kosher_resources": [
                {
                    "name": r.name,
                    "type": r.resource_type,
                    "address": r.address,
                    "certification": r.kosher_certification,
                    "hours": r.hours
                }
                for r in kosher
            ],
            "jewish_community": {
                "jewish_population": jewish_life.jewish_student_population if jewish_life else "Unknown",
                "hillel": jewish_life.hillel_present if jewish_life else False,
                "mikvah": jewish_life.mikvah_available if jewish_life else False,
                "eruv": jewish_life.eruv_present if jewish_life else False
            },
            "pre_visit_checklist": [
                f"☐ Contact Chabad ({chabad.email if chabad else 'N/A'}) 1 week before",
                "☐ RSVP for Shabbat meals if visiting over Shabbat",
                "☐ Pack kosher snacks for travel",
                "☐ Bring siddurim and kippot",
                "☐ Research local kosher restaurants",
                "☐ Ask about meeting observant student-athletes"
            ]
        }
    
    def rank_schools_by_jewish_life(self) -> List[Dict]:
        """Rank target schools by quality of Jewish life"""
        rankings = []
        
        for code, jewish_life in self.jewish_life.items():
            score = 0
            factors = []
            
            # Scoring factors
            if jewish_life.chabad:
                score += 30
                factors.append("Active Chabad")
                if jewish_life.chabad.daily_minyan:
                    score += 15
                    factors.append("Daily minyan")
                if jewish_life.chabad.weekly_attendance > 200:
                    score += 10
                    factors.append("Large community")
            
            if jewish_life.kosher_dining_hall:
                score += 20
                factors.append("Kosher dining")
            
            if jewish_life.mikvah_available:
                score += 10
                factors.append("Mikvah available")
            
            if jewish_life.eruv_present:
                score += 5
                factors.append("Eruv present")
            
            if jewish_life.jewish_student_population > 3000:
                score += 15
                factors.append("Large Jewish population")
            
            if len(self.kosher_resources.get(code, [])) > 2:
                score += 10
                factors.append("Multiple kosher options")
            
            rankings.append({
                "school": code,
                "university": jewish_life.university,
                "score": score,
                "factors": factors,
                "chabad_contact": jewish_life.chabad.rabbi_name if jewish_life.chabad else "N/A"
            })
        
        return sorted(rankings, key=lambda x: x["score"], reverse=True)
    
    def get_contact_template(self, school_code: str, visit_dates: str) -> str:
        """Generate email template for contacting Chabad before visit"""
        chabad = self.get_chabad_info(school_code)
        if not chabad:
            return "No Chabad contact found for this school."
        
        template = f"""Subject: Prospective Student-Athlete Visit - {visit_dates}

Dear {chabad.rabbi_name},

My name is Ariel Shapira, and my son Michael is a junior at Satellite Beach High School. 
Michael is being recruited for the {chabad.university} swimming team and we are planning 
a campus visit on {visit_dates}.

We are an Orthodox family and would love to connect with the {chabad.name} during our visit.
If our visit falls over Shabbat, we would be honored to join you for Shabbat dinner and 
services.

A bit about Michael:
- Junior at Satellite Beach HS (Class of 2027)
- D1 swimming recruit (50 Free, 100 Free, 100 Fly, 100 Back)
- SAT: 1280, GPA: 3.5
- Keeps kosher and observes Shabbat

We would appreciate any information about:
1. Shabbat hospitality during our visit
2. Kosher food options on/near campus
3. Any Orthodox student-athletes who might connect with Michael
4. Jewish life for student-athletes at {chabad.university}

Thank you for your time, and we look forward to meeting you.

B'vracha,
Ariel Shapira
(321) XXX-XXXX
"""
        return template


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("✡️ Chabad Contacts Agent - Michael Shapira D1 Pathway")
    print("=" * 60)
    
    agent = ChabadContactsAgent()
    
    # Show rankings
    print("\n📊 Schools Ranked by Jewish Life Quality:")
    rankings = agent.rank_schools_by_jewish_life()
    for i, school in enumerate(rankings, 1):
        print(f"\n   {i}. {school['university']} (Score: {school['score']})")
        print(f"      Factors: {', '.join(school['factors'][:3])}")
        print(f"      Rabbi: {school['chabad_contact']}")
    
    # UF Detail
    print("\n\n🐊 UF JEWISH LIFE DETAIL:")
    uf_info = agent.prepare_visit_jewish_info("UF")
    print(f"   Chabad: {uf_info['chabad']['name']}")
    print(f"   Rabbi: {uf_info['chabad']['contact']['rabbi']}")
    print(f"   Phone: {uf_info['chabad']['contact']['phone']}")
    print(f"   Daily Minyan: {'✅' if uf_info['chabad']['services']['daily_minyan'] else '❌'}")
    print(f"   Kosher Meals: {uf_info['chabad']['services']['kosher_meals']}")
    
    print(f"\n   Kosher Resources ({len(uf_info['kosher_resources'])}):")
    for resource in uf_info['kosher_resources']:
        print(f"      • {resource['name']} ({resource['type']})")
    
    print("\n✅ Chabad Contacts Agent initialized")
