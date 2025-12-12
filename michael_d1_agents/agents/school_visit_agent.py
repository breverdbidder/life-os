"""
School Visit Travel Agent
Michael Shapira D1 Pathway - Specialized Agent

Coordinates:
- Official and unofficial visit logistics
- Transportation (driving/flights)
- Accommodations
- Itinerary planning
- Shabbat-compliant scheduling
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json


class VisitType(Enum):
    UNOFFICIAL = "unofficial"  # At athlete's expense
    OFFICIAL = "official"  # School pays (5 allowed in D1)


class TransportMode(Enum):
    DRIVE = "drive"
    FLY = "fly"
    MIXED = "mixed"


@dataclass
class School:
    """D1 swimming program information"""
    name: str
    city: str
    state: str
    conference: str
    swim_coach: str
    coach_email: str
    distance_from_satellite_beach: int  # miles
    has_kosher_dining: bool
    nearest_chabad: str
    program_tier: str  # "P5", "G5", "Mid-Major"


@dataclass
class Flight:
    """Flight information"""
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    booking_url: str = ""


@dataclass
class Hotel:
    """Hotel accommodation"""
    name: str
    address: str
    distance_to_campus: float  # miles
    price_per_night: float
    has_kitchenette: bool  # For kosher prep
    kosher_friendly: bool
    booking_url: str = ""


@dataclass
class VisitItinerary:
    """Complete visit itinerary"""
    school: School
    visit_type: VisitType
    dates: Tuple[date, date]  # Start, end
    transport: TransportMode
    flights: List[Flight] = field(default_factory=list)
    hotel: Optional[Hotel] = None
    schedule: Dict[str, List[Dict]] = field(default_factory=dict)
    total_cost_estimate: float = 0.0
    shabbat_compliant: bool = True
    meal_plan: List[Dict] = field(default_factory=list)


class SchoolVisitAgent:
    """
    Specialized agent for coordinating D1 swimming program visits.
    Handles logistics while respecting Orthodox Shabbat observance.
    """
    
    # Satellite Beach, FL coordinates for distance calculations
    HOME_BASE = {"lat": 28.1761, "lon": -80.5901, "airport": "MLB"}
    
    # Florida D1 Swimming Programs
    TARGET_SCHOOLS = [
        School("University of Florida", "Gainesville", "FL", "SEC", 
               "Anthony Nesty", "nesty@gators.ufl.edu", 180,
               True, "Chabad UF", "P5"),
        School("Florida State University", "Tallahassee", "FL", "ACC",
               "Neal Studd", "nstudd@fsu.edu", 280,
               False, "Chabad FSU", "P5"),
        School("University of Miami", "Coral Gables", "FL", "ACC",
               "Andy Kershaw", "akershaw@miami.edu", 200,
               True, "Chabad UM", "P5"),
        School("University of South Florida", "Tampa", "FL", "AAC",
               "Ira Klein", "iklein@usf.edu", 140,
               False, "Chabad USF", "G5"),
        School("Florida Atlantic University", "Boca Raton", "FL", "AAC",
               "Marck Rauterkus", "mrauterkus@fau.edu", 170,
               True, "Chabad FAU", "G5"),
        School("Florida International University", "Miami", "FL", "CUSA",
               "Randy Horner", "rhorner@fiu.edu", 210,
               True, "Chabad FIU", "Mid-Major"),
    ]
    
    def __init__(self, family_profile: Dict[str, Any]):
        self.family = family_profile
        self.visits_planned: List[VisitItinerary] = []
        self.official_visits_used: int = 0  # Max 5 in D1
        
    def get_school_by_name(self, name: str) -> Optional[School]:
        """Find school by name"""
        for school in self.TARGET_SCHOOLS:
            if name.lower() in school.name.lower():
                return school
        return None
    
    def check_shabbat_conflict(self, start_date: date, end_date: date) -> Dict:
        """Check if dates conflict with Shabbat"""
        conflicts = []
        current = start_date
        
        while current <= end_date:
            # Friday sunset to Saturday sunset
            if current.weekday() == 4:  # Friday
                conflicts.append({
                    "date": str(current),
                    "issue": "Shabbat begins at sunset",
                    "recommendation": "Arrive before sunset or visit Chabad"
                })
            elif current.weekday() == 5:  # Saturday
                conflicts.append({
                    "date": str(current),
                    "issue": "Shabbat - no travel allowed",
                    "recommendation": "Stay local, attend Chabad services"
                })
            current += timedelta(days=1)
        
        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts,
            "shabbat_compliant_alternatives": self._suggest_alternative_dates(start_date, end_date)
        }
    
    def _suggest_alternative_dates(self, original_start: date, original_end: date) -> List[Dict]:
        """Suggest Shabbat-compliant alternative dates"""
        duration = (original_end - original_start).days
        alternatives = []
        
        # Try weeks before and after
        for offset in [-7, 7, -14, 14]:
            new_start = original_start + timedelta(days=offset)
            new_end = new_start + timedelta(days=duration)
            
            # Check if new dates avoid Shabbat
            has_friday = False
            has_saturday = False
            current = new_start
            while current <= new_end:
                if current.weekday() == 4:
                    has_friday = True
                if current.weekday() == 5:
                    has_saturday = True
                current += timedelta(days=1)
            
            if not has_saturday:  # Saturday is the main issue
                alternatives.append({
                    "start": str(new_start),
                    "end": str(new_end),
                    "friday_present": has_friday,
                    "notes": "Arrive before Shabbat Friday" if has_friday else "Fully compliant"
                })
        
        return alternatives[:3]  # Top 3 alternatives
    
    def recommend_transport(self, school: School) -> Dict:
        """Recommend best transport mode based on distance"""
        distance = school.distance_from_satellite_beach
        
        if distance <= 200:
            return {
                "mode": TransportMode.DRIVE,
                "reason": f"Only {distance} miles - easy drive",
                "drive_time_hours": round(distance / 60, 1),  # ~60mph average
                "estimated_cost": round(distance * 0.67 * 2, 2),  # IRS rate round trip
                "recommendation": "Drive - most flexible for kosher food transport"
            }
        elif distance <= 400:
            return {
                "mode": TransportMode.DRIVE,
                "reason": f"{distance} miles - doable drive, check flight prices",
                "drive_time_hours": round(distance / 60, 1),
                "estimated_cost": round(distance * 0.67 * 2, 2),
                "recommendation": "Drive preferred for kosher flexibility, consider flying if time-constrained"
            }
        else:
            return {
                "mode": TransportMode.FLY,
                "reason": f"{distance} miles - flying recommended",
                "recommended_airports": self._get_airport_options(school),
                "recommendation": "Fly and rent car, bring kosher food in cooler"
            }
    
    def _get_airport_options(self, school: School) -> List[Dict]:
        """Get airport options for school"""
        airports = {
            "Gainesville": [{"code": "GNV", "name": "Gainesville Regional", "to_campus": 10}],
            "Tallahassee": [{"code": "TLH", "name": "Tallahassee International", "to_campus": 8}],
            "Miami": [{"code": "MIA", "name": "Miami International", "to_campus": 12}],
            "Coral Gables": [{"code": "MIA", "name": "Miami International", "to_campus": 10}],
            "Tampa": [{"code": "TPA", "name": "Tampa International", "to_campus": 15}],
            "Boca Raton": [{"code": "PBI", "name": "Palm Beach International", "to_campus": 25}],
        }
        return airports.get(school.city, [{"code": "MCO", "name": "Orlando International", "to_campus": 50}])
    
    def create_visit_itinerary(self, school_name: str, 
                                visit_type: VisitType,
                                preferred_dates: Tuple[date, date]) -> VisitItinerary:
        """Create complete visit itinerary"""
        school = self.get_school_by_name(school_name)
        if not school:
            raise ValueError(f"School not found: {school_name}")
        
        start_date, end_date = preferred_dates
        
        # Check Shabbat
        shabbat_check = self.check_shabbat_conflict(start_date, end_date)
        
        # Get transport recommendation
        transport_rec = self.recommend_transport(school)
        
        # Build schedule
        schedule = self._build_visit_schedule(school, start_date, end_date, visit_type)
        
        # Estimate costs
        costs = self._estimate_costs(school, visit_type, transport_rec, 
                                      (end_date - start_date).days + 1)
        
        itinerary = VisitItinerary(
            school=school,
            visit_type=visit_type,
            dates=(start_date, end_date),
            transport=transport_rec["mode"],
            schedule=schedule,
            total_cost_estimate=costs["total"],
            shabbat_compliant=not shabbat_check["has_conflict"],
            meal_plan=self._create_meal_plan(school, start_date, end_date)
        )
        
        self.visits_planned.append(itinerary)
        
        if visit_type == VisitType.OFFICIAL:
            self.official_visits_used += 1
        
        return itinerary
    
    def _build_visit_schedule(self, school: School, start: date, end: date, 
                               visit_type: VisitType) -> Dict[str, List[Dict]]:
        """Build day-by-day visit schedule"""
        schedule = {}
        duration = (end - start).days + 1
        
        for i in range(duration):
            current_date = start + timedelta(days=i)
            date_str = str(current_date)
            day_name = current_date.strftime("%A")
            
            if current_date.weekday() == 5:  # Saturday - Shabbat
                schedule[date_str] = [
                    {"time": "09:00", "activity": "Shabbat services at " + school.nearest_chabad},
                    {"time": "12:30", "activity": "Shabbat lunch at Chabad"},
                    {"time": "14:00", "activity": "Rest / Walk campus"},
                    {"time": "19:00", "activity": "Havdalah"},
                    {"time": "19:30", "activity": "Optional: Evening with team (post-Shabbat)"}
                ]
            elif i == 0:  # First day
                schedule[date_str] = [
                    {"time": "09:00", "activity": f"Depart Satellite Beach"},
                    {"time": "12:00", "activity": f"Arrive {school.city}"},
                    {"time": "13:00", "activity": "Check in to hotel"},
                    {"time": "14:00", "activity": "Campus tour"},
                    {"time": "16:00", "activity": "Watch team practice"},
                    {"time": "18:00", "activity": "Dinner with coaching staff" if visit_type == VisitType.OFFICIAL else "Dinner (own expense)"}
                ]
            elif i == duration - 1:  # Last day
                schedule[date_str] = [
                    {"time": "08:00", "activity": "Breakfast meeting with coaches"},
                    {"time": "10:00", "activity": "Academic support tour"},
                    {"time": "12:00", "activity": "Check out of hotel"},
                    {"time": "12:30", "activity": f"Depart {school.city}"},
                    {"time": "16:00", "activity": "Arrive Satellite Beach"}
                ]
            else:  # Middle days
                schedule[date_str] = [
                    {"time": "07:00", "activity": "Morning practice observation"},
                    {"time": "09:00", "activity": "Breakfast"},
                    {"time": "10:00", "activity": "Class visit / Academic meetings"},
                    {"time": "12:00", "activity": "Lunch with current swimmers"},
                    {"time": "14:00", "activity": "Facilities tour (pool, weight room)"},
                    {"time": "16:00", "activity": "Meeting with coaching staff"},
                    {"time": "18:00", "activity": "Dinner"}
                ]
        
        return schedule
    
    def _estimate_costs(self, school: School, visit_type: VisitType,
                        transport: Dict, nights: int) -> Dict[str, float]:
        """Estimate visit costs"""
        if visit_type == VisitType.OFFICIAL:
            return {
                "transport": 0,
                "hotel": 0,
                "meals": 0,
                "misc": 50,  # Personal expenses
                "total": 50,
                "note": "Official visit - school covers most expenses"
            }
        
        # Unofficial visit costs
        distance = school.distance_from_satellite_beach
        
        if transport["mode"] == TransportMode.DRIVE:
            transport_cost = distance * 0.67 * 2  # IRS rate round trip
        else:
            transport_cost = 400  # Estimated flight + rental
        
        hotel_cost = nights * 150  # Average hotel
        meals_cost = nights * 75  # $75/day for kosher-friendly meals
        
        return {
            "transport": round(transport_cost, 2),
            "hotel": round(hotel_cost, 2),
            "meals": round(meals_cost, 2),
            "misc": 50,
            "total": round(transport_cost + hotel_cost + meals_cost + 50, 2),
            "note": "Unofficial visit - family expense"
        }
    
    def _create_meal_plan(self, school: School, start: date, end: date) -> List[Dict]:
        """Create kosher meal plan for visit"""
        meals = []
        duration = (end - start).days + 1
        
        for i in range(duration):
            current_date = start + timedelta(days=i)
            day_meals = {
                "date": str(current_date),
                "breakfast": "Packed kosher breakfast / Hotel breakfast (eggs, fruit)",
                "lunch": f"Chabad at {school.name}" if school.has_kosher_dining else "Packed kosher lunch",
                "dinner": f"Chabad Shabbat dinner" if current_date.weekday() == 4 else "Kosher restaurant or packed"
            }
            meals.append(day_meals)
        
        return meals
    
    def get_official_visits_remaining(self) -> int:
        """Get remaining official visits (max 5 for D1)"""
        return 5 - self.official_visits_used
    
    def generate_packing_list(self, itinerary: VisitItinerary) -> Dict[str, List[str]]:
        """Generate packing list for visit"""
        base_list = {
            "documents": [
                "Driver's license / ID",
                "School transcript (unofficial)",
                "SAT/ACT score report",
                "Swimming times documentation",
                "Questions for coaches (prepared list)"
            ],
            "swim_gear": [
                "2 competition suits",
                "3 practice suits",
                "Goggles (2 pairs)",
                "Cap",
                "Team apparel"
            ],
            "clothing": [
                "Business casual outfit (meeting with coaches)",
                "Comfortable walking shoes",
                "Athletic wear",
                "Shabbat clothes" if not itinerary.shabbat_compliant else None
            ],
            "kosher_essentials": [
                "Cooler bag",
                "Kosher snacks (protein bars, nuts)",
                "Packed meals (if limited kosher options)",
                "Kiddush cup (if over Shabbat)",
                "Siddur"
            ],
            "electronics": [
                "Phone + charger",
                "Camera (optional)",
                "Laptop (for note-taking)"
            ]
        }
        
        # Remove None values
        base_list["clothing"] = [item for item in base_list["clothing"] if item]
        
        return base_list


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("✈️ School Visit Travel Agent - Michael Shapira D1 Pathway")
    print("=" * 60)
    
    family = {
        "swimmer": "Michael Shapira",
        "parent": "Ariel Shapira",
        "home": "Satellite Beach, FL",
        "observance": "Orthodox"
    }
    
    agent = SchoolVisitAgent(family)
    
    # Show target schools
    print("\n🏊 Target D1 Swimming Programs:")
    for school in agent.TARGET_SCHOOLS[:4]:
        print(f"   • {school.name} ({school.conference}) - {school.distance_from_satellite_beach} mi")
        print(f"     Coach: {school.swim_coach} | Chabad: {school.nearest_chabad}")
    
    # Create sample itinerary for UF
    print("\n📅 Creating UF Visit Itinerary...")
    uf_visit = agent.create_visit_itinerary(
        "University of Florida",
        VisitType.UNOFFICIAL,
        (date(2025, 1, 12), date(2025, 1, 13))  # Sun-Mon
    )
    
    print(f"\n🐊 UF Visit Summary:")
    print(f"   Type: {uf_visit.visit_type.value.title()}")
    print(f"   Dates: {uf_visit.dates[0]} to {uf_visit.dates[1]}")
    print(f"   Transport: {uf_visit.transport.value.upper()}")
    print(f"   Shabbat Compliant: {'✅' if uf_visit.shabbat_compliant else '⚠️ Conflict'}")
    print(f"   Est. Cost: ${uf_visit.total_cost_estimate:.2f}")
    
    print(f"\n📋 Official Visits Remaining: {agent.get_official_visits_remaining()}/5")
    
    print("\n✅ School Visit Travel Agent initialized")
